# Provenance of the reconstructed burden equations

Review date: 17 October 2026

Implementation reviewed: the contents of `src/blastdesign/burden.py` supplied by the project author after the v1.0.0 release checks.

This document traces the seven Python burden equations to the MSc thesis and records the extent of the external source checks. The implementations can be traced to the thesis equations and tables, including documented corrections. Verification against the original publications remains incomplete. The review also identifies differences between source conditions and the inputs accepted by the software.

This is an initial provenance audit. It does not change the equations, public API, compatibility baseline, reference scenario, evidence tiers, or saved numerical results. Findings below are review items, not changes already made to the software.

## Evidence recorded by this review

Four questions are kept separate:

1. **Implementation:** What expression, units, defaults, and branch rules does the current code use?
2. **Thesis reconstruction:** Where is that expression or table recorded in the thesis, and how were discrepancies resolved?
3. **Publication provenance:** Has the cited publication, its actual equation or table, and its conditions been inspected?
4. **Field validation:** Is there suitable observational evidence for the reconstructed implementation and intended application?

These questions are separate from the existing A/B/C applicability classifications. A bibliographic record confirms a publication's identity; it does not verify every coefficient. Agreement with a thesis example does not supply independent validation of the Python implementation.

The source review uses thesis section and equation/table identifiers. Page numbering varies between Word rendering and extracted versions, so unverified page numbers are not supplied. External records were checked on the review date. Where only an abstract, catalogue entry, or extracted reproduction was available, that limit is stated.

## Equation map

In this table, `d = hole_diameter_mm / 1000` is the diameter actually used by the Python functions, in metres; `B` is returned in metres. Let `q = explosive_density_g_cm3 / rock_density_g_cm3`.

| Model ID | Implemented relationship | Thesis locator |
|---|---|---|
| `CONV_ASH` | `B = K_B d` | Section 2-2-3, Eq. 2-4; Section 4-3, Eq. 4-1 |
| `CONV_BHANDARI` | `B = 24d + 0.85` | Section 2-2-4, Eq. 2-6; Section 4-3, Eq. 4-2 |
| `CONV_JIMENO` | `B = k d`, using diameter, strength and explosive branches | Section 2-2-5, Tables 2-3 and 2-4 |
| `CONV_KONYA_1972` | `B = 37.8d q^0.33` | Section 2-2-6, Eqs. 2-7 and 2-9; Section 4-3, Eq. 4-3 |
| `CONV_KONYA_1983` | `B = 12d(2q + 1.5)` | Section 2-2-6, Eqs. 2-8 and 2-10; compare Eq. 4-4 |
| `CONV_RUSTAN` | `B = 18.1d^0.689` | Section 2-2-7, Eq. 2-11; Section 4-3, Eq. 4-5 |
| `CONV_TATIYA` | `B = ad^2 + bd + c`, using ANFO strength classes | Section 2-2-8, Eq. 2-12 and Table 2-5; Section 4-3, Eq. 4-6 |

## Ash

Function: `ash_burden(hole_diameter_mm, burden_ratio=25.0)`.

The code implements thesis Eq. 2-4 and accepts `20 <= K_B <= 40`. The default is 25. It does not derive the coefficient from rock or explosive properties.

The thesis attributes the relationship to Ash's early work through Hustrulid (1999). Its Table 2-2 cites an ISEE web document, `BurdenRatio.doc`, accessed in 2009. These are the documented source chain; the original Ash article and the historical ISEE file have not been inspected in this review.

A later handbook coauthored by Konya gives an Ash expression using explosive charge diameter and describes developments in 1964 and 1968 [K]. The thesis's 1963 attribution therefore still requires an exact original citation. This is not evidence that the implemented linear expression is numerically incorrect.

The interval 20–40 is an implemented coefficient constraint. It is not a universal calibration domain or a rule for selecting a field coefficient.

## Bhandari and Vutukuri

Function: `bhandari_burden(hole_diameter_mm)`.

Thesis Eq. 2-6 explicitly assigns metres to both diameter and burden. The code follows that convention: the slope 24 is dimensionless and the intercept 0.85 has units of metres. The equivalent expression with diameter in millimetres is `B_m = 0.024 d_mm + 0.85`.

The thesis cites Bhandari's 1997 book [B] and identifies Bhandari and Vutukuri (1973) in a footnote. The originating 1973 publication and the relevant book page remain to be checked. Claims about the original sample size and calibration population should be attributed to the thesis until that check is complete.

The function accepts positive diameters without a source-domain upper or lower bound. Numerical acceptance is therefore broader than a demonstrated empirical applicability range.

## López Jimeno and coauthors

Function: `lopez_jimeno_burden(hole_diameter_mm, ucs_mpa, explosive_type="ANFO")`.

The source chain is the thesis Tables 2-3 and 2-4 to *Drilling and Blasting of Rocks* [J]. The book's publication identity has been located, but the complete original table headings, accompanying text, and charging assumptions have not been checked against an accessible original edition in this review.

The following intervals describe the code exactly. They should not be presented as newly established physical discontinuities.

| Diameter branch | UCS interval, MPa | Multiplier `k` |
|---|---|---:|
| `d_mm <= 165` | `UCS < 70` | 39 |
| `d_mm <= 165` | `70 <= UCS <= 120` | 37 |
| `d_mm <= 165` | `120 < UCS <= 180` | 35 |
| `d_mm <= 165` | `UCS > 180` | 33 |
| `d_mm > 180`, ANFO | `UCS < 70` | 28 |
| `d_mm > 180`, ANFO | `70 <= UCS <= 180` | 23 |
| `d_mm > 180`, ANFO | `UCS > 180` | 21 |
| `d_mm > 180`, emulsion or watergel | `UCS < 70` | 38 |
| `d_mm > 180`, emulsion or watergel | `70 <= UCS <= 180` | 32 |
| `d_mm > 180`, emulsion or watergel | `UCS > 180` | 30 |

The implemented diameter gap is **`165 < d_mm <= 180`**: 165 mm is accepted and 180 mm is rejected. The small-hole branch returns before checking `explosive_type`, so its current result is independent of that argument. The thesis's surrounding introduction describes small-hole blasting from 65 to 165 mm, whereas the function also accepts positive diameters below 65 mm. These distinctions should be documented before extending the applicability claims.

The exact assignment at shared strength-class endpoints, particularly 120 MPa, should be checked against the original table and its explanatory text. The table above records the existing software convention.

## Konya 1972

Function: `konya_1972_burden(hole_diameter_mm, explosive_density_g_cm3, rock_density_g_cm3)`.

The implementation follows the thesis metric expression, Eq. 2-9, including the exponent **0.33**. It reproduces that expression rather than replacing the exponent with one third.

The metric coefficient is consistent with conversion of the thesis imperial expression: converting burden from feet to metres and diameter from metres to inches multiplies 3.15 by 12, giving 37.8. Both densities must use compatible units and measurement definitions.

The Konya-authored FHWA handbook [K] gives a cube-root form, attributes it to 1972, and defines its diameter as explosive charge diameter. It supports the equation family, but does not independently verify the exact exponent `0.33` or the original 1972 publication. A cube root and exponent 0.33 are numerically different.

The Python input is hole diameter. Equating it to charge diameter assumes full radial coupling. Decoupled charges require separate treatment of that input definition; the current function has no decoupling parameter.

## Konya 1983

Function: `konya_1983_burden(hole_diameter_mm, explosive_density_g_cm3, rock_density_g_cm3)`.

Thesis Eq. 2-10 includes `2q`, while thesis Eq. 4-4 omits the factor 2. The Python implementation follows Eq. 2-10. This is an explicit reconstruction decision, also recorded in the earlier scientific audit notes.

At the reconstructed reference inputs, the implemented expression gives approximately 5.689716 m; omitting the factor gives approximately 5.103858 m. The thesis reference value of 5.69 m supports the chosen reconstruction. This is internal consistency evidence, not verification of the originating 1983 publication.

The coefficient 12 is consistent with the same feet/inches conversion used above. The exact 1983 publication, original variable definitions, any adjustment factors, and empirical conditions remain unresolved. The word "Verified" in the current function docstring should be read in the context of the documented reconstruction check, not as certification that every original-source condition has been audited.

## Rustan

Functions: `rustan_burden(hole_diameter_mm)` and `rustan_applicability(hole_diameter_mm)`.

The thesis prints millimetres beside Eq. 2-11, but the code uses metres. Its benchmark supports that reconstruction. The applicability helper records 89–311 mm; the numerical function itself accepts any positive diameter.

Rustan's 1992 paper [R] was checked through an extracted full-text reproduction, with publication identity corroborated by LTU. Section 4.3, Eq. 22 reports the implemented expression over **89–381 mm**, conflicting with the thesis. Its burden is normalized to spacing/burden equal to one; Section 4.2 defines that quantity using the square root of practical burden times practical spacing. The paper also assumes coupled charges.

This distinction affects interpretation of the seven-model comparison. The source scan should be visually checked before changing the applicability helper, diameter grid, or associated documentation. The v1.0.0 values remain unchanged by this review.

## Tatiya and Al-Ajmi

Functions: `tatiya_al_ajmi_coefficients(ucs_mpa)` and `tatiya_al_ajmi_burden(hole_diameter_mm, ucs_mpa, explosive_type="ANFO")`.

The code follows thesis Eq. 2-12 and Table 2-5:

| UCS interval, MPa | `a`, per metre | `b`, dimensionless | `c`, metres |
|---|---:|---:|---:|
| `UCS < 55` | -40 | 35.9 | 0.45 |
| `55 <= UCS <= 110` | -30 | 29.4 | 0.35 |
| `UCS > 110` | -20 | 24.1 | 0.30 |

The negative signs and decimal values are consistent with the thesis's Persian notation. Diameter must be in metres for these coefficient values. The function enforces ANFO but does not enforce a diameter interval.

The authors' university record for their 2000 article [T] identifies **25–304 mm**, ANFO, and tests at two Omani limestone operations. This verifies the publication record and reported study scope. The full article's coefficient table has not been inspected, so exact coefficient verification against that article remains open.

Published tests of the historical relationship do not constitute independent field validation of this Python reconstruction, its reference scenario, or its exploratory grids. Conversely, the absence of a project validation dataset should not be described as proof that the historical relationship was never tested in mines.

## Review items before changing numerical behaviour

| ID | Item | Next evidence needed |
|---|---|---|
| P01 | Rustan's published upper diameter differs from the thesis-derived helper | Inspect the original page image for Section 4.3/Eq. 22; review the helper, tests, grid rationale, and research text together |
| P02 | Diameter can mean charge diameter or hole diameter | Record the source definition for each equation and the coupling assumption used in comparisons |
| P03 | Tatiya diameter scope is not enforced by the function | Check the full article and decide how source applicability will be represented without silently changing the public numerical interface |
| P04 | Konya exponent 0.33 differs from a cube root | Identify the intended source edition and preserve the legacy expression unless a separately documented correction is justified |
| P05 | Several citations stop at a secondary source or publication record | Obtain exact pages/equation or table identifiers for Ash, Bhandari–Vutukuri, López Jimeno, and both Konya versions |
| P06 | Branch acceptance can exceed documented scenario coverage | Check small-hole charging assumptions, diameter limits, and endpoint conventions against the complete source tables |

A future correction should identify the affected source claim, retain the released v1.0.0 record, assess API compatibility, and regenerate affected numerical artifacts only when a numerical change has actually been made.

## References and access status

**[M] Thesis reconstruction source.** Mehregan, A. (formerly Choupankareh), 2010. MSc thesis on a computer model for drilling and blasting in open-pit mines, Imam Khomeini International University. Repository source: `docs/sources/A.Mehregan MSc Thesis at IKIU 2010 (full).docx`. Relevant locations: Sections 2-2-3 through 2-2-8 and 4-3; Eqs. 2-4 through 2-12 and 4-1 through 4-6; Tables 2-2 through 2-5. Thesis body text, equation text, and table entries were inspected; no claim of complete visual inspection is made.

**[B] Book cited by the thesis.** Bhandari, S., 1997. *Engineering Rock Blasting Operations*. A.A. Balkema. The relevant formula page and original 1973 reference still need inspection. This entry records the thesis citation, not a completed original-source check.

**[J] Book cited by the thesis.** López Jimeno, C., López Jimeno, E., and Ayala Carcedo, F.J., 1995. *Drilling and Blasting of Rocks*. A.A. Balkema. [Publisher record](https://www.routledge.com/Drilling-and-Blasting-of-Rocks/Jimeno-Jimeno-Carcedo/p/book/9781315141435). Exact table locations and full conditions remain to be checked.

**[K] Later author-coauthored reference.** Konya, C.J., and Walter, E.J., 1991. *Rock Blasting and Overbreak Control*. FHWA-HI-92-001. [USDOT record](https://rosap.ntl.bts.gov/view/dot/743); [FHWA text](https://www.fhwa.dot.gov/engineering/geotech/pubs/012844.pdf), historical discussion of burden equations, printed p. 352. The relevant indexed text was inspected; this is not a claim to have inspected the original 1972 or 1983 publications.

**[R] Original research publication.** Rustan, R. Agne, 1992. *Burden, spacing and borehole diameter at rock blasting*. International Journal of Surface Mining, Reclamation and Environment 6(3), 141–149. [DOI](https://doi.org/10.1080/09208119208944329); [LTU publication record](https://ltu.diva-portal.org/smash/record.jsf?pid=diva2:982260). Relevant extracted text: Sections 4.2–4.3, Eqs. 18 and 22; [reproduction inspected](https://www.scribd.com/document/383336301/Rustan-1992). Original page-image verification remains open.

**[T] Original research publication identified.** Tatiya, R.R., and Al-Ajmi, A., 2000. *Evaluation of the Atlas Copco relation between burden and blast-hole diameter and rock strength at bench blasting — a case study*. International Journal of Surface Mining, Reclamation and Environment 14(2), 151–160. [DOI](https://doi.org/10.1080/13895260008953310); [authors' university record](https://squ.elsevierpure.com/en/publications/evaluation-of-the-atlas-copco-relation-between-burden-and-blast-h/). Publication metadata and abstract inspected; full coefficient table not inspected.

The calculations remain subject to `RESEARCH_COMPARATOR_ONLY`. This provenance review supplies neither a calibrated uncertainty interval nor an operational burden recommendation.
