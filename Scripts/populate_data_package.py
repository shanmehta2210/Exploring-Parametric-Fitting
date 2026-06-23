import glob
import os
import shutil

from paths import CONFIG, DATA_PACKAGE, GALAXIES, ROOT, galaxy_dir, galaxy_science

SOURCE_ROOT = ROOT
DEST_ROOT = DATA_PACKAGE


def main():
    defaults_folder = DEST_ROOT / "SExtractor and PSFEx Defaults"
    if defaults_folder.exists():
        shutil.rmtree(defaults_folder)
    defaults_folder.mkdir(parents=True)

    for name in ["default.sex", "default.param"]:
        src = CONFIG / "sextractor" / name
        if src.exists():
            shutil.copy2(src, defaults_folder / name)
    psfex_src = CONFIG / "psfex" / "default.psfex"
    if psfex_src.exists():
        shutil.copy2(psfex_src, defaults_folder / "default.psfex")
    for name in ["default.conv", "default.nnw"]:
        src = CONFIG / "sextractor" / name
        if src.exists():
            shutil.copy2(src, defaults_folder / name)

    print("Refining Data Package (With Renaming)...")

    for galaxy in GALAXIES:
        source_base = galaxy_dir(galaxy)
        source_science = galaxy_science(galaxy)
        dest_path = DEST_ROOT / galaxy
        if dest_path.exists():
            shutil.rmtree(dest_path)
        dest_path.mkdir(parents=True)

        for ext in ["_r_cutout.fits", "_r_sigma_cutout.fits"]:
            src = source_science / f"{galaxy}{ext}"
            if src.exists():
                shutil.copy2(src, dest_path / src.name)

        psf_src = source_science / "PSF_Output" / f"{galaxy}_final_psf.fits"
        if psf_src.exists():
            shutil.copy2(psf_src, dest_path / psf_src.name)

        if source_science.exists():
            for log in source_science.glob("*.log"):
                log_name = log.name
                if "fit" not in log_name:
                    continue

                keep = True
                if galaxy == "NGC_5846" and "fixedsky" not in log_name:
                    keep = False
                elif galaxy == "NGC_5576" and "multi" not in log_name:
                    keep = False
                elif galaxy == "NGC_4762" and "withpsf" in log_name and "n5" not in log_name:
                    keep = False

                if keep:
                    target_name = log_name
                    if "_fit_withpsf" in log_name:
                        target_name = f"{galaxy}_fit_withpsf.log"
                    elif "_fit_nopsf" in log_name:
                        target_name = f"{galaxy}_fit_nopsf.log"
                    shutil.copy2(log, dest_path / target_name)
                    print(f"[{galaxy}] Copied {log_name} -> {target_name}")

        for fm in source_base.glob("*.feedme"):
            shutil.copy2(fm, dest_path / fm.name)

        for model in source_science.glob("*_galfit_*.fits"):
            shutil.copy2(model, dest_path / model.name)

    print("Data Package Refined Successfully (Logs Standardized).")


if __name__ == "__main__":
    main()
