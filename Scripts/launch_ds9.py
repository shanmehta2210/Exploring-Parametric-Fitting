import subprocess
import os

GALAXIES = [
    "NGC_5846", "NGC_5576", "NGC_4623", "NGC_3245", 
    "NGC_4762", "NGC_4378", "NGC_4814", "NGC_3938"
]
ROOT_DIR = r"c:\Users\lenovo\Desktop\FRB-capstone"

def launch_ds9():
    fits_files = []
    for gal in GALAXIES:
        path = os.path.join(ROOT_DIR, f"{gal}_Analysis", "Science_Output", f"{gal}_r_cutout.fits")
        if os.path.exists(path):
            fits_files.append(path)
        else:
            print(f"Warning: File not found: {path}")

    if not fits_files:
        print("No FITS files found to open.")
        return

    # DS9 Command
    # -log: sets scale to log
    # -scale mode minmax: sets min/max limits
    # -tile grid: tiles frames
    # -lock frame wcs: locks navigation
    cmd = [
        "ds9",
        *fits_files,
        "-tile", "grid",
        "-scale", "log",
        "-scale", "mode", "minmax",
        "-zoom", "to", "fit",
        "-lock", "frame", "wcs"
    ]

    # Set environment variables to fix init.tcl error
    env = os.environ.copy()
    env["TCL_LIBRARY"] = r"C:\SAOImageDS9\tcl8.6"
    env["TK_LIBRARY"] = r"C:\SAOImageDS9\tk8.6"

    print(f"Executing: {' '.join(cmd)}")
    try:
        # Use Popen to launch in background and not wait
        subprocess.Popen(cmd, env=env)
        print("DS9 launched successfully in the background with Tcl/Tk env variables.")
    except Exception as e:
        print(f"Failed to launch DS9: {e}")

if __name__ == "__main__":
    launch_ds9()
