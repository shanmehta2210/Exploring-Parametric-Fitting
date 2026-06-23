
import os
import numpy as np
from astropy.io import fits

# Configuration
GALAXY = "NGC_5846"
BASE_DIR = r"c:\Users\lenovo\Desktop\FRB-capstone"
PSF_DIR = os.path.join(BASE_DIR, f"{GALAXY}_Analysis", "Science_Output", "PSF_Output")

# Input: The PROTO file (Contains Basis Vectors)
# The first extension (or first slice of primary) is the Mean PSF.
proto_path = os.path.join(PSF_DIR, f"{GALAXY}_proto_{GALAXY}.fits")
out_path = os.path.join(PSF_DIR, f"{GALAXY}_final_psf.fits")

print(f"Extracting Mean PSF for {GALAXY}...")

try:
    with fits.open(proto_path) as hdul:
        # Proto file structure for BASIS_TYPE PIXEL:
        # Usually a 3D cube (Component, Y, X) or a 2D mosaic.
        # In the user's image, it looked like a mosaic line side-by-side.
        # Let's inspect shape.
        data = hdul[0].data
        header = hdul[0].header
        
        print(f"Proto Shape: {data.shape}")
        
        # PSF_SIZE is 25x25.
        psf_size = 25
        
        final_psf = None
        
        # Case A: 3D Cube (N, 25, 25)
        if data.ndim == 3:
            print("Detected 3D Cube. Extracting index 0 (Mean PSF).")
            final_psf = data[0, :, :]
            
        # Case B: 2D Mosaic (25, N*25) - Side by side
        elif data.ndim == 2:
            h, w = data.shape
            print(f"Detected 2D Mosaic ({h}x{w}).")
            # Assuming the first square is the mean.
            # PSFEx places them side-by-side.
            # Check if height is 25.
            if h == psf_size:
                print("Height matches PSF_SIZE. Extracting first patch.")
                final_psf = data[:, 0:psf_size]
            else:
                # Warning: Weird shape.
                print(f"Warning: Unexpected height {h}. Attempting center crop or first patch.")
                final_psf = data[0:psf_size, 0:psf_size]
        
        if final_psf is not None:
            # Normalize (Sum = 1) - Good practice for GALFIT/Conuvoltions
            total_flux = np.sum(final_psf)
            if total_flux > 0:
                final_psf /= total_flux
                print(f"Normalized PSF (Sum was {total_flux:.4f}).")
            
            # Save
            hdu = fits.PrimaryHDU(final_psf)
            # Copy minimal header info if needed
            hdu.writeto(out_path, overwrite=True)
            print(f"Saved: {out_path}")
            
except Exception as e:
    print(f"Error extracting PSF: {e}")
