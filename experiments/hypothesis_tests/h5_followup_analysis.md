# Analysis of H5 Follow-up: Investigation of Low CV for 2 Line Defects

Date: $(date +%Y-%m-%d) <!-- TODO: Update date -->
Experiment Script: `h5_followup_low_count_lines_test.py`

## 1. Experiment Configuration
*   `GRID_SIZE = 50`
*   `BASE_CELL_WORK_UNITS = 1`
*   `DEFECT_CELL_WORK_UNITS = 101`
*   `BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000`
*   **`NUM_ITERATIONS_PER_CONFIG = 25`** (Increased from 5 in original H5)
*   **`NUM_INSTANCES_PER_COUNT = 10`** (Increased from 3 in original H5)
*   `LINE_DEFECT_COUNTS = [0, 1, 2, 3, 4]` (Focused range)

## 2. Purpose of Follow-up
This experiment was designed to achieve higher statistical confidence in the CV measurements for low counts of line defects (0-4), particularly to investigate the anomalously low CV observed for 2 line defects in the original H5 experiment (`h5_critical_destabilization_test.py`).

## 3. Raw Results of Follow-up Experiment

| Defect Type | Defect Count | Mean Exec Time (ms) | CV       |
| :---------- | :----------- | :------------------ | :------- |
| Baseline    | 0            | 978.750             | 0.019144 |
| Line        | 1            | 2947.899            | 0.017257 |
| Line        | 2            | 4899.179            | 0.016849 |
| Line        | 3            | 6814.106            | 0.017228 |
| Line        | 4            | 8728.362            | 0.017172 |

## 4. Comparison with Original H5 Results (for Line Defects 0-4)

**Original H5 Run (`NUM_ITERATIONS_PER_CONFIG = 5`, `NUM_INSTANCES_PER_COUNT = 3`):**
| Defect Type             | Defect Count | Mean Exec Time (ms) | CV       |
| :---------------------- | :----------- | :------------------ | :------- |
| Baseline (from Point)   | 0            | 975.196             | 0.001469 |
| Line                    | 1            | 2964.411            | 0.012528 |
| Line                    | 2            | 4904.471            | 0.001870 |
| Line                    | 3            | 6818.994            | 0.007122 |
| Line                    | 4            | 8741.027            | 0.015754 |

## 5. Analysis and Discussion in Context of Hypothesis H5

Hypothesis H5 ("Critical Destabilization by Low-Count Correlated Geometric Defects") predicted that a small, critical number of line defects would cause localized CV peaks significantly higher than baseline and equivalent point defects.

**Key Observations from Follow-up:**

1.  **Significantly Higher Baseline CV:**
    *   The baseline CV (0 defects) in this follow-up is `0.019144`. This is over **13 times higher** than the baseline CV of `0.001469` in the original H5 experiment.
    *   This suggests that the overall system state or measurement conditions during this more intensive follow-up run (approx. 16.7 times more computation per defect count) might have been subject to greater inherent variability (e.g., other system processes, thermal fluctuations from sustained CPU load over a longer period).

2.  **Re-evaluation of the 2-Line Defect Anomaly:**
    *   In the original H5 experiment, 2 line defects showed an exceptionally low CV (`0.001870`), even lower than the CV for 3 defects and comparable to the original baseline.
    *   In this follow-up, the CV for 2 line defects is `0.016849`. While this is the lowest CV among the tested defect counts (0-4) *within this specific follow-up run*, it is:
        *   Not anomalously low compared to other CVs in *this* run.
        *   Much higher than the `0.001870` observed in the original H5 run.
    *   This suggests the previous very low CV for 2 lines was likely a statistical artifact of the smaller sample size in the original H5 experiment or specific to the conditions of that shorter run. The more robust sampling here did not replicate that extreme low.

3.  **CV Pattern for Line Defects (0-4) in Follow-up:**
    *   The CVs for 0, 1, 2, 3, and 4 line defects are: `0.019144`, `0.017257`, `0.016849`, `0.017228`, `0.017172`.
    *   The highest CV is for the baseline (0 defects).
    *   All non-zero defect counts (1-4 lines) show slightly *lower* CVs than this follow-up's baseline.
    *   There is a slight "dip" where 2 lines (`0.016849`) is lower than 1 line (`0.017257`) and 3 lines (`0.017228`), but the differences are small relative to the overall CV level and the baseline.

**Implications for Hypothesis H5 Predictions:**

*   **"Localized CV peaks significantly higher than baseline"**:
    *   This core prediction of H5 is **not supported** by this follow-up experiment when using its own baseline. The CVs for 1 and 4 line defects (`0.017257` and `0.017172` respectively) are *lower* than the follow-up baseline CV (`0.019144`).
    *   The striking visual peaks from the original H5 plot (where CVs for 1 and 4 lines were ~0.012-0.015 against a ~0.0015 baseline) are absent here due to the much higher baseline and the resulting CVs for 1-4 defects being fairly similar to each other.

*   **Comparison with Zero Defects**:
    *   H5 implied that low-count line defects would be more "destabilizing" (higher CV) than zero defects. This follow-up shows the opposite for its own conditions: CVs for 1-4 lines are slightly *more stable* (lower CV) than the 0-defect baseline of this run.

*   **Shape of CV Curve**:
    *   The original H5 showed a clear rise-dip-rise-fall pattern (peaks at 1 and 4 lines, dip at 2).
    *   This follow-up, starting from a high baseline, shows a drop from baseline to 1 line, a further slight drop to 2 lines, then slight rises for 3 and 4 lines, but all these values (for 1-4 lines) are fairly close to each other (`~0.017`).

**Conclusions Regarding H5 based on this Follow-up:**

*   The increased statistical power of this follow-up experiment suggests that the dramatic CV peaks (relative to a very low baseline) and the exceptionally low CV for 2 line defects observed in the initial H5 run might have been influenced by lower sample sizes or specific, perhaps more "ideal" or less noisy, system conditions during that shorter experiment.
*   Under the conditions of this more intensive follow-up experiment (which exhibited a higher baseline CV), the evidence for H5's specific predictions of *pronounced CV peaks from low-count correlated defects being significantly higher than baseline* is weak.
*   The phenomenon of "critical destabilization" as originally envisioned (sharp, high CV peaks) appears to be either less robust, more subtle, or highly dependent on the baseline system stability than initially concluded from the first H5 run.
*   It's crucial to understand why the baseline CV was so much higher in this run. If such high baseline CVs are typical for longer, CPU-intensive tasks, then any "geometric defect" signal might be much harder to discern or might manifest differently.

## 6. Next Steps and Further Discussion Points

1.  **Investigate Baseline CV Variability and Potential Temperature Effects:**
    *   Why was the baseline CV ~0.019 in this run versus ~0.0015 in the original H5 run? Potential factors:
        *   **CPU Temperature:** Longer total experiment duration leading to sustained higher CPU temperatures, potentially causing thermal throttling or other dynamic clock adjustments that increase timing variability. This is a known factor in performance testing.
        *   Background OS/process activity levels.
        *   The nature of `time.perf_counter_ns()` over many more calls during a longer, hotter run.
    *   **Action Idea (Temperature Correlation):**
        *   Log CPU core temperatures (e.g., using system utilities like `sensors` on Linux, or platform-specific tools) concurrently with running both the original `h5_critical_destabilization_test.py` and the `h5_followup_low_count_lines_test.py` (especially their baseline configurations).
        *   Analyze if higher baseline CVs correlate with higher average CPU temperatures or more significant temperature fluctuations during the measurement periods.
    *   **Action Idea (Baseline Reproducibility & Cooldown):**
        *   Run extended baseline tests (0 defects) with the `h5_followup` script's high iteration/instance counts, perhaps with enforced cool-down periods between `NUM_INSTANCES_PER_COUNT` blocks, to see if baseline CV can be stabilized at a lower level.
        *   Re-run the *original* H5 script (with its lower iteration/instance counts) to assess the reproducibility of its low baseline CV under current system conditions.

2.  **Re-evaluate "Destabilization":**
    *   If the system's baseline is inherently more "noisy" (higher CV), then "destabilization" by defects might manifest not as an increase *above* baseline CV, but perhaps as a change in the *pattern* of CVs or a failure to *reduce* CV as much as other configurations.
    *   The current follow-up data, with its flat CVs for 1-4 lines, doesn't strongly point to a unique "destabilizing" signature for any specific low count in this regime.

3.  **Consider Absolute Standard Deviation:**
    *   Given the mean execution times do scale with defect count, it might be worth looking at the absolute standard deviation in addition to CV, though CV is generally preferred for comparing variability of measurements with different means.

4.  **Update Main Hypothesis Document:**
    *   The summary for H5 in `experiments/hypothesis_tests/hypotheses_from_ontology.md` will need to be updated to reflect these more nuanced findings and the questions raised by this follow-up, including the potential role of system variables like temperature.

This follow-up has provided valuable, more robust data, leading to a more complex picture than the initial H5 results suggested. The key now is to understand the baseline behavior better, potentially including environmental factors like CPU temperature.

## 7. H5 Re-confirmation Experiments with Thermal Management (Exp A & Exp B) - 2024-06-03

Following the insights from the `h5_followup_low_count_lines_test.py` (documented above), a new set of experiments (A and B) were designed to explicitly incorporate CPU temperature logging and to test two different thermal management strategies. The goal was to further investigate the stability of CV patterns and their potential correlation with thermal conditions.

These experiments used dedicated scripts:
*   `h5_exp_A_cooler_run.py`: Based on `h5_critical_destabilization_test.py` (lower iterations, cool-downs).
*   `h5_exp_B_hotter_run.py`: Based on `h5_followup_low_count_lines_test.py` (higher iterations, no cool-downs).
Both scripts logged CPU temperatures and precise work-phase timings, and saved primary results (Mean Exec Time, CV) directly to CSV files.

**Common Configuration Parameters (for A & B unless specified):**
*   `GRID_SIZE = 50`
*   `BASE_CELL_WORK_UNITS = 1`
*   `DEFECT_CELL_WORK_UNITS = 101`
*   `BUSY_WORK_ITERATIONS_PER_WORK_UNIT = 10000`
*   `LINE_DEFECT_COUNTS = [0, 1, 2, 3, 4, 5, 10]`

### 7.1 Experiment A: Cooler Run (with Cool-downs)

*   **Script:** `h5_exp_A_cooler_run.py`
*   **Configuration:**
    *   `NUM_ITERATIONS_PER_CONFIG = 5`
    *   `NUM_INSTANCES_PER_COUNT = 3`
    *   Cool-down Target: 45°C package temperature before each defect count test.
*   **Purpose:** To attempt to reproduce conditions of the original H5 experiment (where CV peaks were observed) but with active temperature management and logging.

**Results Summary (Exp A - Run 2, from automated CSV):**

| Defect Type   | Defect Count | MeanExec(ms) | CV       | Samples | PkgMin(C) | PkgMean(C) | PkgMax(C) | CoreMean(C) |
| :------------ | :----------- | :----------- | :------- | :------ | :-------- | :--------- | :-------- | :---------- |
| Baseline_Line | 0            | 996.415      | 0.028572 | 15      | 44.0      | 47.7       | 52.0      | 37.1        |
| Line          | 1            | 2906.480     | 0.001166 | 43      | 49.0      | 51.7       | 54.0      | 37.0        |
| Line          | 2            | 4801.256     | 0.001026 | 71      | 50.0      | 53.7       | 57.0      | 39.1        |
| Line          | 3            | 6836.900     | 0.001161 | 101     | 54.0      | 55.6       | 58.0      | 40.7        |
| Line          | 4            | 8631.637     | 0.017671 | 128     | 54.0      | 57.0       | 59.0      | 42.3        |
| Line          | 5            | 10459.709    | 0.006038 | 155     | 54.0      | 57.3       | 60.0      | 42.1        |
| Line          | 10           | 19474.025    | 0.005009 | 288     | 54.0      | 56.7       | 59.0      | 41.8        |

*Note: An earlier run of Exp A (with manually recorded results) showed a CV peak at Defect Count 2 (0.011039 at PkgMean 54.8°C). The run above (Run 2) is from automated CSV logging and shows different CV characteristics.*

**Analysis of Experiment A (Cooler Run - Run 2):**
1.  **Baseline CV:** The baseline CV (`0.028572`) was notably high in this run, suggesting underlying system variability.
2.  **CV Pattern:** The highest CV among defect configurations was for 4 line defects (`0.017671`). The CV for 2 line defects (`0.001026`) was very low, contrasting with the initial H5 findings and the first (manually logged) run of Experiment A.
3.  **Temperature:** Cool-downs were effective in reducing pre-test temperatures. However, package temperatures still rose to the mid-to-high 50s (°C) during tests. The `PkgMean(C)` for the CV peak at Defect Count 4 was 57.0°C.
4.  **Reproducibility:** The CV peak location was not consistent between the two informal runs of Experiment A, highlighting sensitivity to run conditions even with cool-downs.

### 7.2 Experiment B: Hotter Run (No Cool-downs)

*   **Script:** `h5_exp_B_hotter_run.py`
*   **Configuration:**
    *   `NUM_ITERATIONS_PER_CONFIG = 25`
    *   `NUM_INSTANCES_PER_COUNT = 10`
    *   No cool-down periods enforced.
*   **Purpose:** To observe system behavior and CV under sustained, higher thermal load.

**Results Summary (Exp B):**

| Defect Type   | Defect Count | MeanExec(ms) | CV       | Samples | PkgMin(C) | PkgMean(C) | PkgMax(C) | CoreMean(C) |
| :------------ | :----------- | :----------- | :------- | :------ | :-------- | :--------- | :-------- | :---------- |
| Baseline_Line | 0            | 973.134      | 0.006911 | 240     | 47.0      | 56.8       | 59.0      | 40.3        |
| Line          | 1            | 2939.290     | 0.010042 | 725     | 54.0      | 57.4       | 60.0      | 41.9        |
| Line          | 2            | 4873.739     | 0.009821 | 1203    | 54.0      | 57.8       | 60.0      | 42.4        |
| Line          | 3            | 6789.198     | 0.009251 | 1674    | 54.0      | 57.3       | 60.0      | 42.0        |
| Line          | 4            | 8730.416     | 0.008880 | 2153    | 54.0      | 57.7       | 60.0      | 42.2        |
| Line          | 5            | 10587.424    | 0.009075 | 2612    | 53.0      | 58.0       | 63.0      | 42.5        |
| Line          | 10           | 19701.837    | 0.015348 | 4859    | 53.0      | 58.7       | 69.0      | 43.6        |

**Analysis of Experiment B (Hotter Run):**
1.  **Baseline CV:** The baseline CV (`0.006911`) was moderate, lower than Exp A (Run 2) but higher than the original H5 baseline.
2.  **CV Pattern:** The highest CV (`0.015348`) occurred at 10 line defects, which was the highest workload and experienced the highest temperatures. CVs for other defect counts were relatively clustered.
3.  **Temperature:** The system ran significantly hotter. `PkgMean(C)` was consistently in the high 50s (°C), reaching 58.7°C for 10 defects. The `PkgMax(C)` for 10 defects was 69.0°C.
4.  **CV vs. Load/Temp:** In this hotter, sustained-load scenario, the highest CV aligned with the highest load and temperature, a more conventional expectation.

### 7.3 Combined Discussion and Implications for H5

These re-confirmation experiments (A and B) provide critical context to the original H5 findings and the earlier follow-up.

1.  **Reproducibility of CV Peaks:** The specific CV peaks observed in the original H5 experiment (e.g., at 1 and 4 defects, with a dip at 2 defects) were not consistently reproduced. Experiment A showed shifting peaks between its informal runs, and Experiment B showed a peak at the highest load (10 defects). This suggests that the precise location and magnitude of CV peaks can be highly sensitive to overall system state, thermal conditions, and potentially run-to-run variability.

2.  **Impact of Thermal Conditions:**
    *   **Cooler Run (Exp A):** Even with cool-downs, the system heated up during tests. The inconsistent CV peaks suggest that in this moderately "warm" and thermally cycled environment, different workloads might hit points of instability unpredictably. The high baseline CV in one run also complicates interpretation.
    *   **Hotter Run (Exp B):** Under sustained thermal load, the system behaved more predictably in one sense: the highest variability occurred at the highest load/temperature. This suggests that once the system is consistently hot, general thermal stress might become a more dominant factor in variability than subtle structural defect sensitivities.

3.  **Baseline CV is Critical:** The variability of the baseline CV across different experimental setups and runs is a major finding.
    *   Original H5: ~0.0015
    *   `h5_followup_low_count_lines_test.py`: ~0.0191
    *   Exp A (Run 2): ~0.0285
    *   Exp B: ~0.0069
    A "destabilizing" effect from defects can only be meaningfully interpreted relative to the baseline of *that specific experimental run and its conditions*. The high baselines in some runs make it difficult to claim that low-count defects are causing CV peaks "significantly higher than baseline" as originally hypothesized.

4.  **Revisiting H5 ("Critical Destabilization"):**
    *   The evidence for a *specific, low count* of line defects consistently causing a CV peak significantly above a stable, low baseline is weakened by these experiments.
    *   If "destabilization" occurs, it appears to be highly dependent on the thermal state and overall system noise. Under hotter, sustained conditions (Exp B), the "destabilization" (highest CV) shifted to the highest overall workload.
    *   The "Ontology Proponent" view (that specific structures interact uniquely with system state) is not strongly, or at least not simply, supported if the criterion is a fixed, reproducible CV peak at a specific low defect count irrespective of broader conditions. However, the *variability* of peaks in Exp A could be argued as evidence of complex interactions.
    *   The "Conventional View" (variability tied to general factors like thermal throttling, resource contention) seems to better explain Exp B's results. For Exp A, it would require more nuanced arguments about hitting specific performance cliffs unpredictably.

**Conclusions from Exp A & B:**
*   The phenomenon of sharp CV peaks at specific low defect counts, as seen in the initial H5 run, is not easily reproducible and appears highly sensitive to experimental conditions, especially thermal state and baseline system stability.
*   Sustained higher temperatures (Exp B) tend to result in the highest CV at the highest workload, aligning with more conventional expectations of system stress.
*   Understanding and stabilizing baseline CV is paramount for future investigations. The thermal logging and management introduced here are good steps.

### 7.4 Updated Next Steps (incorporating Exp A & B insights)

Previous "Next Steps" from section 6 remain relevant, but are augmented by these findings:

1.  **Deep Dive into Baseline CV:**
    *   **Systematic Baseline Tests:** Conduct multiple, extended baseline (0 defects) runs under both "Cooler" (with cool-downs) and "Hotter" (no cool-downs, but perhaps for a defined total duration) conditions. Log temperature and other system metrics (e.g., CPU frequency scaling, background processes) to identify factors contributing to baseline CV.
    *   **Controlled Environment:** If possible, minimize background tasks and ensure a more consistent starting state for each run.

2.  **Reproducibility Runs:** If a stable, low baseline can be achieved:
    *   Re-run a chosen configuration (e.g., the Exp A setup) multiple times (e.g., 3-5 times) to assess the statistical reliability of any observed CV patterns for specific defect counts.

3.  **Thermal Correlation Refinement:**
    *   With multiple runs, perform more detailed correlation analysis between various temperature metrics (min, mean, max, rate of change during work phase) and CV for each defect count.
    *   Consider if specific *temperature thresholds* or *rates of temperature increase* correlate with CV spikes, rather than just average temperatures.

4.  **Hypothesis Refinement for H5:**
    *   The original H5 formulation might need refinement. Instead of looking for fixed CV peaks, perhaps the hypothesis could explore conditions under which certain defect structures become *more susceptible* to thermal or other system stressors, leading to increased variability compared to other structures *under those specific stress conditions*.
    *   The concept of "destabilization" might be relative to the current operational regime of the system.

5.  **Explore Other Metrics (from original Next Steps):**
    *   Continue to consider absolute standard deviation if CV interpretation remains challenging due to baseline shifts.

These experiments (A & B) have significantly advanced the investigation by introducing thermal measurement and highlighting the complexity and sensitivity of the system. They emphasize the need for rigorous control and repeated measurements in drawing conclusions about subtle performance variations. 