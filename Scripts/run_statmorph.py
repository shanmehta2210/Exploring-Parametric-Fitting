
import os
import glob
import numpy as np
import pandas as pd
from astropy.io import fits
import statmorph
from statmorph.utils.image_diagnostics import make_figure
import matplotlib.pyplot as plt
from astropy.wcs import WCS
import warnings

# Suppress annoying warnings
warnings.filterwarnings('ignore')

from paths import GALAXIES, RESULTS, ROOT, galaxy_dir

ROOT_DIR = str(ROOT)
RESULTS_FILE = RESULTS / "statmorph_results.csv"

def process_galaxy(gal_name, analysis_dir):
    print(f"Processing {gal_name}...")
    
    # Define paths
    science_path = os.path.join(analysis_dir, "Science_Output", f"{gal_name}_r_cutout.fits")
    sigma_path = os.path.join(analysis_dir, "Science_Output", f"{gal_name}_r_sigma_cutout.fits")
    psf_path = os.path.join(analysis_dir, "Science_Output", "PSF_Output", f"{gal_name}_final_psf.fits")
    segmap_path = os.path.join(analysis_dir, "Science_Output", "segmentation.fits")
    
    # Check files exist
    for p in [science_path, sigma_path, psf_path, segmap_path]:
        if not os.path.exists(p):
            print(f"  Missing file: {p}")
            return None

    # Load data
    with fits.open(science_path) as hdul:
        image = hdul[0].data
        header = hdul[0].header
        
    with fits.open(sigma_path) as hdul:
        weight = hdul[0].data
        # Statmorph expects weight/sigma map. SExtractor weight map (MAP_RMS) is usually sigma.
        # But my pipeline generates 1/sqrt(invvar) which IS sigma.
        # Just ensure no Infs or NaNs.
        weight = np.nan_to_num(weight, nan=1e9, posinf=1e9)
        
    with fits.open(psf_path) as hdul:
        psf = hdul[0].data
        
    with fits.open(segmap_path) as hdul:
        segmap = hdul[0].data
        
    # --- COMPANION HANDLING STRATEGY ---
    # For NGC 5576 (ID 1 in segmap usually) and 5846, the segmap handles deblending
    # provided SExtractor did its job. We need to identify WHICH label corresponds to the
    # target galaxy.
    # Heuristic: The target galaxy is always at the center of the cutout.
    # Find the label at the center pixel.
    
    cy, cx = image.shape
    cy, cx = cy // 2, cx // 2
    target_label = segmap[cy, cx]
    
    if target_label == 0:
        print(f"  Warning: Center pixel ({cx}, {cy}) is background (label 0). Finding nearest object.")
        # Search a small box around center
        box = 10
        sl = (slice(cy-box, cy+box), slice(cx-box, cx+box))
        center_crop = segmap[sl]
        labels, counts = np.unique(center_crop[center_crop > 0], return_counts=True)
        if len(labels) == 0:
            print("  Error: No object found near center.")
            return None
        target_label = labels[np.argmax(counts)] # Take the dominant label in center
        print(f"  Found nearest object label: {target_label}")
    else:
        print(f"  Target Label: {target_label}")

    # Create mask: statmorph fits ONE source. We mask everything that provides light
    # but isn't the target source (label != target_label) and is not background (label != 0).
    # Actually statmorph uses the segmap to define the source. It handles 'other sources' 
    # by ignoring them if the mask is passed correctly?
    # Statmorph documentation says: "segmap: ... where the label of the source of interest is 'label'."
    # It masks other sources automatically if they are in the segmap.
    
    # Run statmorph
    # Direct instantiation to avoid wrapper issues
    try:
        morph = statmorph.SourceMorphology(
            image, segmap, label=target_label, weightmap=weight, psf=psf, n_sigma_outlier=10
        )
    except Exception as e:
        print(f"  Statmorph failed: {e}")
        return None
    
    # Extract metrics
    results = {
        'galaxy': gal_name,
        'gini': morph.gini,
        'm20': morph.m20,
        'concentration': morph.concentration,
        'asymmetry': morph.asymmetry,
        'smoothness': morph.smoothness,
        'rpetro_circ': morph.rpetro_circ,
        'rpetro_ellip': morph.rpetro_ellip,
        'rhalf_circ': morph.rhalf_circ,
        'rhalf_ellip': morph.rhalf_ellip,
        'sersic_n': morph.sersic_n,
        'sersic_rhalf': morph.sersic_rhalf,
        'xc_centroid': morph.xc_centroid,
        'yc_centroid': morph.yc_centroid,
        'ellipticity_centroid': morph.ellipticity_centroid,
        'orientation_centroid': morph.orientation_centroid, # radians
        'flag': morph.flag,
        'flag_sersic': morph.flag_sersic
    }
    
    print(f"  Done. G={morph.gini:.3f}, M20={morph.m20:.3f}, C={morph.concentration:.3f}")
    
    # Save Diagnostic Plot
    try:
        fig = make_figure(morph)
        plot_path = os.path.join(analysis_dir, "Science_Output", f"{gal_name}_statmorph_diagnostic.png")
        fig.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved diagnostic plot to {plot_path}")
    except Exception as e:
        print(f"  Warning: Failed to save diagnostic plot: {e}")
        
    return results

def main():
    all_results = []

    for gal_name in GALAXIES:
        adir = galaxy_dir(gal_name)
        if not adir.exists():
            continue
        res = process_galaxy(gal_name, str(adir))
        if res:
            all_results.append(res)
            
    if all_results:
        df = pd.DataFrame(all_results)
        RESULTS.mkdir(parents=True, exist_ok=True)
        df.to_csv(RESULTS_FILE, index=False)
        print(f"\nSaved results to {RESULTS_FILE}")
        
        # Also print a quick summary to stdout
        print("\n--- Summary ---")
        print(df[['galaxy', 'gini', 'm20', 'concentration', 'asymmetry', 'sersic_n']])
    else:
        print("No results generated.")

if __name__ == "__main__":
    main()
