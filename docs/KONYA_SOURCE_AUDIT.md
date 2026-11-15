# Konya equation and diameter source check

Review date: 15 November 2026. Repository baseline: `b962c6c`.

## Source inspected

Konya, C.J., and Walter, E.J. (1991), *Rock Blasting and Overbreak Control*,
FHWA-HI-92-001. [USDOT record](https://rosap.ntl.bts.gov/view/dot/743);
[official PDF](https://rosap.ntl.bts.gov/view/dot/743/dot_743_DS1.pdf).

Printed pp. 89, 91-93, 352-353 were visually inspected (PDF pages 108, 110-112,
371-372, counted from one). The downloaded PDF has 434 pages and SHA-256
`d9ba7e67ce3ec945b0866008aa0323471f95eee09605b441efe1a03cede16d5b`.
Its SHA-512 matched the checksum in the official repository record.

## Readings

| Printed page | Verified finding |
|---|---|
| 89 | Burden is distance to available relief when the hole fires. |
| 91, Eq. 6.2 | `B_ft = (2 SGe/SGr + 1.5) De_in`; `De` denotes explosive diameter. |
| 92, Example 6.2 | A 2.5-inch cartridge in a 3-inch hole, with specific gravities 1.3 and 2.6, gives 6.25 ft. |
| 93 | The density approximation does not distinguish all emulsion energy differences. |
| 352-353 | The historical discussion gives the 1972 cube-root form and attributes Eq. 6.2 to Konya's 1983 development. |

## Project decisions

The linear implementation and its factor two are supported by this later,
author-coauthored source. The originating 1983 publication has still not been
inspected. That remaining bibliographic gap does not negate this source check.

The legacy `hole_diameter_mm` parameter and the shared reference scenario remain
unchanged. The comparator's equal-diameter assumption is now explicit in both
Konya docstrings. No geometry conversion or decoupling model is added. Reproducing
the published worked example requires its charge diameter, as the new regression
test makes explicit; its expected metric result is 1.905 m.

The 1972 exponent remains 0.33 to preserve the released reconstruction. This
review does not replace it with an exact cube root, rename an argument, recapture
the API baseline, alter saved results, or change historical tiers.

A published worked-example check verifies transcription and unit handling; it
does not establish site-specific predictive accuracy. The other source targets
still need harmonization. `RESEARCH_COMPARATOR_ONLY` remains in force.
