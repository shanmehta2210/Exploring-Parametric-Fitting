
# Script to launch DS9 with all galaxy cutouts
# Uses absolute path to DS9 since it's not in PATH

$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"

# Find all cutout files (excluding sigma maps and the misc archive)
# We look for *r_cutout.fits specifically
$files = Get-ChildItem -Path $root -Recurse -Filter "*_r_cutout.fits" | 
         Where-Object { $_.Name -notmatch "sigma" -and $_.FullName -notmatch "Archive_Misc" -and $_.FullName -notmatch "NGC_3379" } | 
         Select-Object -ExpandProperty FullName

# Check if we found files
if ($files.Count -eq 0) {
    Write-Host "No cutout files found!" -ForegroundColor Red
    exit
}

Write-Host "Opening $($files.Count) files in DS9..."
Write-Host "Files: "
$files | ForEach-Object { Write-Host " - $_" }

# Launch DS9
# -tile mode puts them in a grid
# -zscale uses smart scaling
& $ds9 -tile -zscale $files
