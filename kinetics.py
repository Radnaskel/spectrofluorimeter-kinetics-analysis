import sys
import statistics


def parse_file(filepath):
    """
    Reads the raw spectrofluorimeter .dat file.

    Expected file structure:
    - First line: LED switching times
    - Remaining lines: spectral table
      * first row of the table contains wavelength values
      * next rows contain time + intensities at each wavelength

    Parameters
    ----------
    filepath : str
        Path to the input .dat file.

    Returns
    -------
    switching_times : list of float
        Times at which LED excitation changes.
    spectra_table : list of str
        Raw lines of the spectral table.
    """
    # Open the file and split it into separate lines
    with open(filepath, 'r') as f:
        lines = f.read().split('\n')

    # The first line contains technical metadata including LED switching times.
    # In the original file format, useful switching times begin from column 4,
    # so we take elements [3:-1].
    switching_times = list(map(float, lines[0].split('\t')[3:-1]))

    # All remaining lines belong to the spectral table
    spectra_table = lines[1:]

    return switching_times, spectra_table


def extract_wavelengths(spectra_table):
    """
    Extracts wavelength values from the header row of the spectral table.

    Parameters
    ----------
    spectra_table : list of str
        Raw spectral table lines.

    Returns
    -------
    header : list of float
        Wavelength values corresponding to spectral columns.
    """
    # The first row of the spectral table contains wavelengths
    # The last element is ignored because it is empty in this file format
    header = list(map(float, spectra_table[0].split('\t')[:-1]))
    return header


def find_indices(wavelengths, target, tolerance=0.5):
    """
    Finds indices of wavelengths that fall within target ± tolerance.

    This is used to average intensity values around the desired emission peak,
    for example:
    - 520 ± 0.5 nm
    - 580 ± 0.5 nm

    Parameters
    ----------
    wavelengths : list of float
        All wavelength values from the spectral header.
    target : float
        Target wavelength.
    tolerance : float, optional
        Allowed deviation from the target wavelength.

    Returns
    -------
    list of int
        Indices of wavelength columns matching the specified interval.
    """
    return [
        i for i, wl in enumerate(wavelengths)
        if target - tolerance <= wl <= target + tolerance
    ]


def extract_intensity(values, indices):
    """
    Calculates the mean intensity for selected wavelength indices.

    Parameters
    ----------
    values : list of float
        One row of spectral data:
        first element is time, remaining elements are intensities.
    indices : list of int
        Indices corresponding to the target wavelength range.

    Returns
    -------
    int
        Mean intensity rounded down to integer.
    """
    # Select all intensities that belong to the target wavelength interval
    selected = [values[i] for i in indices]

    # Average them to reduce noise and represent the signal around the peak
    return int(statistics.mean(selected))


def process_data(switching_times, spectra_table, idx_520, idx_580):
    """
    Splits the experiment into 400 nm and 560 nm excitation segments,
    and extracts fluorescence kinetics at 520 nm and 580 nm.

    Logic of the experiment:
    - excitation alternates between 400 nm and 560 nm
    - switching moments are stored in switching_times
    - for each time point, we determine which excitation pulse it belongs to
    - then we store intensity values separately for 400 nm and 560 nm pulses

    Parameters
    ----------
    switching_times : list of float
        LED switching times.
    spectra_table : list of str
        Raw spectral table lines.
    idx_520 : list of int
        Column indices for 520 ± 0.5 nm.
    idx_580 : list of int
        Column indices for 580 ± 0.5 nm.

    Returns
    -------
    imp400 : dict
        Time points and intensities collected during 400 nm excitation.
    imp560 : dict
        Time points and intensities collected during 560 nm excitation.
    """
    # Containers for separated kinetics:
    # time + intensity at 520 nm + intensity at 580 nm
    imp400 = {"time": [], "i520": [], "i580": []}
    imp560 = {"time": [], "i520": [], "i580": []}

    # In the original dataset, useful alternation begins from switching_times[2]
    # This reproduces the logic of the initial working script.
    led_idx = 2

    # The experiment starts from the 400 nm excitation segment
    impulse = 400

    # Skip spectra_table[0] because it contains wavelengths, not data
    for row in spectra_table[1:]:
        # Parse one row of measurements into floats
        values = list(map(float, row.split('\t')[:-1]))

        # The first value in the row is time
        time = values[0]

        # Stop analysis after the chosen experimental time cutoff
        # This prevents processing parts of the file that are outside
        # the intended kinetics interval
        if time > 175:
            break

        # Extract mean intensities around 520 nm and 580 nm
        i520 = extract_intensity(values, idx_520)
        i580 = extract_intensity(values, idx_580)

        # Check whether the current time point still belongs
        # to the current excitation segment
        if time <= switching_times[led_idx]:
            # Save values according to the current excitation wavelength
            if impulse == 400:
                imp400["time"].append(time)
                imp400["i520"].append(i520)
                imp400["i580"].append(i580)
            else:
                imp560["time"].append(time)
                imp560["i520"].append(i520)
                imp560["i580"].append(i580)
        else:
            # If we have crossed the switching time,
            # move to the next segment and switch excitation label
            led_idx += 1
            impulse = 560 if impulse == 400 else 400

    return imp400, imp560


def save_csv(filename, times, intensities):
    """
    Saves one kinetics trace to a CSV file.

    Output format:
    time,intensity

    Parameters
    ----------
    filename : str
        Name of the output CSV file.
    times : list of float
        Time values.
    intensities : list of int
        Corresponding intensity values.
    """
    with open(filename, 'w') as f:
        for t, i in zip(times, intensities):
            f.write(f"{t},{i}\n")


def main():
    """
    Main function of the script.

    Workflow:
    1. Read input file path from command line
    2. Parse raw data
    3. Extract wavelength columns
    4. Find indices for 520 nm and 580 nm
    5. Separate data into 400 nm and 560 nm excitation segments
    6. Save extracted kinetics to CSV files
    """
    # Check that the user provided an input file
    if len(sys.argv) < 2:
        print("Usage: python kinetics.py data.dat")
        return

    # Input file path passed from command line
    filepath = sys.argv[1]

    # Read raw data and LED switching times
    switching_times, spectra_table = parse_file(filepath)

    # Read wavelength values from the header row
    wavelengths = extract_wavelengths(spectra_table)

    # Find columns corresponding to the required emission ranges
    idx_520 = find_indices(wavelengths, 520)
    idx_580 = find_indices(wavelengths, 580)

    # Extract kinetics for both excitation regimes
    imp400, imp560 = process_data(
        switching_times, spectra_table, idx_520, idx_580
    )

    # Save separated kinetics into individual CSV files
    save_csv("imp400_inten_520.csv", imp400["time"], imp400["i520"])
    save_csv("imp400_inten_580.csv", imp400["time"], imp400["i580"])
    save_csv("imp560_inten_520.csv", imp560["time"], imp560["i520"])
    save_csv("imp560_inten_580.csv", imp560["time"], imp560["i580"])


# Standard Python entry point:
# run main() only when the script is executed directly
if __name__ == "__main__":
    main()