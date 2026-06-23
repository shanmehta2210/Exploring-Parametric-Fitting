
$ds9 = "C:\SAOImageDS9\ds9.exe"
$root = "c:\Users\lenovo\Desktop\FRB-capstone"

# Find specifically the cutout files
$files = Get-ChildItem -Path $root -Recurse -Filter "*_r_cutout.fits" | 
Where-Object { $_.Name -notmatch "sigma" -and $_.FullName -notmatch "Archive_Misc" -and $_.FullName -notmatch "NGC_3379" } | 
Select-Object -ExpandProperty FullName

Write-Host "Opening Final Inspection..."
$files | ForEach-Object { Write-Host " - $_" }

# Launch with requested scaling
& $ds9 -tile -scale log -scale minmax $files
