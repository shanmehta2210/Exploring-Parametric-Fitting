import os
import subprocess

from paths import CONFIG, GALAXIES, galaxy_dir, galaxy_science, wsl_path

CONFIG_FILE = wsl_path(CONFIG / "psfex" / "default.psfex")

def run_wsl_command(cmd):
    """Run a command in WSL via subprocess."""
    wsl_cmd = f'wsl bash -c "source ~/miniconda3/etc/profile.d/conda.sh && conda activate frb_project && {cmd}"'
    print(f"Executing: {wsl_cmd}")
    process = subprocess.run(wsl_cmd, shell=True)
    return process.returncode

def main():
    for galaxy in GALAXIES:
        print(f"\nProcessing {galaxy}...")

        output_dir = galaxy_science(galaxy)
        ldac_file = output_dir / f"{galaxy}.ldac"
        psf_out_dir = output_dir / "PSF_Output"
        psf_out_dir.mkdir(parents=True, exist_ok=True)

        if not ldac_file.exists():
            print(f"Skipping {galaxy}: Catalog not found at {ldac_file}")
            continue

        ldac_wsl = wsl_path(ldac_file)
        psf_out_wsl = wsl_path(psf_out_dir)
        
        # Define Checkplot suffixes (must match default.psfex types roughly)
        suffixes = ["selfwhm", "fwhm", "ellipticity", "counts", "countfrac", "chi2", "resi"]
        
        # specific checkplot paths inside PSF_Output
        checkplots = [f"{psf_out_wsl}/{galaxy}_{s}" for s in suffixes]
        checkplot_arg = ",".join(checkplots)
        
        # Define CheckImage names (prefixed)
        # default.psfex names: chi.fits,proto.fits,samp.fits,resi.fits,snap.fits
        check_imgs = ["chi", "proto", "samp", "resi", "snap"]
        checkimg_paths = [f"{psf_out_wsl}/{galaxy}_{img}.fits" for img in check_imgs]
        checkimg_arg = ",".join(checkimg_paths)

        # Construct PSFEx command
        psfex_cmd = (
            f"psfex {ldac_wsl} "
            f"-c {CONFIG_FILE} "
            f"-PSF_DIR {psf_out_wsl} "
            f"-CHECKPLOT_DEV PDF "
            f"-CHECKPLOT_NAME {checkplot_arg} "
            f"-CHECKIMAGE_NAME {checkimg_arg} "
            f"-XML_NAME {psf_out_wsl}/{galaxy}_psfex.xml"
        )
        
        ret = run_wsl_command(psfex_cmd)
        if ret == 0:
            print(f"Successfully processed {galaxy}")
        else:
            print(f"Failed to process {galaxy}")

if __name__ == "__main__":
    main()
