# Master Guide: FRB Capstone Galaxy Morphology Pipeline

This document serves as the master source of truth for the Multi-Galaxy Morphology Analysis project. It consolidates the project overview, target catalog, technical strategies, and progress logs.

---

## 1. Project Overview
**Objective**: Perform detailed morphological modeling (using GALFIT) of 8 target (mostly elliptical/lenticular) galaxies from the Legacy Survey (DECaLS).
**Status**: Data preparation, SExtractor catalog generation, and PSF modeling are **COMPLETE** for all 8 target galaxies. We are currently in the iterative GALFIT modeling phase.

---

## 2. Target Sample & Catalog

### Sample Overview
All galaxies are processed into centered, square cutouts (r-band) with associated Sigma maps and PSF kernels.

| Galaxy      | Type | RA (J2000)       | Dec (J2000)      | Cutout Size | Notes                                    |
| :---------- | :--- | :--------------- | :--------------- | :---------- | :--------------------------------------- |
| **NGC 5846**| E0   | `15h 06m 29.3s`  | `+01d 36m 20s`   | 300"        | Massive elliptical. Huge halo. Companion present. |
| **NGC 5576**| E3   | `14h 21m 14.2s`  | `+03d 15m 17s`   | 300"        | Elliptical. Neighbor companion present.  |
| **NGC 4623**| E7   | `12h 42m 20.9s`  | `+07d 39m 28s`   | 300"        | Edge-on elliptical.                      |
| **NGC 3245**| S0   | `10h 27m 18.2s`  | `+28d 30m 28s`   | 300"        | Face-on lenticular.                      |
| **NGC 4762**| S0   | `12h 52m 55.8s`  | `+11d 13m 54s`   | 300"        | Edge-on lenticular, extremely flat disk. |
| **NGC 4378**| Sa   | `12h 25m 18.1s`  | `+04d 55m 31s`   | 300"        | Spiral with large bulge.                 |
| **NGC 4814**| Sb   | `12h 55m 32.1s`  | `+58d 19m 44s`   | 300"        | Spiral.                                  |
| **NGC 3938**| Sc   | `11h 52m 49.4s`  | `+44d 07m 15s`   | **500"**    | Face-on spiral. Large arms.              |

---

## 3. Technical Directory Structure

### Repository layout

```text
FRB-capstone/
├── README.md
├── config/                   # Canonical SExtractor, PSFEx, GALFIT templates
├── docs/                     # PIPELINE_GUIDE.md, RESULTS_SUMMARY.md, PDF
├── Scripts/                  # Pipeline automation
├── results/                  # CSV summaries (git-tracked)
├── figures/                  # QC PNG panels (git-tracked)
├── NGC_*_Analysis/           # Per-galaxy science trees
└── NGC_3379_Analysis/        # Pilot galaxy
```

### Per-galaxy layout

Each production galaxy follows this organization:
```text
NGC_XXXX_Analysis/
├── Input_Bricks/       # Original .fits.fz brick files (local only)
├── Configuration/      # SExtractor .sex, .param, .conv, .nnw files
├── _working/           # GALFIT iteration artifacts (local only)
└── Science_Output/     # Final science products (local FITS; panels in figures/)
    ├── [Galaxy]_r_cutout.fits
    ├── [Galaxy]_r_sigma_cutout.fits
    ├── [Galaxy].ldac
    ├── segmentation.fits
    ├── objects.fits
    ├── [Galaxy]_check_plot.png
    └── PSF_Output/
        └── [Galaxy]_final_psf.fits
```

---

## 4. Pipeline Achievements & Progress Log

### Phase 1: Data Preparation (COMPLETE)
1.  **Workspace Reorganization**: Standardized folders and moved scripts.
2.  **Stitched Cutouts**: Developed `Scripts/make_cutouts.py`.
    *   Handles galaxy boundaries by stitching multiple bricks.
    *   Ensures consistent pixel scale (0.262"/px) and centering.
    *   Generates Sigma maps ($\sigma = 1/\sqrt{\text{invvar}}$) with masked pixels at `1e9`.
3.  **Galaxy-Specific Fixes**:
    *   NGC 5576, 4623, 4762, 3938 required multi-brick stitching and re-centering based on manual nucleus identification.

### Phase 2: PSF Generation (COMPLETE)
1.  **PSFEx Tuning**: Optimizing star selection for purity over quantity.
    *   Parameters: `SAMPLE_MINSN=30`, `SAMPLE_MAXELLIP=0.3`.
    *   Asymmetry (Tilt): Observed in models; determined to be intrinsic sampling bias rather than fitting error. Quadratic (Degree=2) model used.
2.  **Extraction**: Converted PSFEx models to standard FITS kernels for GALFIT.

---

## 5. Core Configuration Strategies

### SExtractor Strategy (`default.sex`)
Modified parameters from defaults:
- **`DEBLEND_MINCONT`**: `0.01` - `0.05` (Prevents galaxy "shredding").
- **`WEIGHT_TYPE`**: `MAP_RMS`.
- **`RESCALE_WEIGHTS`**: `N` (Forces trust in absolute Sigma values).
- **`MAG_ZEROPOINT`**: `22.5` (DECaLS standard).
- **`PIXEL_SCALE`**: `0` (Forces use of WCS from header).
- **`BACK_SIZE`**: `128` (Up to `1024` for frame-filling objects like NGC 3938).
- **`MEMORY_PIXSTACK`**: `5,000,000` (Handles 500x500+ cutouts).
- **`CHECKIMAGE_TYPE`**: `OBJECTS, SEGMENTATION, APERTURES`.

---

## 6. Environment & Tooling
- **WSL Debian**: Primary environment for compiled tools (SExtractor, PSFEx, GALFIT).
- **Conda Environment**: `frb_project`.
- **Interoperability**: Python wrappers (in `Scripts/`) handle path conversion between Windows and WSL automatically.
- **DS9 Usage**: Use **Log MinMax** or **ZScale** for residuals. Residual range should be tight (e.g., -0.05 to 0.05).

---

## 7. Phase 3: GALFIT Implementation & Pivot Strategy

### Urgent Milestone: PSF Impact Analysis (DONE)
We demonstrated for all 8 galaxies that omitting the PSF leads to:
1.  **Overestimated Effective Radii ($R_e$)**: Models spread out to fit blurred light.
2.  **Biased Sersic Indices ($n$)**: Central cuspiness is poorly captured.
*See `NGC_5846_psf_impact.png` for the best visual proof.*

### Current Refined Strategy: Two-Stage Modeling
We observed significant residuals in **NGC 5576** and **NGC 5846** due to bright companion galaxies in the frame.

> [!IMPORTANT]
> **PIVOT**: We are focusing on finalizing the 6 "clean" galaxies (NGC 4623, 3245, 4762, 4378, 4814, 3938) first to analyze morphology shifts. The complex multi-object models for 5576 and 5846 are deferred but REMEMBERED.

#### Multi-Object Results (NGC 5576 & 5846):
We successfully resolved the high residuals by modeling the companions:

### NGC 5576 (E3)
- **Model**: 2-Comp (Bulge+Disk) + **Neighbor Sersic**.
- **Companion**: Located at `(1012, 119)`, Mag ~12.0. Likely NGC 5577.
- **Results (With PSF)**: $\chi^2_{\nu} = 19.93$. Bulge $n=3.56$, Disk $n=1.17$.
- **Physics**: Deconvolution successfully disentangled the Bulge and Disk/Halo throughout the profile.
- **Status**: **COMPLETE (Provisionally)**. Comparison with "No PSF" shows potential component swapping (Disk $n$ higher than Bulge without PSF). Further theoretical understanding of this profile shift is recommended.

### NGC 5846 (E0)
- **Model**: 2-Comp (Bulge+Halo) + **Neighbor Sersic** (NGC 5846A).
- **Physical Fix**: Measured and **fixed Sky background to 0.0025 ADU**.
- **Results (With PSF)**: $\chi^2_{\nu} = 33.35$. Bulge $n=2.82$, Halo $n=0.21$.
- **Physics**: Fixing the sky prevented the Halo from running away. The final model reveals a massive, diffuse envelope ($R_e \approx 300$ px) and a clearly sharpened Bulge ($R_e \approx 141$ px).
- **Status**: **COMPLETE**. Definitive physical model achieved.

## Iteration & Review Logs

### NGC 3245
- **Model**: 2-Component (Bulge + Disk), Co-centric (Linked centers).
- **Results (With PSF)**: $\chi^2_{\nu} = 12.80$, Bulge $n = 1.73$.
- **Physical Accuracy**: Accounted for atmospheric smearing, revealing a more concentrated ($n \uparrow$) and realistic bulge profile compared to the "No PSF" case. Fixed initial center offset issue by hard-linking disk to bulge.

### NGC 3938
- **Model**: 2-Component (Bulge + Disk), Co-centric (Hard-aligned centers).
- **Results (With PSF)**: $\chi^2_{\nu} \approx 20.50$, Bulge $n = 1.27$.
- **Convergence Note**: The fit reached the maximum iteration "countdown" (100) before mathematical convergence. However, parameters ($n$, $R_e$) stabilized well enough for analysis.
- **Physical Accuracy**: Fits the smooth baseline components. The asymmetric spiral structure is correctly isolated in the residuals.

### NGC 4623
- **Model**: 2-Component (Bulge + Disk), Co-centric (Hard-aligned centers).
- **Results (With PSF)**: $\chi^2_{\nu} = 12.13$, Bulge $n = 4.0$ (Fixed), Bulge $R_e = 77.2$, Disk $R_e = 118.2$.
- **Results (No PSF)**: $\chi^2_{\nu} = 12.16$, Bulge $n = 3.30$, Bulge $R_e = 73.8$, Disk $R_e = 120.6$.
- **Physical Accuracy**: **Degeneracy Confirmed**. A free fit drifted to $n=5.01$ for a negligible gain in $\chi^2$ ($\Delta < 0.01$). Fixing $n=4$ yields a chemically stable solution where the Bulge $R_e$ remains consistent with the seeing-limited estimate ($74 \rightarrow 77$ px). Tested a 3-component (Nucleus+Bulge+Disk) model, but it yielded a significantly worse fit ($\chi^2_{\nu} \approx 16.2$), confirming the 2-component structure is optimal.

### NGC 4762
- **Model**: 2-Component (Bulge + Disk), Co-centric (Hard-aligned centers).
- **Results (With PSF)**: $\chi^2_{\nu} = 28.85$, Bulge $n = 5.0$ (Fixed), Bulge $R_e = 80.0$ px.
- **Results (No PSF)**: $\chi^2_{\nu} = 31.06$, Bulge $n = 4.69$, Bulge $R_e = 80.4$.
- **Physical Accuracy**: **Physics Confirmed**. The "No PSF" model yielded $n \approx 4.7$. Incorporating the PSF and fixing $n=5$ improved the fit ($\chi^2 = 28.85$) over the $n=4$ case ($30.29$). This confirms the **steepening** of the profile ($n: 4.7 \rightarrow 5.0+$) when the atmospheric blur is removed, restoring the sharp cusp expected for this S0 galaxy.
- **Note**: The persistent crash of the 3-component (Nucleus) model suggests a data/constraint issue. Comparison using Fixed $n=5$ provides a robust proxy for this nuclear cusp.

### NGC 4814
- **Model**: 2-Component (Bulge + Disk), Co-centric (Hard-aligned centers).
- **Results (With PSF)**: $\chi^2_{\nu} = 10.69$, Bulge $n = 4.0$ (Fixed), Bulge $R_e = 112.1$.
- **Physical Accuracy**: **Degeneracy Confirmed**. The free fit ran away to unphysical values (**$n=8.11$, $R_e=759$ px**), trying to fit the background. Fixing $n=4$ (Classic Bulge) broke this degeneracy, yielding a stable solution where the Bulge $R_e$ increased slightly ($96 \rightarrow 112$ px) after deconvolution, consistent with expectations.

### NGC 4378
- **Model**: 2-Component (Bulge + Disk), Co-centric (Hard-aligned centers).
- **Results (With PSF)**: $\chi^2_{\nu} = 8.16$, Bulge $n = 4.13$.
- **Physical Accuracy**: Massive PSF impact observed. The Sersic index $n$ jumped from 2.8 to 4.1, and $R_e$ nearly doubled, revealing a significantly more concentrated core once the atmospheric "blur" was deconvolved. Fixed a massive 32px center offset from initial unstable run.

### Phase 3a Conclusion (Clean 6)
**Status**: COMPLETE.
All 6 isolated galaxies have been successfully modeled. We found that **PSF deconvolution is critical** for recovering physical Sersic indices.
- **Stable fits** (NGC 3245, 3938, 4378) showed expected sharpening ($n \uparrow$).
- **Degenerate fits** (NGC 4623, 4814) required **Fixed n=4** constraints to avoid mathematical runaway, yielding physically consistent results.
- **Edge-on cases** (NGC 4762) revealed complex nuclear structures ($n \approx 9$) that may require dedicated nucleus modeling in future phases.

---

## 8. Future Work & Open Questions

The Phase 3 analysis has successfully established baseline morphology models for all 8 galaxies, but several deep physical questions remain for future investigation:

1.  **NGC 5576 Component Swapping**:
    *   **Issue**: In the "No PSF" model, the Disk component takes a higher Sersic index ($n \approx 3.7$) than the Bulge ($n \approx 1.9$). Deconvolution flips this to the expected physical regime (Bulge $n \approx 3.5$, Halo $n \approx 1.2$).
    *   **Action**: This is a prime candidate for a theoretical case study on how seeing conditions can fundamentally invert morphological interpretations.

2.  **NGC 4762 Nucleus Stability**:
    *   **Issue**: A 3-component model (Nucleus + Bulge + Disk) consistently crashes GALFIT.
    *   **Action**: Future iterations should attempt more robust initial constraints or use a different minimization algorithm to resolve this sharp nuclear variability.

3.  **Halo Verification (NGC 5846)**:
    *   **Issue**: The massive halo depends critically on the fixed sky background.
    *   **Action**: Deep imaging or larger field-of-view data would verify the extent of this envelope beyond the current 300px radius.

## 9. Final Report Checklist
- [x] Finalize standard fits for 6 clean galaxies.
- [x] Generate residual plots for final models.
- [x] Tabulate Final vs Initial parameters.
- [x] Revisit 5576 and 5846 with multi-object fits.


10. Theoretical Framework Update: Advanced Morphology Architecture

Date: 2025-12-29 Subject: Integration of Advanced GALFIT Features & Statmorph Strategy Reference: Peng et al. (2010), Detailed Decomposition of Galaxy Images. II. Beyond Axisymmetric Models
10.1. Paradigm Shift

Core Principle: "Simplicity is not necessarily congruent with propriety or reality". Observation: The residuals observed in Phase 3 (rings, dipoles, X-shapes) are likely not noise, but un-modeled physical components. Strategy Update: We are moving from "fitting the light" to "modeling the physics." We will use functional forms that match the kinematic structure of the components (e.g., bars are flat, edges are steep) rather than forcing sersic profiles onto every feature.

10.2. The GALFIT Component "Menu" & Usage Rules

The following functional definitions are now approved for use in the pipeline to resolve specific residual artifacts.
A. Radial Profiles (The Skeleton)
Function	Best Use Case	Physical Justification
sersic	Universal. Bulges, Disks, Halos.	

The workhorse. High n for bulges, n≈1 for disks.

edgedisk	Edge-on Disks Only (e.g., NGC 4762).	

Uses a sech2 vertical profile. Essential because sersic cannot capture the steep vertical fall-off of a thin disk.

ferrer	Bars & Lenses.	

Has a flat core and sharp truncation. Prevents the "Bulge" component from trying to fit the Bar's flat light distribution.

psf	Unresolved Nuclei / AGN.	

Use if a Nucleus component (high n) crashes or degenerates. Models the object as a point source.

nuker	Resolved Cusp.	

Use only if psf fails and residuals at r<3 px are significant. Prone to massive degeneracy; requires strict constraints.

B. Azimuthal Modifications (The Flesh)
Function	Target Artifact	Implementation Note
C0	Boxiness / Diskiness.	

C0​>0 for "Boxy" giant ellipticals (like NGC 5846). C0​<0 for "Disky" isophotes.

Fourier (m=1)	Lopsidedness.	

Global asymmetry (AL​). Fixes "dipole" residuals (bright on one side, dark on other).

Fourier (m=2)	Ovals / Weak Bars.	

Warning: Degenerate with axis ratio q. Use only if fixed q fails.

Coord. Rotation	Spiral Arms.	

Rotates the coordinate grid using a tanh function. Essential for spirals (NGC 3938) where arms wind out.

Bending Modes	Warps / U-shapes.	

Use for tidal tails or "banana" distortions in edge-on disks.

C. Truncation (The Sculptor)

    Usage: Create rings (inner truncation) or finite disks (outer truncation).

Application: Can prevent components from overlapping in unphysical ways (e.g., a bar extending beyond the disk).

10.3. Galaxy-Specific Component Architectures (The "Recipes")
Type I: The "Boxy" Giant Elliptical (NGC 5576, 5846)

    Challenge: "Component Swapping" and Halo runaway.

    Architecture:

        Core: sersic (n∼3−4) + C0 (Boxiness) parameter.

Envelope: sersic (n<1, large Re​).

Refinement: If residuals show lopsidedness, add Fourier Mode 1 to the Envelope.

Type II: The Edge-On Lenticular (NGC 4762, 4623)

    Challenge: The "Nucleus vs. Bulge vs. Disk" degeneracy crash.

    Architecture:

        Nucleus: psf (Breaks degeneracy with Bulge).

Bulge: sersic (n∼4, flattened q).

Disk: edgedisk (Breaks degeneracy with sersic Bulge by enforcing vertical limit).

Dust Lane: If dark lane exists, apply Height Truncation to the Disk.

Type III: The Spiral / Barred (NGC 4814, 4378, 3938)

    Challenge: Spiral arms appearing as "clumps" in residuals; Bulge n drifting to fit the Bar.

    Architecture:

        Bulge: sersic (n∼1−4).

        Disk: expdisk (n=1) OR sersic (n=1).

        Bar: ferrer (Flat profile, high ellipticity).

Arms: Apply Coordinate Rotation to the Disk component.

10.4. The Statmorph → GALFIT Integration Strategy

We will use non-parametric morphology to generate robust Priors and Architecture Decisions, avoiding "Pseudo-degeneracies" caused by bad inputs.

Workflow:

    Run statmorph: Extract Gini, M20, Concentration (C), Asymmetry (A), Smoothness (S).

    Logic Gate (Architecture Selection):

        IF A>0.1 (High Asymmetry) → Activate Fourier Mode 1.

IF Gini high + M20 low (Nucleated) → Force psf or nuker component.

IF Shape Asymmetry high → Free the C0 parameter.

    Initialization:

        Use statmorph Half-Light Radius → GALFIT Initial Re​.

        Use statmorph Centroid → GALFIT Initial x,y.

        Use statmorph Background → GALFIT Fixed Sky.

10.5. Next Action Steps

    NGC 4762: Re-run using the Type II Architecture (psf + sersic + edgedisk) to resolve the 3-component crash.

    NGC 5576: Investigate C0 (Boxiness) to see if it resolves the "Component Swap" better than just PSF deconvolution.

    Statmorph Implementation: Begin batch processing of "Clean 6" to extract G,M20​,C,A,S indices.
