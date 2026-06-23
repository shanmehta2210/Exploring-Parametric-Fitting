"""Generate Input | Model | Residual panel PNGs from GALFIT output FITS."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.visualization import (
    ImageNormalize,
    LinearStretch,
    LogStretch,
    MinMaxInterval,
    ZScaleInterval,
)

from paths import FIGURES, GALAXIES, galaxy_science

PANELS_DIR = FIGURES / "fit_panels"
COMPONENTS = {1: "Input", 2: "Model", 3: "Residual"}


def save_panel(data: np.ndarray, title: str, stretch, interval, cmap: str = "gray") -> None:
    norm = ImageNormalize(data, interval=interval, stretch=stretch)
    plt.imshow(data, origin="lower", cmap=cmap, norm=norm)
    plt.title(title, fontsize=10)
    plt.axis("off")


def generate_panel(
    galaxy: str,
    variant: str = "withpsf",
    output_dir: Path | None = None,
) -> Path | None:
    science = galaxy_science(galaxy)
    input_file = science / f"{galaxy}_galfit_{variant}.fits"
    if not input_file.exists():
        print(f"Skipping {galaxy} ({variant}): missing {input_file}")
        return None

    out_dir = output_dir or PANELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{galaxy}_{variant}.png"

    with fits.open(input_file) as hdul:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        for ext_idx, name in COMPONENTS.items():
            if ext_idx >= len(hdul):
                print(f"Warning: extension {ext_idx} missing in {input_file}")
                continue
            data = hdul[ext_idx].data
            ax = axes[ext_idx - 1]
            plt.sca(ax)
            if name == "Residual":
                save_panel(
                    data,
                    name,
                    LinearStretch(),
                    ZScaleInterval(),
                    cmap="RdBu_r",
                )
            else:
                save_panel(
                    data,
                    name,
                    LogStretch(1000),
                    MinMaxInterval(),
                )

    fig.suptitle(f"{galaxy} — GALFIT ({variant.replace('withpsf', 'with PSF').replace('nopsf', 'no PSF')})")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GALFIT fit panel PNGs.")
    parser.add_argument(
        "--galaxy",
        action="append",
        help="Galaxy ID (e.g. NGC_4378). Repeatable; default is all 8 targets.",
    )
    parser.add_argument(
        "--variant",
        choices=("withpsf", "nopsf", "both"),
        default="withpsf",
        help="Which GALFIT run to visualize.",
    )
    args = parser.parse_args()

    galaxies = args.galaxy or GALAXIES
    variants = ["withpsf", "nopsf"] if args.variant == "both" else [args.variant]

    for galaxy in galaxies:
        for variant in variants:
            generate_panel(galaxy, variant=variant)


if __name__ == "__main__":
    main()
