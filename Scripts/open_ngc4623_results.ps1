
$ds9 = "C:\SAOImageDS9\ds9.exe"
$galfit_output = "c:\Users\lenovo\Desktop\FRB-capstone\NGC_4623_Analysis\Science_Output\NGC_4623_galfit_nopsf.fits"

# Verify file exists
if (-not (Test-Path $galfit_output)) {
    Write-Host "Error: GALFIT output file not found at $galfit_output"
    exit
}

Write-Host "Opening NGC 4623 Results in DS9..."
Write-Host "File: $galfit_output"

# Open Input[1], Model[2], Residual[3] explicitly
# Using -tile columns to arrange them side-by-side
& $ds9 "${galfit_output}[1]" "${galfit_output}[2]" "${galfit_output}[3]" -tile columns -scale log -scale mode minmax -cmap cool -zoom to fit -lock frame wcs
