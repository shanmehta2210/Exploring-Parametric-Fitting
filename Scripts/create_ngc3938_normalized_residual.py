
from astropy.io import fits
import numpy as np
import os

# Paths
base_dir = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_3938_Analysis\Science_Output"
galfit_path = os.path.join(base_dir, "NGC_3938_galfit_nopsf.fits")
sigma_path = os.path.join(base_dir, "NGC_3938_r_sigma_cutout.fits")
output_path = os.path.join(base_dir, "NGC_3938_norm_resid.fits")

print(f"Loading GALFIT output: {galfit_path}")
print(f"Loading Sigma map: {sigma_path}")

try:
    # GALFIT Output: Ext 1=Input, 2=Model, 3=Residual (Standard)
    # The user mentioned index 2, which matches astropy index 2 if 0-based for specific file types or 3 if 1-based. 
    # Usually GALFIT puts Residual in the last extension (3 if input/model/resid exist).
    # Let's inspect headers if needed, but standard assumes Ext 3 for full block.
    # However, let's open and find the residual extension dynamically or assume Ext 3.
    
    with fits.open(galfit_path) as hdul_galfit:
        # Check extensions
        print("GALFIT Extensions:")
        for i, hdu in enumerate(hdul_galfit):
            print(f"  {i}: {hdu.name}")
            
        # Usually Ext 3 is Residual
        # If user said [2] in a 0-indexed context, that's Model. If 1-indexed, that's Model.
        # But "residual" is usually the 3rd image.
        # Let's assume standard GALFIT: 1=Input, 2=Model, 3=Residual.
        # We will use Ext 3.
        
        resid_data = hdul_galfit[3].data
        header = hdul_galfit[3].header

    with fits.open(sigma_path) as hdul_sigma:
        sigma_data = hdul_sigma[0].data

    if resid_data.shape != sigma_data.shape:
        print(f"Shape mismatch! Resid: {resid_data.shape}, Sigma: {sigma_data.shape}")
        # Try cropping/padding if needed, usually they should match if cutout used.
        # If sigma is full path, might be issue.
        # Assuming they match since they are from same pipeline.
    
    print("Computing Normalized Residual (Resid / Sigma)...")
    # Avoid div by zero
    norm_resid = np.divide(resid_data, sigma_data, out=np.zeros_like(resid_data), where=sigma_data!=0)

    print(f"Saving to {output_path}")
    fits.writeto(output_path, norm_resid, header, overwrite=True)
    print("Done.")

except Exception as e:
    print(f"Error: {e}")
