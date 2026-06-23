
$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"

# Find specifically the SIGMA cutout files
$files = Get-ChildItem -Path $root -Recurse -Filter "*_r_sigma_cutout.fits" | 
Where-Object { $_.FullName -notmatch "Archive_Misc" -and $_.FullName -notmatch "NGC_3379" } | 
Select-Object -ExpandProperty FullName

Write-Host "Opening Sigma Maps Inspection..."
$files | ForEach-Object { Write-Host " - $_" }

# Launch with Tile mode and ZScale
& $ds9 -tile -zscale $files
