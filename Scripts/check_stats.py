import os
from astropy.io import fits
import numpy as np

def check_gal(gal):
    path = fr'c:\Users\lenovo\Desktop\FRB-capstone\NGC_{gal}_Analysis\Science_Output\PSF_Output\NGC_{gal}_final_psf.fits'
    if os.path.exists(path):
        d = fits.getdata(path)
        print(f"{gal}: Min={np.min(d):.6f} Max={np.max(d):.6f} Mean={np.mean(d):.6f} Std={np.std(d):.6f}")
    else:
        print(f"{gal}: Not found")

check_gal('3245')
check_gal('4623')
check_gal('5846')
