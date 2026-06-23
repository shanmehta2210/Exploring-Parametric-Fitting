import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import LogStretch, ImageNormalize, MinMaxInterval

# Galaxy IDs
galaxies = ['3245', '3938', '4378', '4623', '4762', '4814', '5576', '5846']
root_dir = r'c:\Users\lenovo\Desktop\FRB-capstone'

def process_galaxy(gal_id):
    input_path = os.path.join(root_dir, f'NGC_{gal_id}_Analysis', 'Science_Output', 'PSF_Output', f'NGC_{gal_id}_final_psf.fits')
    
    # Example: ngc_3245_final_psf.png
    output_filename = f'ngc_{gal_id}_final_psf.png'
    output_path = os.path.join(root_dir, output_filename)

    if not os.path.exists(input_path):
        print(f"Skipping {gal_id}: File not found at {input_path}")
        return

    try:
        # Read FITS
        with fits.open(input_path) as hdul:
            data = hdul[0].data

        # Reverting to MinMaxInterval as requested.
        norm = ImageNormalize(data, interval=MinMaxInterval(), stretch=LogStretch())

        # Plot and save
        plt.figure(figsize=(6, 6))
        plt.imshow(data, origin='lower', cmap='gray', norm=norm)
        plt.axis('off')
        
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=150)
        plt.close()
        print(f"Saved {output_filename}")

    except Exception as e:
        print(f"Error processing {gal_id}: {e}")

if __name__ == "__main__":
    for gal in galaxies:
        process_galaxy(gal)
