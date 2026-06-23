from astropy.io import fits
import numpy as np
import sys
import os

def find_neighbors(catalog_path, center_x, center_y, search_radius=500):
    try:
        # LDAC catalogs often have data in the second HDU (index 2 usually, 1 is info)
        # But sometimes it's 1. Let's try 2 first as per standard LDAC.
        hdul = fits.open(catalog_path)
        
        # Find the table extension
        data = None
        for hdu in hdul:
            if hdu.header.get('EXTNAME') == 'LDAC_OBJECTS':
                data = hdu.data
                break
        
        if data is None:
            # Fallback for simple FITS tables
            data = hdul[1].data

        # Extract columns
        x = data['X_IMAGE']
        y = data['Y_IMAGE']
        mag = data['MAG_AUTO']
        
        # Calculate distance from center
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Filter
        mask = dist < search_radius
        
        # Sort by magnitude (brightest first)
        indices = np.argsort(mag[mask])
        
        print(f"--- Brightest Objects within {search_radius}px of ({center_x}, {center_y}) ---")
        print(f"{'ID':<5} {'X':<10} {'Y':<10} {'Mag':<10} {'Dist':<10}")
        
        # Print top 10
        filtered_x = x[mask][indices]
        filtered_y = y[mask][indices]
        filtered_mag = mag[mask][indices]
        filtered_dist = dist[mask][indices]
        
        for i in range(min(10, len(filtered_x))):
            print(f"{i+1:<5} {filtered_x[i]:<10.2f} {filtered_y[i]:<10.2f} {filtered_mag[i]:<10.2f} {filtered_dist[i]:<10.2f}")
            
    except Exception as e:
        print(f"Error reading catalog: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_neighbors.py <catalog_path> [center_x] [center_y]")
    else:
        cat_file = sys.argv[1]
        cx = float(sys.argv[2]) if len(sys.argv) > 2 else 571.5 # Default to typical center
        cy = float(sys.argv[3]) if len(sys.argv) > 3 else 571.5
        radius = float(sys.argv[4]) if len(sys.argv) > 4 else 500
        find_neighbors(cat_file, cx, cy, radius)
