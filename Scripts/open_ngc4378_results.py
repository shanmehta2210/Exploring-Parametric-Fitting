import subprocess
import os

# Path to the GALFIT output file
output_file = r"c:\Users\lenovo\Desktop\FRB-capstone\NGC_4378_Analysis\Science_Output\NGC_4378_galfit_nopsf.fits"

# Construct command to open Input, Model, and Residual extensions
cmd = [
    "ds9",
    f"{output_file}[1]",
    f"{output_file}[2]",
    f"{output_file}[3]",
    "-tile", "columns",
    "-scale", "mode", "minmax",
    "-scale", "log",
    "-zoom", "to", "fit",
    "-lock", "frame", "wcs"
]

# Set environment variables for DS9 on Windows
env = os.environ.copy()
env["TCL_LIBRARY"] = r"C:\SAOImageDS9\tcl8.6"
env["TK_LIBRARY"] = r"C:\SAOImageDS9\tk8.6"

print(f"Executing: {' '.join(cmd)}")
try:
    subprocess.Popen(cmd, env=env)
    print("DS9 launched successfully.")
except Exception as e:
    print(f"Failed to launch DS9: {e}")
