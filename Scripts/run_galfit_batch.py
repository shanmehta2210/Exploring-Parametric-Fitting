import os
import subprocess

from paths import GALAXIES, galaxy_dir, wsl_path

def run_wsl_command(cmd, cwd_wsl):
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
        print(f"GALFIT Batch: {galaxy}")
        print("="*50)
        
        gal_dir = galaxy_dir(galaxy)
        if not gal_dir.exists():
            print(f"ERROR: Directory {gal_dir} not found.")
            continue

        gal_dir_wsl = wsl_path(gal_dir)
        
        for suffix in ["nopsf", "withpsf"]:
            feedme = f"galfit_{suffix}.feedme"
            if not (gal_dir / feedme).exists():
                print(f"ERROR: Feedme {feedme} not found in {gal_dir}.")
                continue
            
            print(f"\n--- Running GALFIT ({suffix}) ---")
            
            # Run GALFIT
            cmd = f"galfit {feedme}"
            ret = run_wsl_command(cmd, gal_dir_wsl)
            
            if ret == 0:
                print(f"SUCCESS: GALFIT {suffix} completed for {galaxy}")
                
                # Organize fit.log
                log_src = gal_dir / "fit.log"
                log_dst = gal_dir / "Science_Output" / f"{galaxy}_fit_{suffix}.log"
                if log_src.exists():
                    os.replace(log_src, log_dst)
                    print(f"Log saved to: {log_dst}")
                
                # Clean up temporary GALFIT files if any (e.g., galfit.01, etc.)
                # Actually, standard GALFIT doesn't leave much else if successful besides the output block
            else:
                print(f"FAILURE: GALFIT {suffix} exited with code {ret}")

if __name__ == "__main__":
    main()
