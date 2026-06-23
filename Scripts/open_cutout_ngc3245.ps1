
$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"
$file = Join-Path $root "NGC_3245_Analysis/Science_Output/NGC_3245_r_cutout.fits"

Write-Host "Opening $file in DS9..."

if (-not (Test-Path $file)) {
    Write-Host "Error: File not found at $file" -ForegroundColor Red
    exit
}

& $ds9 $file -scale log -scale mode minmax -zoom to fit -cmap cool
