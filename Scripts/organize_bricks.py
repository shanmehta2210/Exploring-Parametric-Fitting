
import os
import sys
import shutil
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u

from paths import ROOT

BASE_DIR = str(ROOT)
BRICK_FILES = [f for f in os.listdir(BASE_DIR) if f.startswith('legacysurvey-') and f.endswith('-image-r.fits.fz')]

# Define the targets and their coordinates (from the catalog)
# Note: I am copying the coordinates from previous steps to ensure accuracy.
TARGETS = {
    "NGC_5846": SkyCoord("15h06m29.3s", "+01d36m20s", frame="icrs"),
    "NGC_5576": SkyCoord("14h21m14.2s", "+03d15m17s", frame="icrs"),
    "NGC_4623": SkyCoord("12h42m20.9s", "+07d39m28s", frame="icrs"),
    "NGC_3245": SkyCoord("10h27m18.2s", "+28d30m28s", frame="icrs"),
    "NGC_4762": SkyCoord("12h52m55.8s", "+11d13m54s", frame="icrs"),
    "NGC_4378": SkyCoord("12h25m18.1s", "+04d55m31s", frame="icrs"),
    "NGC_4814": SkyCoord("12h55m32.1s", "+58d19m44s", frame="icrs"),
    "NGC_3938": SkyCoord("11h52m49.4s", "+44d07m15s", frame="icrs"),
}

def find_containing_brick(target_coord):
    """
    Checks all brick files to see if the target coordinate falls within them.
    Returns: List of matching brick filenames.
    """
    matches = []
    
    for brick in BRICK_FILES:
        brick_path = os.path.join(BASE_DIR, brick)
        try:
            # Open header to get WCS
            # Usually extension 1 has the image data and WCS for compressed fits
            with fits.open(brick_path) as hdul:
                header = hdul[1].header
                wcs = WCS(header)
                
                # Check footprints
                # Fast way: check if world_to_pixel results in x,y within image bounds
                # 3600 x 3600 is standard brick size usually, but we check header
                naxis1 = header['NAXIS1']
                naxis2 = header['NAXIS2']
                
                x, y = wcs.world_to_pixel(target_coord)
                
                if 0 <= x < naxis1 and 0 <= y < naxis2:
                    matches.append(brick)
                    
        except Exception as e:
            print(f"Error checking {brick}: {e}")
            
    return matches

def organize_files():
    print("--- Starting Organization ---")
    
    # Track which file belongs to which galaxy to avoid moving issues if one brick covers two (unlikely here but good practice)
    file_mapping = {}

    for name, coord in TARGETS.items():
        print(f"Checking {name}...", end=" ")
        matches = find_containing_brick(coord)
        
        if not matches:
            print("NO MATCH found in current directory!")
        else:
            print(f"Found in: {matches}")
            # Prepare directory
            target_dir = os.path.join(BASE_DIR, f"{name}_Analysis")
            os.makedirs(target_dir, exist_ok=True)
            
            for brick_img in matches:
                # Calculate the paired invvar file
                brick_inv = brick_img.replace("image-r", "invvar-r")
                
                # Move/Copy logic
                # We move files. If a file is needed by multiple, we handle that manually (unlikely for this list)
                src_img = os.path.join(BASE_DIR, brick_img)
                dst_img = os.path.join(target_dir, brick_img)
                
                src_inv = os.path.join(BASE_DIR, brick_inv)
                dst_inv = os.path.join(target_dir, brick_inv)
                
                if os.path.exists(src_img):
                    shutil.move(src_img, dst_img)
                    print(f"   Moved {brick_img} -> {name}_Analysis/")
                else:
                    print(f"   Warning: {brick_img} already moved or missing?")
                    
                if os.path.exists(src_inv):
                    shutil.move(src_inv, dst_inv)
                    print(f"   Moved {brick_inv} -> {name}_Analysis/")
                else:
                    print(f"   Warning: {brick_inv} already moved or missing?")

if __name__ == "__main__":
    organize_files()
