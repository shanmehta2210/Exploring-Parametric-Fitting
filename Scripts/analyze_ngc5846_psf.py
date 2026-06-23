
import os
import numpy as np
from astropy.io import fits, votable
from astropy.table import Table
import matplotlib.pyplot as plt

# Paths
base_dir = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_5846_Analysis\Science_Output\PSF_Output"
xml_path = os.path.join(base_dir, "NGC_5846_psfex.xml")
samp_path = os.path.join(base_dir, "NGC_5846_samp_NGC_5846.fits")
resi_path = os.path.join(base_dir, "NGC_5846_resi_NGC_5846.fits")
cat_path = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_5846_Analysis\Science_Output\NGC_5846.ldac"

print(f"--- Analyzing PSFEx Output for NGC 5846 ---\n")

# 1. XML Analysis (Star Counts)
try:
    # Parsing XML manually or via votable if it's votable-like, but PSFEx XML is specific.
    # We'll just read the file as text and search for keys for simplicity/robustness without heavy XML parsers if structure is simple
    # actually votable parse might fail if it's not VOTable. PSFEx XML is usually VOTable. Let's try astropy.
    try:
        vo = votable.parse(xml_path)
        tab = vo.get_first_table().to_table()
        # Usually contains fields like 'NStars_Accepted'
        # But PSFEx XML structure can be nested.
        # Let's simple-parse text to be safe.
        with open(xml_path, 'r') as f:
            content = f.read()
            if "NStars_Accepted" in content:
                # crude extraction
                import re
                accepted = re.search(r'<PARAM name="Accepted_Stellar_Side" value="(\d+)"', content)
                # Actually PSFEx usually has <PARAM name="NStars_Accepted" value="123" ...
                # Let's print what we find.
                pass
    except Exception as e:
        print(f"Simple XML parse note: {e}")

    # Fallback: Read text
    with open(xml_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "NStars_Accepted" in line:
                print(f"XML Stat: {line.strip()}")
            if "NStars_Total" in line:
                print(f"XML Stat: {line.strip()}")
            if "Chi2" in line and "dof" not in line: # avoid checking params defs
                print(f"XML Stat: {line.strip()}")
except Exception as e:
    print(f"Failed to read XML: {e}")


# 2. Analyze Catalog (S/N Distribution)
try:
    tbl = Table.read(cat_path, hdu=2)
    # Calculate S/N
    # SExtractor FLUX_AUTO / FLUXERR_AUTO
    flux = tbl['FLUX_AUTO']
    fluxerr = tbl['FLUXERR_AUTO']
    snr = flux / fluxerr
    
    # Filter for stars (rough approximation to see what's available)
    # Using CLASS_STAR for visualization
    stars = tbl[tbl['CLASS_STAR'] > 0.8]
    stars_snr = stars['FLUX_AUTO'] / stars['FLUXERR_AUTO']
    
    print(f"\nCatalog Analysis:")
    print(f"Total Sources: {len(tbl)}")
    print(f"Sources with CLASS_STAR > 0.8: {len(stars)}")
    print(f"  - Median S/N of these stars: {np.nanmedian(stars_snr):.2f}")
    print(f"  - 90th Percentile S/N: {np.nanpercentile(stars_snr, 90):.2f}")
    print(f"  - 10th Percentile S/N: {np.nanpercentile(stars_snr, 10):.2f}")
    
    # Suggest S/N cut
    high_snr_stars = stars[stars_snr > 50]
    print(f"  - High Quality Stars (S/N > 50): {len(high_snr_stars)}")
    
except Exception as e:
    print(f"Error reading catalog: {e}")

# 3. Analyze FITS Samples and Residuals
try:
    samp_hdul = fits.open(samp_path)
    resi_hdul = fits.open(resi_path)
    
    # Usually extension 1 has the vignettes
    # They are in a table column called 'VIGNET' usually?
    # Or PSFEx output checkimages are datacubes? 
    # checkimage_type SAMPLES produces a FITS cube or a large image.
    # Usually it's a large image mosaic.
    
    samp_data = samp_hdul[0].data
    resi_data = resi_hdul[0].data
    
    if samp_data is None:
        print("\nWarning: Primary HDU of Sample/Resid is empty. Checking extensions...")
        # Inspect structure
        print(samp_hdul.info())
    else:
        print(f"\nShape of Sample Image: {samp_data.shape}")
        
        # Calculate global residual statistics
        # We want to see if residuals are noise-like or structured.
        mean_res = np.mean(resi_data)
        std_res = np.std(resi_data)
        max_res = np.max(resi_data)
        min_res = np.min(resi_data)
        
        print(f"\nResidual Analysis:")
        print(f"  - Mean Residual: {mean_res:.4f}")
        print(f"  - StdDev Residual: {std_res:.4f}")
        print(f"  - Peak Residual: {max_res:.4f} (Pos), {min_res:.4f} (Neg)")
        
        # Compare to Peak Flux in Samples (roughly)
        peak_flux = np.max(samp_data)
        print(f"  - Peak Flux in Samples: {peak_flux:.4f}")
        print(f"  - Fractional Max Residual: {max_res/peak_flux*100:.2f}% (Target < 5%)")

except Exception as e:
    print(f"Error analyzing FITS images: {e}")
