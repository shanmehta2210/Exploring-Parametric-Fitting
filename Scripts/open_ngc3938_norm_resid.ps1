
$ds9 = "C:\SAOImageDS9\ds9.exe"
$norm_resid = "c:\Users\lenovo\Desktop\FRB-capstone\NGC_3938_Analysis\Science_Output\NGC_3938_norm_resid.fits"

# Verify file exists
if (-not (Test-Path $norm_resid)) {
    Write-Host "Error: Normalized Residual file not found at $norm_resid"
    exit
}

Write-Host "Opening NGC 3938 Normalized Residual in DS9..."
Write-Host "File: $norm_resid"

& $ds9 $norm_resid -scale log -scale mode minmax -cmap cool -zoom to fit
