# Scientific audit notes through Step 24.11

## Gole-Gohar benchmark inputs

- Hole diameter: 251 mm
- UCS used for table/piecewise models: 85 MPa
- Explosive: ANFO
- Explosive density: 0.85 g/cm³
- Rock density: 4.37 g/cm³

## Audited conventional burden outputs

| Model | Full-precision Python result (m) | Thesis table (m) |
|---|---:|---:|
| Ash | 6.275000 | 6.27 |
| Bhandari | 6.874000 | 6.87 |
| López Jimeno | 5.773000 | 5.77 |
| Konya (1972) | 5.527324 | 5.52 |
| Konya (1983) | 5.689716 | 5.69 |
| Rustan | 6.983189 | 6.98 |
| Tatiya–Al-Ajmi | 5.839370 | 5.84 |

## Resolved textual and equation inconsistencies

### Konya (1983)

Thesis Equation 2-10 includes the factor 2:

`B = 12 d (2 rho_e/rho_r + 1.5)`

Equation 4-4 omits that factor. The thesis benchmark of 5.69 m agrees with
Equation 2-10, so Equation 4-4 is treated as a transcription error.

### Rustan

The correct researcher is R. Agne Rustan. The earlier reconstructed registry
spelling `Roustan` was corrected to `Rustan`, with ID `CONV_RUSTAN`.

The text near thesis Equation 2-11 labels `d` as millimetres, but the equation
coefficient and 6.98 m benchmark require `d` in metres. The printed unit label
is therefore treated as an error. The documented thesis diameter range is
89–311 mm; values outside it are extrapolations.

### Tatiya–Al-Ajmi table

For ANFO:

| UCS (MPa) | a | b | c |
|---|---:|---:|---:|
| `<55` | -40 | 35.9 | 0.45 |
| `55–110` | -30 | 29.4 | 0.35 |
| `>110` | -20 | 24.1 | 0.30 |

Persian `40-` means `-40`; `9/35` is the decimal 35.9, not 9 divided by 35.
These coefficients are restricted to ANFO until additional sources or field
calibration justify other explosive types.

## Evidence caution

Internal agreement with thesis examples demonstrates faithful reproduction,
not independent predictive validation. The project must distinguish:

- source/equation verification;
- software implementation verification;
- independent field validation;
- calibrated predictive uncertainty.
