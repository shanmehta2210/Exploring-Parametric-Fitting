import os
import glob
import re

DATA_ROOT = r"c:\Users\lenovo\Desktop\FRB-capstone\Google_Drive_Data_Package"

GALAXIES = [
    "NGC_5846", "NGC_5576", "NGC_4623", "NGC_3245", 
    "NGC_4762", "NGC_4378", "NGC_4814", "NGC_3938"
]

LOG_MAP_WITH_PSF = {
    "NGC_5846": "NGC_5846_fit_withpsf_multi_fixedsky.log",
    "NGC_5576": "NGC_5576_fit_withpsf_multi.log",
    "NGC_4762": "NGC_4762_fit_withpsf_n5.log",
}
LOG_MAP_NO_PSF = {
    "NGC_5846": "NGC_5846_fit_nopsf_multi_fixedsky.log",
    "NGC_5576": "NGC_5576_fit_nopsf_multi.log",
}

def dump_log_stats(log_path, out_file):
    out_file.write(f"--- Log: {os.path.basename(log_path)} ---\n")
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            if "Chi^2/nu" in line:
                out_file.write(f"  {line.strip()}\n")
            if "sersic" in line:
                out_file.write(f"  {line.strip()}\n")
    except Exception as e:
        out_file.write(f"  Error reading log: {e}\n")

if __name__ == "__main__":
    with open("final_dump.txt", "w", encoding="utf-8") as out_file:
        for gal in GALAXIES:
            out_file.write(f"\nGalaxy: {gal}\n")
            dir_path = os.path.join(DATA_ROOT, gal)
            
            # PSF
            log_name = LOG_MAP_WITH_PSF.get(gal, f"{gal}_fit_withpsf.log")
            dump_log_stats(os.path.join(dir_path, log_name), out_file)
            
            # No PSF
            log_name_no = LOG_MAP_NO_PSF.get(gal, f"{gal}_fit_nopsf.log")
            dump_log_stats(os.path.join(dir_path, log_name_no), out_file)
