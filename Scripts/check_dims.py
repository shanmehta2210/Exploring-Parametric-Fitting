import glob

from paths import ROOT


def main():
    files = glob.glob(str(ROOT / "**" / "*_r_cutout.fits"), recursive=True)
    for f in sorted(files):
        print(f)


if __name__ == "__main__":
    main()
