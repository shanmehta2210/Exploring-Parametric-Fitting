from astropy.io import fits
import numpy as np

from paths import GALAXIES, RESULTS, galaxy_science

results = []

print(f"{'Galaxy':<12} | {'X_IMAGE':<8} | {'Y_IMAGE':<8} | {'MAG':<6} | {'R_e':<6} | {'AR':<5} | {'PA':<6}")
print("-" * 65)

for gal in GALAXIES:
    cat_path = galaxy_science(gal) / f"{gal}.ldac"

    if cat_path.exists():
        with fits.open(cat_path) as hdul:
            data = hdul[2].data

            img_center = 1145 / 2.0
            if "3938" in gal:
                img_center = 1908 / 2.0

            dist = np.sqrt((data["X_IMAGE"] - img_center) ** 2 + (data["Y_IMAGE"] - img_center) ** 2)
            idx = np.argmin(dist)
            row = data[idx]

            x = row["X_IMAGE"]
            y = row["Y_IMAGE"]
            mag = row["MAG_AUTO"]

            fr = row["FLUX_RADIUS"]
            re = fr[0] if hasattr(fr, "__len__") else fr

            ar = row["B_IMAGE"] / row["A_IMAGE"]
            pa = row["THETA_IMAGE"]

            print(f"{gal:<12} | {x:8.2f} | {y:8.2f} | {mag:6.2f} | {re:6.2f} | {ar:5.2f} | {pa:6.2f}")
            results.append(
                {"galaxy": gal, "x": x, "y": y, "mag": mag, "re": re, "ar": ar, "pa": pa}
            )
    else:
        print(f"{gal:<12} | NOT FOUND")

RESULTS.mkdir(parents=True, exist_ok=True)
out_path = RESULTS / "initial_guesses.csv"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("galaxy,x,y,mag,re,ar,pa\n")
    for r in results:
        f.write(f"{r['galaxy']},{r['x']},{r['y']},{r['mag']},{r['re']},{r['ar']},{r['pa']}\n")

print(f"Saved {out_path}")
