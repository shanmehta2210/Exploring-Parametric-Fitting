import astropy.io.fits as fits
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
import numpy as np
import os

# Paths
BASE_DIR = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_4378_Analysis\Science_Output"
FILE_WITH_PSF = os.path.join(BASE_DIR, "NGC_4378_galfit_withpsf.fits")
FILE_NO_PSF = os.path.join(BASE_DIR, "NGC_4378_galfit_nopsf.fits")
OUT_DIR = r"c:\Users\lenovo\Desktop\FRB-capstone\Google_Drive_Data_Package\Report_Images"

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def save_plot(data, name, scale='log', vmin=None, vmax=None):
    plt.figure(figsize=(10, 10))
    
    # Handle scaling
    if scale == 'log':
        # Simple LogNorm requires positive values.
        # For data/model, usually > 0.
        # Add small offset just in case? Or clip.
        if vmin is None: vmin = np.percentile(data[data > 0], 1)
        if vmax is None: vmax = np.percentile(data[data > 0], 99.5)
        norm = LogNorm(vmin=vmin, vmax=vmax)
        cmap = 'gray'
    elif scale == 'residual':
        # Residuals can be negative. Use SymLogNorm or linear zscale
        # Log min-max for residuals is tricky if symmetric.
        # User asked for "log min-max", implying dynamic range.
        # Let's use SymLogNorm centered on 0
        norm = SymLogNorm(linthresh=0.01, linscale=1, vmin=-0.1, vmax=0.1)
        cmap = 'RdBu_r' # Diverging map
        
    plt.imshow(data, origin='lower', norm=norm, cmap=cmap)
    plt.axis('off')
    plt.tight_layout(pad=0)
    out_path = os.path.join(OUT_DIR, f"{name}.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved {out_path}")

try:
    # Load With PSF (Extensions: 1=Input, 2=Model, 3=Resid)
    hdul_psf = fits.open(FILE_WITH_PSF)
    data_input = hdul_psf[1].data
    model_psf = hdul_psf[2].data
    resid_psf = hdul_psf[3].data # GALFIT output residual is typically (Data-Model)/Sigma or Data-Model. 
    # Actually GALFIT standard is Data - Model, but if optimized, Ext 3 is Residual.
    # Let's verify headers? Usually Ext 3.
    
    # Load No PSF
    hdul_nopsf = fits.open(FILE_NO_PSF)
    model_nopsf = hdul_nopsf[2].data
    resid_nopsf = hdul_nopsf[3].data
    
    # 1. Fitting Image (Data) - Common to both
    save_plot(data_input, "1_NGC4378_Data", scale='log')
    
    # 2. Models
    # Use same vmin/vmax for direct comparison
    d_min = np.percentile(data_input[data_input > 0], 1)
    d_max = np.percentile(data_input[data_input > 0], 99.5)
    
    save_plot(model_psf, "2_NGC4378_Model_WithPSF", scale='log', vmin=d_min, vmax=d_max)
    save_plot(model_nopsf, "3_NGC4378_Model_NoPSF", scale='log', vmin=d_min, vmax=d_max)
    
    # 3. Residuals
    # Residuals for report usually look best with min/max +/- 5 sigma or so.
    # User said "log min-max scaling", likely meaning Log stretch for the residuals too?
    # Residuals have negative values, so standard Log doesn't work. SymLog does.
    # Or maybe they just meant "scale it well".
    # I will stick to SymLogNorm which is standard for high-dynamic-range residuals.
    save_plot(resid_psf, "4_NGC4378_Residual_WithPSF", scale='residual')
    save_plot(resid_nopsf, "5_NGC4378_Residual_NoPSF", scale='residual')

    hdul_psf.close()
    hdul_nopsf.close()

except Exception as e:
    print(f"Error: {e}")
