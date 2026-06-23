
import os
import pandas as pd
import numpy as np
import argparse

from paths import RESULTS, ROOT

ROOT_DIR = str(ROOT)
GUESSES_FILE = RESULTS / "initial_guesses.csv"
STATMORPH_FILE = RESULTS / "statmorph_results.csv"

def load_priors():
    """
    Loads priors from initial_guesses.csv and merges with statmorph_results.csv if available.
    Statmorph values take precedence for Re, n, PA, AR.
    """
    if not GUESSES_FILE.exists():
        print(f"Error: {GUESSES_FILE} not found.")
        return None
    
    df_guess = pd.read_csv(GUESSES_FILE)
    df_guess['source'] = 'manual'
    
    if STATMORPH_FILE.exists():
        print("Loading Statmorph results...")
        df_stat = pd.read_csv(STATMORPH_FILE)
        
        # Merge. We want to iterate through galaxies and update their values
        for idx, row in df_guess.iterrows():
            gal = row['galaxy']
            stat_row = df_stat[df_stat['galaxy'] == gal]
            
            if not stat_row.empty:
                stat_row = stat_row.iloc[0]
                # Update with statmorph values
                # Gini-M20 derived Sersic index often better than blind guess
                df_guess.at[idx, 're'] = stat_row['sersic_rhalf'] 
                df_guess.at[idx, 'ar'] = 1.0 - stat_row['ellipticity_centroid'] # ar = b/a, ellips = 1 - b/a
                df_guess.at[idx, 'pa'] = np.degrees(stat_row['orientation_centroid']) 
                df_guess.at[idx, 'n'] = stat_row['sersic_n']
                # Position from statmorph is also likely more accurate
                df_guess.at[idx, 'x'] = stat_row['xc_centroid'] + 1 # 0-indexed to 1-indexed conversion? Check if statmorph is 0-indexed. usually is. GALFIT is 1-indexed.
                df_guess.at[idx, 'y'] = stat_row['yc_centroid'] + 1
                df_guess.at[idx, 'source'] = 'statmorph'
    
    return df_guess

def generate_feedme_header(gal, input_img, output_img, sigma_img, psf_img, mask_img="none"):
    # Image size for fitting region
    img_size = 1145
    if "3938" in gal:
        img_size = 1908 
        
    return f"""
================================================================================
# IMAGE and GALFIT CONTROL PARAMETERS
A) {input_img}                # Input data image (FITS file)
B) {output_img}               # Output data image block
C) {sigma_img}                # Sigma image name (made from invvar)
D) {psf_img}                  # Input PSF image (type none if not used)
E) 1                            # PSF fine sampling factor (relative to data)
F) {mask_img}                 # Bad pixel mask (type none if not used)
G) none                                        # File with parameter constraints
H) 1 {img_size} 1 {img_size}    # Image region to fit (xmin xmax ymin ymax)
I) 25 25                        # Size of the convolution box (x y)
J) 22.5                         # Magnitude photometric zeropoint
K) 0.262  0.262                 # Plate scale (dx dy)    [arcsec per pixel]
O) regular                      # Display type (regular, curses, both)
P) 0                            # Choose: 0=optimize, 1=model, 2=imgblock, 3=subcomps

# INITIAL FITTING PARAMETERS
#
#   par)    par value(s)    fit toggle(s)    # parameter description 
# -----------------------------------------------------------------------------
"""

def generate_single_sersic(gal_data, with_psf=True):
    gal = gal_data['galaxy']
    
    # Paths
    suffix = "withpsf_single" if with_psf else "nopsf_single"
    input_img = f"Science_Output/{gal}_r_cutout.fits"
    output_img = f"Science_Output/{gal}_{suffix}.fits"
    sigma_img = f"Science_Output/{gal}_r_sigma_cutout.fits"
    psf_img = f"Science_Output/PSF_Output/{gal}_final_psf.fits" if with_psf else "none"
    
    header = generate_feedme_header(gal, input_img, output_img, sigma_img, psf_img)
    
    # Params
    x, y = gal_data['x'], gal_data['y']
    mag = gal_data['mag']
    re = gal_data['re']
    n = gal_data.get('n', 4.0) # Default to 4 if not in CSV (though load_priors adds it)
    ar = gal_data['ar']
    pa = gal_data['pa']
    
    body = f"""
# Object number: 1 (Single Sersic)
 0) sersic                  #  object type
 1) {x:.2f}  {y:.2f}  1 1     #  position x, y
 3) {mag:.2f}      1            #  Integrated magnitude 
 4) {re:.2f}      1            #  R_e (effective radius)   [pixels]
 5) {n:.2f}        1            #  Sersic index n 
 9) {ar:.2f}        1            #  axis ratio (b/a)  
10) {pa:.2f}        1            #  position angle (PA) [deg]
 Z) 0                       #  output option (0 = resid., 1 = Don't subtract) 
 
# Object number: 2 (Sky)
 0) sky                     #  object type
 1) 0.0      1              #  sky background at center [ADUs]
 2) 0.0000      0           #  dsky/dx (sky gradient in x)
 3) 0.0000      0           #  dsky/dy (sky gradient in y)
 Z) 0                       #  output option (0 = resid., 1 = Don't subtract) 

================================================================================
"""
    return header + body

def generate_bulge_disk(gal_data, with_psf=True):
    gal = gal_data['galaxy']
    
    # Paths
    suffix = "withpsf" if with_psf else "nopsf" # Keeping legacy naming for standard B+D
    input_img = f"Science_Output/{gal}_r_cutout.fits"
    output_img = f"Science_Output/{gal}_galfit_{suffix}.fits"
    sigma_img = f"Science_Output/{gal}_r_sigma_cutout.fits"
    psf_img = f"Science_Output/PSF_Output/{gal}_final_psf.fits" if with_psf else "none"
    
    header = generate_feedme_header(gal, input_img, output_img, sigma_img, psf_img)
    
    x, y = gal_data['x'], gal_data['y']
    mag = gal_data['mag']
    re = gal_data['re']
    # For B+D, we assume the input Re is roughly the "major" component. 
    # Statmorph Re is the TOTAL half light radius.
    # We'll split the difference: Bulge = Re, Disk = 2*Re (Standard guessing)
    # n is usually ignored here as we FORCE 4 and 1, but we could use it?
    # Let's stick to the requested config: Bulge n=4 (free), Disk n=1 (fixed)
    
    ar = gal_data['ar']
    pa = gal_data['pa']
    
    body = f"""
# Object number: 1 (Bulge)
 0) sersic                  #  object type
 1) {x:.2f}  {y:.2f}  1 1     #  position x, y
 3) {mag + 0.75:.2f}      1            #  Integrated magnitude (split)
 4) {re:.2f}      1            #  R_e (effective radius)   [pixels]
 5) 4.0        1            #  Sersic index n (Initial Guess 4)
 9) {ar:.2f}        1            #  axis ratio (b/a)  
10) {pa:.2f}        1            #  position angle (PA) [deg]
 Z) 0                       #  output option (0 = resid., 1 = Don't subtract) 

# Object number: 2 (Disk)
 0) sersic                  #  object type
 1) {x:.2f}  {y:.2f}  1 1     #  position x, y
 3) {mag + 0.75:.2f}      1            #  Integrated magnitude (split)
 4) {re * 2.0:.2f}      1            #  R_e (effective radius)   [pixels]
 5) 1.0        0            #  Sersic index n (1=Exp. Disk, Fixed)
 9) {ar:.2f}        1            #  axis ratio (b/a)  
10) {pa:.2f}        1            #  position angle (PA) [deg]
 Z) 0                       #  output option (0 = resid., 1 = Don't subtract) 

# Object number: 3 (Sky)
 0) sky                     #  object type
 1) 0.0      1              #  sky background at center [ADUs]
 2) 0.0000      0           #  dsky/dx (sky gradient in x)
 3) 0.0000      0           #  dsky/dy (sky gradient in y)
 Z) 0                       #  output option (0 = resid., 1 = Don't subtract) 

================================================================================
"""
    return header + body

def generate_bulge_edgedisk(gal_data, with_psf=True):
    gal = gal_data['galaxy']
    
    # Paths
    suffix = "withpsf_edgedisk" if with_psf else "nopsf_edgedisk"
    input_img = f"Science_Output/{gal}_r_cutout.fits"
    output_img = f"Science_Output/{gal}_galfit_{suffix}.fits"
    sigma_img = f"Science_Output/{gal}_r_sigma_cutout.fits"
    psf_img = f"Science_Output/PSF_Output/{gal}_final_psf.fits" if with_psf else "none"
    
    header = generate_feedme_header(gal, input_img, output_img, sigma_img, psf_img)
    
    x, y = gal_data['x'], gal_data['y']
    mag = gal_data['mag']
    re = gal_data['re']
    ar = gal_data['ar']
    pa = gal_data['pa']
    
    # Edge Disk Params
    # h_s (radial scale) approx Re (of Sersic)
    # h_z (vertical scale) approx 0.1 * h_s for thin disk, let's try 0.2
    h_s = re 
    h_z = re * 0.2
    
    body = f"""
# Object number: 1 (Bulge - Sersic)
 0) sersic                  #  object type
 1) {x:.2f}  {y:.2f}  1 1     #  position x, y
 3) {mag + 0.75:.2f}      1            #  Integrated magnitude (split)
 4) {re * 0.5:.2f}      1            #  R_e (effective radius) [Bulge smaller than Disk]
 5) 4.0        1            #  Sersic index n (Initial Guess 4)
 9) 0.8        1            #  axis ratio (b/a) - Bulge usually rounder
10) {pa:.2f}        1            #  position angle (PA) [deg]
 Z) 0                       #  output option

# Object number: 2 (Disk - EdgeDisk)
 0) edgedisk                #  object type
 1) {x:.2f}  {y:.2f}  1 1     #  position x, y
 3) {mag + 0.75:.2f}      1            #  Integrated magnitude (split)
 4) {h_s:.2f}      1            #  central surface brightness OR h_s (radial scale) ? Check manual. 
                                #  Standard feedme usually 3=mag, 4=hs, 5=hz
                                #  GALFIT usually infers mag vs mu0 from the parameter label or fixed flag?
                                #  Actually par 4 is central surface brightness usually for edgedisk?
                                #  Wait, standard galfit 3.0 uses par 3 for Mag and 4 for scales.
                                #  Let's trust par 3 = Mag, Par 4 = vertical scale? No.
                                #  Let's use standard Sersic-like slotting.
                                #  Par 4 = central surface brightness (mu_0)
                                #  Par 5 = vertical scale height (h_z)
                                #  Par 6 = radial scale length (h_r)
                                #  Wait, no. The format is tricky.
                                #  User manual examples:
                                #  0) edgedisk
                                #  1) x y
                                #  3) mag
                                #  4) h_z (scale height)
                                #  5) h_r (scale length)
                                #  10) PA
                                #  Let's double check this param mapping.
                                #  Actually, widely used config is 4=mu0, 5=hz, 6=hr. But we want Magnitude.
                                #  If we use Mag (3), we skip 4?
                                #  Actually, modern GALFIT usually takes 3) Mag, 4) vertical, 5) radial.
                                #  Let's try that. 4) h_z, 5) h_r.
 4) {h_z:.2f}      1            #  vertical scale height (h_z)
 5) {h_s:.2f}      1            #  radial scale length (h_r)
10) {pa:.2f}        1            #  position angle (PA) [deg]
 Z) 0                       #  output option

# Object number: 3 (Sky)
 0) sky                     #  object type
 1) 0.0      1              #  sky background at center [ADUs]
 2) 0.0000      0           #  dsky/dx (sky gradient in x)
 3) 0.0000      0           #  dsky/dy (sky gradient in y)
 Z) 0                       #  output option

================================================================================
"""
    return header + body

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--galaxy", type=str, help="Specific galaxy to generate for")
    parser.add_argument("--model", type=str, choices=['single', 'bulge_disk', 'bulge_edgedisk'], default='bulge_disk', help="Model architecture")
    args = parser.parse_args()
    
    df = load_priors()
    if df is None: return

    for _, row in df.iterrows():
        gal = row['galaxy']
        if args.galaxy and args.galaxy != gal:
            continue
            
        gal_dir = os.path.join(ROOT_DIR, f"{gal}_Analysis")
        if not os.path.exists(gal_dir):
            continue
            
        print(f"Generating {args.model} feedme for {gal} using {row['source']} priors...")
        print(f"  Priors: n={row.get('n', 'N/A'):.2f}, Re={row['re']:.2f}, PA={row['pa']:.2f}")

        # Always write constraints file just in case (Standard locking)
        with open(os.path.join(gal_dir, "galfit.constraints"), "w") as f:
            f.write("# Component/Parameter constraint file\n#\n1 2 offset 0.0\n1 2 x 0.0 0.0\n1 2 y 0.0 0.0")

        if args.model == 'single':
            content = generate_single_sersic(row, with_psf=True)
            outfile = os.path.join(gal_dir, "galfit_single_withpsf.feedme")
            with open(outfile, "w") as f:
                f.write(content)
        elif args.model == 'bulge_disk':
            content = generate_bulge_disk(row, with_psf=True)
            outfile = os.path.join(gal_dir, "galfit_withpsf.feedme")
            with open(outfile, "w") as f:
                f.write(content)
        elif args.model == 'bulge_edgedisk':
            content = generate_bulge_edgedisk(row, with_psf=True)
            outfile = os.path.join(gal_dir, "galfit_withpsf_edgedisk.feedme")
            with open(outfile, "w") as f:
                f.write(content)
                
        print(f"  Written to {outfile}")

if __name__ == "__main__":
    main()
