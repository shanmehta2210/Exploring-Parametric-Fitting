from astropy.io import fits
import numpy as np
import os

# Paths
base_dir = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_3938_Analysis\Science_Output"
seg_path = os.path.join(base_dir, "segmentation.fits")
mask_path = os.path.join(base_dir, "NGC_3938_mask.fits")

print(f"Loading Segmentation Map: {seg_path}")

try:
    with fits.open(seg_path) as hdul:
        # Assuming segmentation map is in the primary extension or first extension
        seg_data = hdul[0].data
        header = hdul[0].header
        
        # Check if data is loaded
        if seg_data is None:
             print("Data is None in Ext 0, checking Ext 1...")
             seg_data = hdul[1].data
             header = hdul[1].header

    print(f"Shape: {seg_data.shape}")
    cy, cx = seg_data.shape[0] // 2, seg_data.shape[1] // 2
    
    # Identify Galaxy ID at the center
    # Being safe: check a small box around center in case center pixel is 0 (unlikely for main galaxy)
    center_region = seg_data[cy-5:cy+5, cx-5:cx+5]
    gal_id = np.median(center_region[center_region > 0])
    
    # If median fails (empty), take the max or just center pixel
    if np.isnan(gal_id):
        gal_id = seg_data[cy, cx]

    gal_id = int(gal_id)
    print(f"Identified Galaxy ID at center: {gal_id}")
    
    if gal_id == 0:
        print("Error: Center ID is 0 (Background). Cannot identify galaxy.")
    else:
        # Create Mask: 
        # Goal: Galaxy = 0 (Good), Rest = 1 (Bad)
        # This allows fitting ONLY the galaxy.
        
        mask = np.ones_like(seg_data, dtype=np.int16) # Initialize all as 1 (Bad)
        mask[seg_data == gal_id] = 0 # Set Galaxy pixels to 0 (Good)
        
        print(f"Creating mask with Galaxy ID {gal_id} set to 0 (Good) and others to 1 (Bad).")
        print(f"Saving to {mask_path}")
        
        fits.writeto(mask_path, mask, header, overwrite=True)
        print("Done.")

except Exception as e:
    print(f"Error: {e}")
