import os
import subprocess
import time

from paths import GALAXIES, ROOT, galaxy_dir, wsl_path

def run_wsl_command(cmd, cwd_wsl):
    # Combine cd and the command
    wsl_cmd_wrapped = f'wsl bash -c "source ~/miniconda3/etc/profile.d/conda.sh && conda activate frb_project && cd {cwd_wsl} && {cmd}"'
    print(f"\nExecuting in WSL (at {cwd_wsl}): {cmd}")
    try:
        process = subprocess.Popen(wsl_cmd_wrapped, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if stdout: print(f"STDOUT: {stdout.strip()}")
        if stderr: print(f"STDERR: {stderr.strip()}")
        return process.returncode
    except Exception as e:
        print(f"Exception running WSL command: {e}")
        return -1

def main():
    for galaxy in GALAXIES:
        print(f"\n" + "="*50)
        print(f"Processing Galaxy: {galaxy}")
        print("="*50)
        
        gal_dir = galaxy_dir(galaxy)
        if not gal_dir.exists():
            print(f"ERROR: Directory {gal_dir} not found.")
            continue

        gal_dir_wsl = wsl_path(gal_dir)
        
        # In each galaxy folder, Science_Output contains the cutout
        img_name = f"Science_Output/{galaxy}_r_cutout.fits"
        sig_name = f"Science_Output/{galaxy}_r_sigma_cutout.fits"
        
        # Check if files exist locally first
        if not (gal_dir / img_name).exists():
            print(f"ERROR: Image {img_name} not found in {gal_dir}.")
            continue
            
        # Build command with paths RELATIVE to the galaxy directory
        # sex <image> -c Configuration/default.sex ...
        sex_cmd = (
            f"sex {img_name} "
            f"-c Configuration/default.sex "
            f"-CATALOG_NAME Science_Output/{galaxy}.ldac "
            f"-PARAMETERS_NAME Configuration/default.param "
            f"-WEIGHT_IMAGE {sig_name} "
            f"-CHECKIMAGE_TYPE OBJECTS,SEGMENTATION "
            f"-CHECKIMAGE_NAME Science_Output/objects.fits,Science_Output/segmentation.fits"
        )
        
        if "3938" in galaxy:
            # NGC 3938 is large, needs larger background mesh
            sex_cmd += " -BACK_SIZE 512"
            
        ret = run_wsl_command(sex_cmd, gal_dir_wsl)
        
        if ret == 0:
            local_cat = gal_dir / "Science_Output" / f"{galaxy}.ldac"
            if local_cat.exists():
                mtime = local_cat.stat().st_mtime
                print(f"SUCCESS: {galaxy}.ldac updated. New mtime: {time.ctime(mtime)}")
            else:
                print(f"WARNING: SExtractor returned 0 but {local_cat} does not exist!")
        else:
            print(f"FAILURE: SExtractor exited with code {ret}")

if __name__ == "__main__":
    main()
