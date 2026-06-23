"""Plot PSF star candidates from a SExtractor catalog."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
from astropy.table import Table

from paths import GALAXIES, galaxy_science


def check_psf_candidates(galaxy: str) -> None:
    science = galaxy_science(galaxy)
    cat_path = science / f"{galaxy}.ldac"

    print(f"Diagnostics for {galaxy} catalog...")
    tbl = Table.read(cat_path, hdu=2)
    print(f"Loaded {len(tbl)} sources.")

    clean_mask = tbl["FLAGS"] == 0
    print(f"Clean sources (FLAGS=0): {len(tbl[clean_mask])}")

    mag = tbl["MAG_AUTO"]
    size_col = "FWHM_IMAGE" if "FWHM_IMAGE" in tbl.colnames else "FLUX_RADIUS"
    size_label = "FWHM (pixels)" if size_col == "FWHM_IMAGE" else "Flux Radius (pixels)"
    stars = tbl[tbl["CLASS_STAR"] > 0.8]
    print(f"High Confidence Stars (CLASS_STAR > 0.8): {len(stars)}")

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].scatter(mag, tbl[size_col], c="blue", s=10, alpha=0.5, label="All Objects")
    ax[0].scatter(stars["MAG_AUTO"], stars[size_col], c="red", s=20, label="CLASS_STAR > 0.8")
    ax[0].set_xlabel("MAG_AUTO")
    ax[0].set_ylabel(size_label)
    ax[0].set_title("Star-Galaxy Separation")
    ax[0].invert_xaxis()
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)

    ax[1].scatter(tbl["X_IMAGE"], tbl["Y_IMAGE"], c="black", s=1, alpha=0.3, label="All")
    ax[1].scatter(stars["X_IMAGE"], stars["Y_IMAGE"], c="red", marker="*", s=50, label="Stars")
    ax[1].set_xlabel("X")
    ax[1].set_ylabel("Y")
    ax[1].set_title(f"Star Distribution (N={len(stars)})")
    ax[1].legend()
    ax[1].axis("equal")

    plt.tight_layout()
    out_path = science / f"{galaxy}_psf_check.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved diagnostic plot: {out_path}")

    if len(stars) < 10:
        print("\nWARNING: Very few stars (<10). PSFEx might struggle.")
    elif len(stars) < 20:
        print("\nSTATUS: Low star count (10-20). PSFEx should work for constant PSF.")
    else:
        print("\nSTATUS: Good star count (>20). PSFEx should work well.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check PSF star candidates.")
    parser.add_argument("--galaxy", required=True, choices=GALAXIES)
    args = parser.parse_args()
    check_psf_candidates(args.galaxy)


if __name__ == "__main__":
    main()
