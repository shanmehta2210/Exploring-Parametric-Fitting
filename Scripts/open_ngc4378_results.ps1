
$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"
$fits = Join-Path $root "NGC_4378_Analysis\Science_Output\NGC_4378_galfit_nopsf.fits"

Write-Host "Opening NGC 4378 Results in DS9..."
Write-Host "File: $fits"

if (-not (Test-Path $fits)) {
    Write-Host "Error: File not found at $fits" -ForegroundColor Red
    exit
}

# Open Input[1], Model[2], Residual[3]
# Note: In PowerShell, we pass these as strings strings to DS9
& $ds9 "${fits}[1]" "${fits}[2]" "${fits}[3]" -tile columns -scale log -scale mode minmax -zoom to fit -lock frame wcs
