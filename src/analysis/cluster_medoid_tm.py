"""US-align average-length TM parser extracted from the MIT source snapshot."""
import re

def parse_average_length_tm(output):
    scores = [float(match.group(1)) for line in output.splitlines()
              if "average length" in line.lower()
              for match in [re.search(r"TM-score\s*=\s*([0-9.eE+-]+)", line)] if match]
    if len(scores) != 1 or not np.isfinite(scores[0]) or not 0 <= scores[0] <= 1:
        raise ValueError("US-align did not report one valid average-length-normalized TM-score.")
    return scores[0]
