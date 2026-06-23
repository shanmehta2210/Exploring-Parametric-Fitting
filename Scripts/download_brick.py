
import os
import requests

# URL pattern for Legacy Survey DR9 South (likely, based on previous files)
# If this fails, we might try 'north' or different DRs.
# Example: https://portal.nersc.gov/cfs/cosmo/data/legacysurvey/dr9/south/coadd/215/2153p032/legacysurvey-2153p032-image-r.fits.fz

BASE_URL = "https://portal.nersc.gov/cfs/cosmo/data/legacysurvey/dr9/south/coadd"
BRICK_NAME = "2153p032"
# The folder structure is usually first 3 digits of RA / brickname
RA_PREFIX = "215" 

FILES_TO_GET = [
    f"legacysurvey-{BRICK_NAME}-image-r.fits.fz",
    f"legacysurvey-{BRICK_NAME}-invvar-r.fits.fz"
]

OUTPUT_DIR = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_5576_Analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_file(filename):
    url = f"{BASE_URL}/{RA_PREFIX}/{BRICK_NAME}/{filename}"
    local_path = os.path.join(OUTPUT_DIR, filename)
    
    print(f"Downloading {url}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print(f"Saved to {local_path}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    for f in FILES_TO_GET:
        download_file(f)
