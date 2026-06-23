
$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"
$fit = "Science_Output/NGC_3245_galfit_run3.fits"
$path = Join-Path $root "NGC_3245_Analysis/$fit"

Write-Host "Opening $path in DS9..."

if (-not (Test-Path $path)) {
    Write-Host "Error: File not found at $path" -ForegroundColor Red
    exit
}

# Open Input(1), Model(2), Residual(3)
& $ds9 `
    "$($path)[1]" "$($path)[2]" "$($path)[3]" `
    -tile grid `
    -scale log `
    -scale mode minmax `
    -zoom to fit `
    -lock frame wcs `
    -frame 1 -title "Run 3: Input" `
    -frame 2 -title "Run 3: Model" `
    -frame 3 -title "Run 3: Residual"
