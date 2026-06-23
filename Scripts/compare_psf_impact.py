import os
import re

import matplotlib.pyplot as plt
import pandas as pd
from astropy.io import fits
from astropy.visualization import ImageNormalize, LogStretch, ZScaleInterval

from paths import FIGURES, GALAXIES, RESULTS, galaxy_science

PSF_COMPARISON_DIR = FIGURES / "psf_comparison"


def resolve_fit_logs(galaxy: str):
    """Return (nopsf_log, withpsf_log) using the same selection rules as populate_data_package."""
    science = galaxy_science(galaxy)
    logs = list(science.glob("*.log"))
    fit_logs = [p for p in logs if "fit" in p.name]
    if not fit_logs:
        return None, None

    def pick_nopsf():
        if galaxy == "NGC_5846":
            matches = [p for p in fit_logs if "nopsf" in p.name and "fixedsky" in p.name]
        elif galaxy == "NGC_5576":
            matches = [p for p in fit_logs if "nopsf" in p.name and "multi" in p.name]
        else:
            matches = [p for p in fit_logs if p.name == f"{galaxy}_fit_nopsf.log"]
            if not matches:
                matches = [p for p in fit_logs if "nopsf" in p.name]
        return matches[0] if matches else None

    def pick_withpsf():
        if galaxy == "NGC_5846":
            matches = [p for p in fit_logs if "withpsf" in p.name and "fixedsky" in p.name]
        elif galaxy == "NGC_5576":
            matches = [p for p in fit_logs if "withpsf" in p.name and "multi" in p.name]
        elif galaxy == "NGC_4762":
            matches = [p for p in fit_logs if "withpsf" in p.name and "n5" in p.name]
            if not matches:
                matches = [p for p in fit_logs if p.name == f"{galaxy}_fit_withpsf.log"]
        else:
            matches = [p for p in fit_logs if p.name == f"{galaxy}_fit_withpsf.log"]
            if not matches:
                matches = [p for p in fit_logs if "withpsf" in p.name]
        return matches[0] if matches else None

    return pick_nopsf(), pick_withpsf()


def parse_fit_log(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    chi2_match = re.search(r"Chi\^2/nu = ([\d\.]+)", content)
    chi2_nu = float(chi2_match.group(1)) if chi2_match else None

    sersics = re.findall(
        r"sersic\s+:\s+\(([\d\.\s,]+)\)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.\[\]]+)\s+([\d\.]+)\s+([\d\.\-]+)",
        content,
    )

    results = {"chi2_nu": chi2_nu}
    for i, s in enumerate(sersics):
        prefix = f"c{i+1}_"
        results[f"{prefix}mag"] = float(s[1])
        results[f"{prefix}re"] = float(s[2])
        n_str = s[3].replace("[", "").replace("]", "")
        results[f"{prefix}n"] = float(n_str)
        results[f"{prefix}ar"] = float(s[4])
        results[f"{prefix}pa"] = float(s[5])

    return results


def create_comparison_plot(galaxy, data_nopsf, data_withpsf, output_path):
    science = galaxy_science(galaxy)
    obs_path = science / f"{galaxy}_r_cutout.fits"
    nopsf_out = science / f"{galaxy}_galfit_nopsf.fits"
    withpsf_out = science / f"{galaxy}_galfit_withpsf.fits"

    if not all(p.exists() for p in [obs_path, nopsf_out, withpsf_out]):
        print(f"Missing FITS files for {galaxy}")
        return

    with fits.open(obs_path) as hdul:
        obs = hdul[0].data

    def get_galfit_imgs(path):
        with fits.open(path) as hdul:
            return hdul[2].data, hdul[3].data

    mod_no, res_no = get_galfit_imgs(nopsf_out)
    mod_psf, res_psf = get_galfit_imgs(withpsf_out)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    interval = ZScaleInterval()
    norm_obs = ImageNormalize(obs, interval=interval, stretch=LogStretch())
    norm_res = ImageNormalize(res_psf, vmin=-0.05, vmax=0.05)

    axes[0, 0].imshow(obs, origin="lower", norm=norm_obs, cmap="gray")
    axes[0, 0].set_title("Observation")
    axes[0, 1].imshow(mod_no, origin="lower", norm=norm_obs, cmap="gray")
    axes[0, 1].set_title(
        f"Model (No PSF)\n$n={data_nopsf.get('c1_n', 0):.2f}, R_e={data_nopsf.get('c1_re', 0):.1f}$"
    )
    axes[0, 2].imshow(res_no, origin="lower", norm=norm_res, cmap="RdBu_r")
    axes[0, 2].set_title(f"Residual (No PSF)\n$\\chi^2_{{\\nu}}={data_nopsf.get('chi2_nu', 0):.2f}$")

    axes[1, 0].imshow(obs, origin="lower", norm=norm_obs, cmap="gray")
    axes[1, 0].set_title("Observation")
    axes[1, 1].imshow(mod_psf, origin="lower", norm=norm_obs, cmap="gray")
    axes[1, 1].set_title(
        f"Model (With PSF)\n$n={data_withpsf.get('c1_n', 0):.2f}, R_e={data_withpsf.get('c1_re', 0):.1f}$"
    )
    axes[1, 2].imshow(res_psf, origin="lower", norm=norm_res, cmap="RdBu_r")
    axes[1, 2].set_title(
        f"Residual (With PSF)\n$\\chi^2_{{\\nu}}={data_withpsf.get('chi2_nu', 0):.2f}$"
    )

    for ax in axes.flatten():
        ax.set_xticks([])
        ax.set_yticks([])

    plt.suptitle(f"PSF Convolution Impact Analysis: {galaxy}", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    PSF_COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    summary_data = []
    RESULTS.mkdir(parents=True, exist_ok=True)

    for gal in GALAXIES:
        log_no, log_psf = resolve_fit_logs(gal)
        if not log_no or not log_psf:
            print(f"Skipping {gal}: missing canonical fit logs")
            continue

        res_no = parse_fit_log(log_no)
        res_psf = parse_fit_log(log_psf)

        if res_no and res_psf:
            print(f"Analyzing {gal}...")
            summary_data.append(
                {
                    "galaxy": gal,
                    "chi2_no": res_no.get("chi2_nu"),
                    "chi2_psf": res_psf.get("chi2_nu"),
                    "n_no": res_no.get("c1_n"),
                    "n_psf": res_psf.get("c1_n"),
                    "re_no": res_no.get("c1_re"),
                    "re_psf": res_psf.get("c1_re"),
                    "delta_n": res_psf.get("c1_n", 0) - res_no.get("c1_n", 0),
                    "delta_re": res_psf.get("c1_re", 0) - res_no.get("c1_re", 0),
                }
            )
            plot_path = PSF_COMPARISON_DIR / f"{gal}_psf_impact.png"
            create_comparison_plot(gal, res_no, res_psf, plot_path)

    df = pd.DataFrame(summary_data)
    df.to_csv(RESULTS / "psf_impact_summary.csv", index=False)
    print("\nSummary and plots generated.")
    if not df.empty:
        print(df[["galaxy", "delta_n", "delta_re", "chi2_psf", "chi2_no"]])


if __name__ == "__main__":
    main()
