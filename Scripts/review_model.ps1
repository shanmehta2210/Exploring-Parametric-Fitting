param (
    [string]$Galaxy
)

$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"
$gal_dir = Join-Path $root "$($Galaxy)_Analysis\Science_Output"
$fit_with = Join-Path $gal_dir "$($Galaxy)_galfit_withpsf.fits"
$fit_no = Join-Path $gal_dir "$($Galaxy)_galfit_nopsf.fits"

if (-not (Test-Path $fit_with)) { Write-Host "Fit file not found: $fit_with" -ForegroundColor Red; exit }
if (-not (Test-Path $fit_no)) { Write-Host "Fit file not found: $fit_no" -ForegroundColor Red; exit }

Write-Host "Opening $Galaxy (With vs No PSF) in DS9..."

# Open frames: [1-3] With PSF (Obs, Mod, Res), [4-6] No PSF (Obs, Mod, Res)
& $ds9 `
    "$($fit_with)[1]" "$($fit_with)[2]" "$($fit_with)[3]" `
    "$($fit_no)[1]" "$($fit_no)[2]" "$($fit_no)[3]" `
    -tile grid `
    -scale log `
    -scale mode minmax `
    -zoom to fit `
    -lock frame wcs `
    -frame 1 -title "WITH PSF: Obs" `
    -frame 2 -title "WITH PSF: Mod" `
    -frame 3 -title "WITH PSF: Res" `
    -frame 4 -title "NO PSF: Obs" `
    -frame 5 -title "NO PSF: Mod" `
    -frame 6 -title "NO PSF: Res"
