
$ds9 = "C:\SAOImageDS9\ds9.exe"
$mask = "c:\Users\lenovo\Desktop\FRB-capstone\NGC_3938_Analysis\Science_Output\NGC_3938_mask.fits"

if (-not (Test-Path $mask)) {
    Write-Host "Error: Mask file not found at $mask"
    exit
}

Write-Host "Opening NGC 3938 Mask in DS9..."
# Open mask
& $ds9 $mask -zoom to fit -cmap grey
