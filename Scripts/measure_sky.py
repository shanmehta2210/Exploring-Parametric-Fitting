from astropy.io import fits
import numpy as np
import sys

def measure_sky_corners(fits_path, box_size=50):
    try:
        hdul = fits.open(fits_path)
        data = hdul[0].data if len(hdul) > 0 else None # Usually primary extension
        
        # If data is in ext 1 (compressed etc)
        if data is None and len(hdul) > 1:
            data = hdul[1].data
            
        if data is None:
            print("Error: Could not find image data.")
            return

        h, w = data.shape
        
        # Extract corners
        c1 = data[0:box_size, 0:box_size]
        c2 = data[0:box_size, w-box_size:w]
        c3 = data[h-box_size:h, 0:box_size]
        c4 = data[h-box_size:h, w-box_size:w]
        
        # Combine
        corners = np.concatenate((c1.flatten(), c2.flatten(), c3.flatten(), c4.flatten()))
        
        # Sigma clip just in case
        mean = np.mean(corners)
        std = np.std(corners)
        
        clean_mask = (np.abs(corners - mean) < 3 * std)
        clean_corners = corners[clean_mask]
        
        final_sky = np.median(clean_corners)
        final_std = np.std(clean_corners)
        
        print(f"Image Dimensions: {w}x{h}")
        print(f"Corner Stats (Box Size {box_size}):")
        print(f"  Mean: {np.mean(clean_corners):.5f}")
        print(f"  Median: {final_sky:.5f}")
        print(f"  StdDev: {final_std:.5f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python measure_sky.py <fits_path>")
    else:
        measure_sky_corners(sys.argv[1])
