
import os
import numpy as np
from astropy.io import fits

from paths import GALAXIES, ROOT, galaxy_science

BASE_DIR = str(ROOT)
PSF_SIZE = 25

def extract_psf(galaxy):
    psf_dir = galaxy_science(galaxy) / "PSF_Output"
    proto_path = psf_dir / f"{galaxy}_proto_{galaxy}.fits"
    out_path = psf_dir / f"{galaxy}_final_psf.fits"

    if not proto_path.exists():
        print(f"Skipping {galaxy}: Proto file not found ({proto_path}).")
        return

    print(f"Extracting Mean PSF for {galaxy}...")
    try:
        with fits.open(proto_path) as hdul:
            data = hdul[0].data
            
            final_psf = None
            
            # Case A: 3D Cube (N, 25, 25)
            if data.ndim == 3:
                final_psf = data[0, :, :]
                
            # Case B: 2D Mosaic (25, N*25)
            elif data.ndim == 2:
                h, w = data.shape
                # Assuming standard side-by-side mosaic
                if h == PSF_SIZE:
                    final_psf = data[:, 0:PSF_SIZE]
                else:
                    # Fallback (e.g. if single star and shape is 25x25)
                    if h == PSF_SIZE and w == PSF_SIZE:
                        final_psf = data
                    else:
                        print(f"  Warning: Unexpected shape {data.shape}. Taking top-left 25x25.")
                        final_psf = data[0:PSF_SIZE, 0:PSF_SIZE]
            
            if final_psf is not None:
                # Normalize
                total_flux = np.sum(final_psf)
                if total_flux > 0:
                    final_psf /= total_flux
                
                # Save
                hdu = fits.PrimaryHDU(final_psf)
                hdu.writeto(out_path, overwrite=True)
                print(f"  Saved: {out_path}")
                
    except Exception as e:
        print(f"  Error extracting PSF for {galaxy}: {e}")

if __name__ == "__main__":
    # User can uncomment specific galaxies or run all
    # For now, running all to update any that are ready
    for g in GALAXIES:
        extract_psf(g)
