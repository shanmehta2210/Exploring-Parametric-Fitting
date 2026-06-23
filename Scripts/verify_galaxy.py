"""Verify SExtractor segmentation for a target galaxy."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.visualization import ZScaleInterval

from paths import GALAXIES, galaxy_dir, galaxy_science


def verify(galaxy: str) -> None:
    base_dir = galaxy_dir(galaxy)
    science = galaxy_science(galaxy)
    cutout_path = science / f"{galaxy}_r_cutout.fits"
    seg_path = science / "segmentation.fits"

    print(f"Analyzing {galaxy}...")

    with fits.open(cutout_path) as hdul:
        img_data = hdul[0].data
    with fits.open(seg_path) as hdul:
        seg_data = hdul[0].data

    n_objects = int(np.max(seg_data))
    center_y, center_x = np.array(img_data.shape) // 2
    center_val = int(seg_data[int(center_y), int(center_x)])

    print(f"Total Objects Detected: {n_objects}")
    print(f"Central Pixel Segment ID: {center_val}")

    if center_val > 0:
        obj_pixels = int(np.sum(seg_data == center_val))
        print(f"Central Object Size: {obj_pixels} pixels")
        if obj_pixels < 1000:
            print("WARNING: Central object seems small. Possible shredding or mis-centering?")
        else:
            print("Central object is substantial.")
    else:
        print("WARNING: Central pixel is NOT in any segment!")

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    interval = ZScaleInterval()
    vmin, vmax = interval.get_limits(img_data)
    ax[0].imshow(img_data, origin="lower", cmap="gray", vmin=vmin, vmax=vmax)
    ax[0].set_title(f"{galaxy} Cutout")
    ax[0].scatter([center_x], [center_y], color="r", marker="x", s=100, label="Center")

    ax[1].imshow(seg_data, origin="lower", cmap="nipy_spectral", interpolation="nearest")
    ax[1].set_title(f"Segmentation Map ({n_objects} objs)")

    if center_val > 0:
        ax[0].contour(seg_data == center_val, colors="lime", levels=[0.5], linewidths=1)

    plt.tight_layout()
    out_path = science / f"{galaxy}_check_plot.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Plot saved to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify galaxy segmentation.")
    parser.add_argument("--galaxy", required=True, choices=GALAXIES)
    args = parser.parse_args()
    verify(args.galaxy)


if __name__ == "__main__":
    main()
