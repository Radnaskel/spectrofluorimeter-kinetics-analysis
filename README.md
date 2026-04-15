# Spectrofluorimeter Kinetics Analysis

## Overview

This project provides a Python pipeline for processing time-resolved spectrofluorimeter data and extracting fluorescence kinetics under alternating LED excitation.

The analysis focuses on fluorescence emission at:

* **520 nm (green channel)**
* **580 nm (red channel)**

under alternating excitation:

* **400 nm excitation**
* **560 nm excitation**
  
---

## Experimental Setup

The experiment consists of alternating LED pulses with variable duration:

* 400 nm (blue excitation)
* 560 nm (green/yellow excitation)

### Data format

* First row: LED switching times
* Subsequent rows: spectral measurements over time

  * Column 1: time
  * Remaining columns: intensities across wavelengths

---

## Method

The processing pipeline:

1. Parses raw `.dat` spectrofluorimeter data
2. Extracts wavelength values
3. Identifies spectral regions:

   * 520 ± 0.5 nm
   * 580 ± 0.5 nm
4. Averages intensities within these ranges
5. Segments the time series based on LED switching
6. Outputs kinetics as CSV files

---

## Output

Generated files:

* `imp400_inten_520.csv`
* `imp400_inten_580.csv`
* `imp560_inten_520.csv`
* `imp560_inten_580.csv`

Each file contains:

```id="csvformat"
time, intensity
```

---

## Visualization

Kinetics were visualized using Jupyter Notebook.

## Example Results

![400 nm kinetics](imp400_plot.png)
![560 nm kinetics](imp560_plot.png)

---

## Interpretation

The observed fluorescence behavior is consistent with a **biphotochromic fluorescent protein exhibiting multiple emissive states**.

* **400 nm excitation** enhances the green-emitting state (~520 nm)
* **560 nm excitation** enhances the red-emitting state (~580 nm)

This suggests the presence of at least two chromophore states and light-dependent transitions between them.

---

## How to Run

```bash
python kinetics.py spectral_data.dat
```

---

## Acknowledgements

This project was developed with the assistance of AI tools, including ChatGPT, which was used to support code structuring and debugging.

All modeling decisions, analysis, and interpretations were performed by the author.
