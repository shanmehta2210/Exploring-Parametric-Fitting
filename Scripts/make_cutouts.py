
import os
import glob
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
import astropy.units as u
from reproject import reproject_interp
from reproject.mosaicking import find_optimal_celestial_wcs, reproject_and_coadd

from paths import ROOT

# --- CONFIGURATION ---
BASE_DIR = str(ROOT)
CUTOUT_SIZE = (300 * u.arcsec, 300 * u.arcsec)  # Size of the final cutout
PIXEL_SCALE = 0.262 * u.arcsec / u.pixel  # Standard DECaLS pixel scale

# Target List (Same as Catalog)
TARGETS = {
    "NGC_5846": SkyCoord("15h06m29.3s", "+01d36m20s", frame="icrs"),
    "NGC_5576": SkyCoord(215.2652283 * u.deg, 3.27099224 * u.deg, frame="icrs"),
    "NGC_4623": SkyCoord(190.54446979 * u.deg, 7.67703249 * u.deg, frame="icrs"),
    "NGC_3245": SkyCoord("10h27m18.2s", "+28d30m28s", frame="icrs"),
    "NGC_4762": SkyCoord(193.23312311 * u.deg, 11.23105323 * u.deg, frame="icrs"),
    "NGC_4378": SkyCoord("12h25m18.1s", "+04d55m31s", frame="icrs"),
    "NGC_4814": SkyCoord(193.84111557 * u.deg, 58.3441749 * u.deg, frame="icrs"),
    "NGC_3938": SkyCoord(178.20589703 * u.deg, 44.1207948 * u.deg, frame="icrs"),
}

def process_galaxy(name, target_coord, size=CUTOUT_SIZE):
    print(f"\n=== Processing {name} ===")
    
    # Define Input/Output Paths
    work_dir = os.path.join(BASE_DIR, f"{name}_Analysis")
    if not os.path.exists(work_dir):
        print(f"Skipping: Directory {work_dir} not found.")
        return

    # Find all brick files (image and invvar)
    # Find all brick files (image and invvar)
    image_files = glob.glob(os.path.join(work_dir, "Input_Bricks", "legacysurvey-*-image-r.fits.fz"))
    invvar_files = glob.glob(os.path.join(work_dir, "Input_Bricks", "legacysurvey-*-invvar-r.fits.fz"))
    
    if len(image_files) == 0:
        print(f"Error: No image files found in {work_dir}")
        return

    print(f"Found {len(image_files)} bricks.")
    
    # ---------------------------------------------------------
    # 1. LOAD DATA & WCS
    # ---------------------------------------------------------
    files_img = []
    files_inv = []
    hdus_img = []
    hdus_inv = []
    
    try:
        # Open all files
        for img_f in image_files:
            f = fits.open(img_f)
            files_img.append(f)
            hdus_img.append(f[1]) # Extension 1

        # Match invvars
        for img_f in image_files:
            # Construct invvar filename robustly
            # Assumes img_f is ".../legacysurvey-XXXX-image-r.fits.fz"
            dirname = os.path.dirname(img_f)
            basename = os.path.basename(img_f)
            inv_base = basename.replace("image-r", "invvar-r")
            inv_f = os.path.join(dirname, inv_base)
            
            if os.path.exists(inv_f):
                f = fits.open(inv_f)
                files_inv.append(f)
                hdus_inv.append(f[1])
            else:
                print(f"Warning: Missing invvar file: {inv_f}")
                print("Strict mode: Aborting.")
                return

        # ---------------------------------------------------------
        # 2. DEFINE OUTPUT WCS
        # ---------------------------------------------------------
        # If single brick, just use its WCS. If multiple, build an optimal one.
        if len(image_files) == 1:
            wcs_out = WCS(hdus_img[0].header)
            data_img = hdus_img[0].data
            data_inv = hdus_inv[0].data
        else:
            print("Mosaic mode activated: Stitching bricks...")
            
            # Define WCS for the *Cutout*
            
            # Calculate pixels needed
            npix = int(size[0] / (PIXEL_SCALE * u.pixel)) # approx 763 px
            
            center_pix = npix / 2.0
            
            wcs_cutout = WCS(naxis=2)
            wcs_cutout.wcs.crpix = [center_pix, center_pix]
            wcs_cutout.wcs.crval = [target_coord.ra.deg, target_coord.dec.deg]
            wcs_cutout.wcs.cdelt = [-0.262/3600.0, 0.262/3600.0] # Standard DECaLS scale
            wcs_cutout.wcs.ctype = ["RA---TAN", "DEC--TAN"]

            shape_out = (npix, npix)
            
            print(f"Reprojecting to centered cutout ({npix}x{npix})...")
            
            # Reproject Images
            data_img, footprint_img = reproject_and_coadd(
                hdus_img, wcs_cutout, shape_out=shape_out, reproject_function=reproject_interp
            )
            
            # Reproject InvVars
            data_inv, footprint_inv = reproject_and_coadd(
                hdus_inv, wcs_cutout, shape_out=shape_out, reproject_function=reproject_interp
            )
            
            final_cutout_img = data_img
            final_cutout_inv = data_inv
            final_wcs = wcs_cutout
            
            hdr_cut = final_wcs.to_header()

        # ---------------------------------------------------------
        # 3. CUTOUT (If Single Brick)
        # ---------------------------------------------------------
        if len(image_files) == 1:
            # Standard Cutout2D with PARTIAL handling
            # mode='partial' ensures we get the full size (e.g. 763x763) even if it hits the edge.
            # It fills the empty space with fill_value.  
            try:
                cutout_img_obj = Cutout2D(data_img, position=target_coord, size=CUTOUT_SIZE, wcs=wcs_out, mode='partial', fill_value=0)
                cutout_inv_obj = Cutout2D(data_inv, position=target_coord, size=CUTOUT_SIZE, wcs=wcs_out, mode='partial', fill_value=0)
                
                final_cutout_img = cutout_img_obj.data
                final_cutout_inv = cutout_inv_obj.data
                hdr_cut = cutout_img_obj.wcs.to_header()
            except Exception as e:
                print(f"Error during Cutout2D: {e}")
                return
        
        # ---------------------------------------------------------
        # 4. SIGMA MAP GENERATION
        # ---------------------------------------------------------
        print("Generating Sigma Map...")
        
        sigma = np.full(final_cutout_inv.shape, 1e9, dtype=float) # Default high sigma
        
        # Avoid NaNs in invvar
        final_cutout_inv = np.nan_to_num(final_cutout_inv, nan=0.0)
        
        mask = final_cutout_inv > 0
        sigma[mask] = 1.0 / np.sqrt(final_cutout_inv[mask])
        
        # ---------------------------------------------------------
        # 5. SAVE
        # ---------------------------------------------------------
        out_dir = os.path.join(work_dir, "Science_Output")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_img_name = os.path.join(out_dir, f"{name}_r_cutout.fits")
        out_sig_name = os.path.join(out_dir, f"{name}_r_sigma_cutout.fits")
        
        fits.PrimaryHDU(data=final_cutout_img, header=hdr_cut).writeto(out_img_name, overwrite=True)
        fits.PrimaryHDU(data=sigma, header=hdr_cut).writeto(out_sig_name, overwrite=True)
        
        print(f"Saved: {out_img_name}")
        print(f"Saved: {out_sig_name}")
        
    finally:
        # Cleanup open handles
        for f in files_img: f.close()
        for f in files_inv: f.close()

if __name__ == "__main__":
    for name, coord in TARGETS.items():
        if name == "NGC_3938":
             process_galaxy(name, coord, size=(500 * u.arcsec, 500 * u.arcsec))
        else:
             process_galaxy(name, coord)
