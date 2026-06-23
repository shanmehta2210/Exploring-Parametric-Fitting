from astropy.io import fits
import pandas as pd
import os

ROOT_DIR = r"c:\Users\lenovo\Desktop\FRB-capstone"
GALAXIES = ["NGC_5576", "NGC_5846"]

def get_bright_neighbors(galaxy):
    sci_dir = os.path.join(f"{galaxy}_Analysis", "Science_Output")
    if not os.path.exists(sci_dir):
        print(f"Directory not found: {sci_dir}")
        return
    
    ldacs = [f for f in os.listdir(sci_dir) if f.endswith(".ldac") and not "check" in f.lower()]
    if not ldacs:
        print(f"No LDAC found in {sci_dir}")
        return
    
    catalog_path = os.path.join(sci_dir, ldacs[0])
    print(f"Found catalog: {catalog_path}")
    
    with fits.open(catalog_path) as hdul:
        hdul.info()
        # Find which HDU has the data (search for LDAC_OBJECTS or just data)
        data_hdu = None
        for hdu in hdul:
            if hdu.data is not None:
                data_hdu = hdu
        
        if data_hdu is None:
            print("No data found in any HDU")
            return
            
        data = data_hdu.data
        
        # Build DataFrame manually to handle array columns
        needed_cols = ['X_IMAGE', 'Y_IMAGE', 'MAG_AUTO', 'FLUX_RADIUS', 'A_IMAGE', 'B_IMAGE', 'THETA_IMAGE']
        results = {}
        for col in needed_cols:
            if col in data.names:
                val = data[col]
                if col == 'FLUX_RADIUS' and len(val.shape) > 1:
                    results[col] = val[:, 0] # Take first flux radius
                else:
                    results[col] = val
        
        df = pd.DataFrame(results)
        
    # Sort by magnitude (brightest first)
    # Filter out the main galaxy (usually near center 573, 573)
    main_x, main_y = 573, 573
    df['dist_to_center'] = ((df['X_IMAGE'] - main_x)**2 + (df['Y_IMAGE'] - main_y)**2)**0.5
    
    # Prominent neighbors are bright but not the central object
    # Let's say dist > 50 pixels to avoid the main galaxy's nucleus components
    neighbors = df[df['dist_to_center'] > 50].sort_values(by='MAG_AUTO').head(5)
    
    print(f"\n--- Top 5 Bright Neighbors for {galaxy} ---")
    print(neighbors)
    return neighbors

if __name__ == "__main__":
    for gal in GALAXIES:
        get_bright_neighbors(gal)
