# SPDX-License-Identifier: MIT

# Copyright (c) 2026 Oscar Montiel Ross

"""
Reproducibility script for the diagonal metadata illustration.

This script accompanies the manuscript:

```
An Effect-Algebraic Framework for Mediative Truth--Falsity Semantics
in Quantum Evidence Models
```

Author:
Oscar Montiel Ross

License:
The code in this script is released under the MIT License.
See the LICENSE file in this repository for the full license text.

Data notice:
This script uses a minimal preprocessed representation of selected
ZOD-derived metadata rows only to reproduce the illustrative semantic
calculations reported in the manuscript.

```
No raw ZOD sensor data, images, LiDAR, radar, video, trained perception
models, or personally identifying information are included in this
repository.

The original Zenseact Open Dataset (ZOD) remains governed by its own
license terms. Users should consult and cite the original ZOD source when
using or referencing ZOD-derived material.
```

Purpose:
Starting from zod_selected_preprocessed_rows.csv, this script recomputes:

```
    - the contextual-complexity index c;
    - the distance/proximity quantities D and r, when applicable;
    - the truth--falsity pair (mu_p, nu_p);
    - hesitation pi_p;
    - contradiction zeta_p;
    - the diagonal mediative value M_q(p,rho).

The computation is illustrative and reproducibility-oriented. It does not
train, validate, or benchmark an autonomous-driving perception model. It
also does not define a safety policy, a detector, or a decision rule.
```

"""

from **future** import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, Optional

INPUT_FILE = Path("zod_selected_preprocessed_rows.csv")
OUTPUT_FILE = Path("zod_mfl_recomputed_results.csv")

def clip(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
"""Clip a numeric value to the interval [lower, upper]."""
return max(lower, min(upper, value))

def parse_float(value: str) -> Optional[float]:
"""Parse an optional floating-point value from a CSV field."""
value = (value or "").strip()
if value == "":
return None
return float(value)

def round3(value: Optional[float]) -> str:
"""
Format a value to three decimals using standard half-up decimal rounding.

```
This avoids platform-dependent visual discrepancies for values such as
0.3445, which should be reported as 0.345 in the manuscript table.
"""
if value is None:
    return ""
rounded = Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
return f"{rounded:.3f}"
```

def compute_context_score(row: Dict[str, str]) -> float:
"""
Compute the contextual-complexity index

```
    c = 0.35*c_weather + 0.25*c_light + 0.20*c_road + 0.20*c_density.
"""
c_weather = float(row["c_weather"])
c_light = float(row["c_light"])
c_road = float(row["c_road"])
c_density = float(row["c_density"])

return (
    0.35 * c_weather
    \+ 0.25 * c_light
    \+ 0.20 * c_road
    \+ 0.20 * c_density
)
```

def compute_truth_falsity(row: Dict[str, str], c: float) -> Dict[str, Optional[float]]:
"""
Compute the illustrative truth--falsity pair and diagnostic quantities.

```
For rows with risk_indicator = 1, the preprocessed distance field is used
only to define a bounded proximity quantity. For rows with risk_indicator = 0,
no distance/proximity quantity is used.
"""
risk_indicator = int(row["risk_indicator"])
distance_m = parse_float(row.get("distance_m", ""))

if risk_indicator == 1:
    if distance_m is None:
        raise ValueError("Positive-risk rows require distance_m.")

    D = clip(distance_m / 10.0, 0.0, 1.0)
    r = 1.0 - D

    mu_p = 0.55 + 0.35 * r + 0.10 * c
    nu_p = 0.05 + 0.20 * D + 0.25 * c

else:
    D = None
    r = None

    mu_p = 0.10 + 0.30 * c
    nu_p = 0.60 + 0.25 * (1.0 - c)

pi_p = max(0.0, 1.0 - mu_p - nu_p)
zeta_p = max(0.0, mu_p + nu_p - 1.0)

M_q = (
    (1.0 - pi_p - zeta_p / 2.0) * mu_p
    + (pi_p + zeta_p / 2.0) * (1.0 - nu_p)
)

return {
    "D": D,
    "r": r,
    "mu_p": mu_p,
    "nu_p": nu_p,
    "pi_p": pi_p,
    "zeta_p": zeta_p,
    "M_q": M_q,
}
```

def build_evidence_pattern(row: Dict[str, str]) -> str:
"""Build the compact evidence-pattern text used for traceability."""
fields = [
row.get("reason_field", "").strip(),
row.get("weather", "").strip(),
row.get("time_of_day", "").strip(),
row.get("road_condition", "").strip(),
]
return "; ".join(field for field in fields if field)

def main() -> None:
if not INPUT_FILE.exists():
raise FileNotFoundError(
f"Cannot find {INPUT_FILE}. Run this script in the supplement folder."
)

```
rows_out = []

with INPUT_FILE.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        c = compute_context_score(row)
        computed = compute_truth_falsity(row, c)

        rows_out.append(
            {
                "case_id": row["case_id"],
                "split": row["split"],
                "frame_id": row["frame_id"],
                "risk_indicator": row["risk_indicator"],
                "evidence_pattern": build_evidence_pattern(row),
                "context_score_c": round3(c),
                "D": round3(computed["D"]),
                "r": round3(computed["r"]),
                "mu_p": round3(computed["mu_p"]),
                "nu_p": round3(computed["nu_p"]),
                "pi_p": round3(computed["pi_p"]),
                "zeta_p": round3(computed["zeta_p"]),
                "M_q_p_rho": round3(computed["M_q"]),
            }
        )

if not rows_out:
    raise ValueError(f"No rows were found in {INPUT_FILE}.")

fieldnames = list(rows_out[0].keys())

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print(f"Wrote {OUTPUT_FILE}")
print("Rounded values reproduced for the diagonal metadata illustration:")
for row in rows_out:
    print(
        f"Case {row['case_id']}: "
        f"split/frame={row['split']}/{row['frame_id']}, "
        f"c={row['context_score_c']}, "
        f"(mu_p,nu_p)=({row['mu_p']},{row['nu_p']}), "
        f"(pi_p,zeta_p)=({row['pi_p']},{row['zeta_p']}), "
        f"M_q(p,rho)={row['M_q_p_rho']}"
    )
```

if **name** == "**main**":
main()
