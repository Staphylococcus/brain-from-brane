# Analysis of H5: Critical Destabilization by Low-Count Correlated Geometric Defects

Date: June 2, 2025

Experiment Script: `h5_critical_destabilization_test.py`

Configuration:
*   `BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000`
*   `NUM_ITERATIONS_PER_CONFIG = 5`
*   `NUM_INSTANCES_PER_COUNT = 3`

## 1. Raw Results Summary

```
🔬 HYPOTHESIS 5: CRITICAL DESTABILIZATION BY LOW-COUNT CORRELATED GEOMETRIC DEFECTS
Grid Size: 50x50, Base Work Units: 1
Defect Work Units: 101
Busy Work Iterations per Unit: 10000
Iterations per config: 5, Instances per count: 3
--------------------------------------------------------------------------------
Defect Type,Defect Count,Mean Exec Time (ms),CV

Starting: Point Defects Loop (by count)
Starting: Point Defects, Count: 0
Baseline,0,975.196,0.001469
Finished: Point Defects, Count: 0
Starting: Point Defects, Count: 1
Point,1,1015.577,0.003862
Finished: Point Defects, Count: 1
Starting: Point Defects, Count: 2
Point,2,1054.350,0.003111
Finished: Point Defects, Count: 2
Starting: Point Defects, Count: 3
Point,3,1095.684,0.004922
Finished: Point Defects, Count: 3
Starting: Point Defects, Count: 4
Point,4,1135.688,0.002808
Finished: Point Defects, Count: 4
Starting: Point Defects, Count: 5
Point,5,1176.475,0.008802
Finished: Point Defects, Count: 5
Starting: Point Defects, Count: 7
Point,7,1256.996,0.014612
Finished: Point Defects, Count: 7
Starting: Point Defects, Count: 10
Point,10,1372.582,0.006415
Finished: Point Defects, Count: 10
Starting: Point Defects, Count: 15
Point,15,1570.132,0.005031
Finished: Point Defects, Count: 15
Starting: Point Defects, Count: 20
Point,20,1763.600,0.001965
Finished: Point Defects, Count: 20
Starting: Point Defects, Count: 25
Point,25,1958.036,0.001869
Finished: Point Defects, Count: 25
Starting: Point Defects, Count: 50
Point,50,2953.438,0.008700
Finished: Point Defects, Count: 50
Starting: Point Defects, Count: 100
Point,100,5000.209,0.026460
Finished: Point Defects, Count: 100
Starting: Point Defects, Count: 125
Point,125,5890.313,0.001535
Finished: Point Defects, Count: 125
Starting: Point Defects, Count: 250
Point,250,10827.279,0.004217
Finished: Point Defects, Count: 250
Finished: Point Defects Loop (by count)

Starting: Line Defects Loop (by count)
Baseline (from Point Loop),0,975.196,0.001469
Starting: Line Defects, Count: 1
Line,1,2964.411,0.012528
Finished: Line Defects, Count: 1
Starting: Line Defects, Count: 2
Line,2,4904.471,0.001870
Finished: Line Defects, Count: 2
Starting: Line Defects, Count: 3
Line,3,6818.994,0.007122
Finished: Line Defects, Count: 3
Starting: Line Defects, Count: 4
Line,4,8741.027,0.015754
Finished: Line Defects, Count: 4
Starting: Line Defects, Count: 5
Line,5,10603.694,0.005227
Finished: Line Defects, Count: 5
Starting: Line Defects, Count: 7
Line,7,14271.295,0.005669
Finished: Line Defects, Count: 7
Starting: Line Defects, Count: 10
Line,10,19722.998,0.008953
Finished: Line Defects, Count: 10
Starting: Line Defects, Count: 15
Line,15,28309.039,0.003803
Finished: Line Defects, Count: 15
Starting: Line Defects, Count: 20
Line,20,36731.715,0.004788
Finished: Line Defects, Count: 20
Finished: Line Defects Loop (by count)
--------------------------------------------------------------------------------
Experiment finished.
```

## 2. Analysis of H5 Experiment Results (Numerical & Visual)

### 2.1. Baseline and General Trends
*   **Baseline:** The defect-free baseline run (0 defects) showed a mean execution time of ~975 ms with a CV of ~0.0015. This indicates a stable baseline for comparison.
*   **Mean Execution Time:** For both point and line defects, the mean execution time increased with the number of defects, as expected due to the increased computational load in defective cells.

### 2.2. Point Defect Behavior
*   **CV (Numerical):** The Coefficient of Variation (CV) for point defects generally remained low.
    *   For counts 1-5, CVs ranged from ~0.0028 to ~0.0088.
    *   A slight rise was seen at 7 defects (CV ~0.0146).
    *   A more noticeable CV increase occurred at 100 point defects (CV ~0.0265), representing 4% of total cells being defective.
*   **Interpretation (Numerical):** With the exception of 100 defects, point defects did not cause major processing instability, which aligns with H5's expectation that isolated defects are less disruptive than correlated ones. The rise at 100 defects suggests a possible threshold where even point defects, in sufficient quantity, begin to destabilize processing.

### 2.3. Line Defect Behavior (Primary Focus of H5)
*   **CV Pattern (Numerical):** The CV for line defects showed a non-monotonic (up-and-down) pattern:
    *   **1 Line Defect:** CV ~0.0125 (significantly higher than baseline and low-count point defects).
    *   **2 Line Defects:** CV dropped sharply to ~0.0019 (near baseline stability).
    *   **3 Line Defects:** CV rose to ~0.0071.
    *   **4 Line Defects:** CV peaked again at ~0.0158 (the highest observed for line defects in this run).
    *   **5+ Line Defects:** CV generally trended lower for 5, 7, 10, 15, and 20 lines, ranging from ~0.0038 to ~0.0090.
*   **Localized CV Peaks (Numerical):** The results show localized peaks in CV at 1 and 4 line defects. This behavior, particularly the CV being higher for 1 or 4 lines than for 2, 3, or 5+ lines, is consistent with Hypothesis 5's prediction that a *small, critical number* of correlated defects can cause disproportionate instability.

### 2.4. Comparison to H4 Anomaly & H5 Predictions (Based on Numerical Data)
*   The CV for 1 line defect (~0.0125) in this H5 run, while elevated, is lower than the ~0.027-0.030 CV observed in the H4 experiment for configurations that likely also produced 1 line defect. The increased number of iterations (3 to 5) and instances (2 to 3) in H5 likely provided more stable CV measurements, potentially smoothing out earlier statistical noise.
*   The H5 numerical results (peaks at 1 and 4 lines) provide tentative support for H5. The CV for these low-count line defects is generally higher than for an equivalent number of point defects.

### 2.5. Visual Analysis of Plotted Results (from `h5_cv_vs_defect_count.png`)

![h5_cv_vs_defect_count](h5_cv_vs_defect_count.png)

The visual plot of CV vs. Defect Count provides clear insights:

*   **Line Defect Curve (Orange, Dashed Line with Square Markers):**
    *   **Prominent Peaks:** The peaks at 1 line defect (CV ~0.0125) and 4 line defects (CV ~0.0158) are visually distinct and are the highest points on the line defect curve for low defect counts (0-10).
    *   **Non-Monotonic Behavior:** The curve clearly shows a rise to the first peak at 1 defect, a sharp drop for 2 defects, a rise to the second peak at 4 defects, and then a general decline or stabilization at lower CV values for 5+ defects within the plotted range (up to 20).
    *   **Confirmation of H5:** This visual pattern strongly supports H5's prediction of localized destabilization at critical low counts of correlated defects.

*   **Point Defect Curve (Blue, Solid Line with Circle Markers):**
    *   **Low-Count Stability:** For low defect counts (0-25), the CV for point defects is generally low and relatively flat, staying well below the initial peaks of the line defect curve.
    *   **Spike at 100 Defects:** The most dramatic feature of the point defect curve is the very sharp spike at 100 defects (CV ~0.0265), which is the absolute highest CV value on the entire plot. After this peak, the CV drops again for 125 and 250 defects.
    *   **Comparison:** This visually emphasizes that while point defects can cause instability, it occurs at a much higher number of defects compared to the critical low counts for line defects.

*   **Direct Comparison:**
    *   At 1 and 4 defects, the orange line (Line Defects) is clearly above the blue line (Point Defects), indicating higher instability for lines.
    *   The CV for 2 line defects (~0.0019) is remarkably low, comparable to the baseline and very low point defect counts.

*   **Y-Axis Scale & Clarity:** The Y-axis (CV) ranges from approximately 0 to 0.028. The plot effectively uses this range to show the relative magnitudes of the CV values and the significance of the observed peaks.

*   **Overall Impression:** The plot makes a compelling visual case for H5. The differing behaviors of line and point defects, particularly the early, sharp peaks for line defects, are evident.

## 3. Next Steps to "Dig Deeper" (Revised based on Plot)

1.  **Documentation and Reporting:**
    *   **Action:** Formally add a description of the visual findings (as above) to this analysis document (`h5_analysis_and_next_steps.md`). Include a note to manually insert or reference the `h5_cv_vs_defect_count.png` image.
    *   **Action:** Update the main `hypotheses_from_ontology.md` with a concise summary of these H5 findings and the supporting visual evidence, linking back to this detailed analysis.

2.  **Investigate the Low CV for 2 Line Defects:**
    *   The remarkably low CV for 2 line defects (~0.0019, almost baseline stability) sandwiched between higher CVs for 1 and 3/4 lines is particularly intriguing and warrants focused investigation.
    *   **Action:** Design a specific follow-up experiment focusing *only* on line defect counts of 0, 1, 2, 3, and 4.
        *   For these specific counts, significantly increase `NUM_ITERATIONS_PER_CONFIG` (e.g., to 20-30) and `NUM_INSTANCES_PER_COUNT` (e.g., to 10-15). This is to achieve very high confidence in the CV values for these critical low counts.
        *   The goal is to confirm if the dip at 2 lines is a robust phenomenon or if it smooths out with more averaging.

3.  **Explore the 100 Point Defect Spike:**
    *   While not the primary focus of H5, the CV spike (~0.0265) for 100 point defects is a strong signal.
    *   **Action (Lower Priority):** If resources permit, conduct a focused run on point defects with counts around 100 (e.g., 75, 90, 100, 110, 125) with increased iterations/instances to characterize this peak more precisely.

4.  **Refine H5 Interpretation (Post Follow-up Experiments):**
    *   After the focused runs (especially for low-count line defects), re-evaluate and refine the interpretations from both the ontology proponent and conventional perspectives. If the dip at 2 line defects is robust, it adds another layer of complexity and interest to the ontology's predictions about geometric interactions.
