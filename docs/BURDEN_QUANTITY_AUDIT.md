# Diameter and burden definition audit

Review date: 31 October 2026.

## Scope

The current evaluator supplies one hole-diameter input to seven reconstructed
equations. All results appear under `burden_m`. These software conventions do
not establish that the original sources use identical diameters, charging
conditions, or burden quantities.

## Evidence ledger

| Model | Diameter evidence | Burden definition and remaining work |
|---|---|---|
| Ash | The MSc thesis identifies hole diameter. The later FHWA handbook, printed p. 352, uses explosive charge diameter. | The original Ash burden convention and coefficient conditions remain to be checked. Record the intended source edition and any coupling assumption. |
| Bhandari–Vutukuri | MSc Eq. 2-6 identifies hole diameter in metres. | The originating source's practical/maximum/nominal burden convention remains unresolved. Inspect the cited book page and original publication. |
| Lopez Jimeno | MSc Tables 2-3 and 2-4 identify hole diameter. | Inspect the original table headings and surrounding text for burden, charging, geometry, adjustment, and branch conditions. |
| Konya 1972 | The MSc thesis and later FHWA handbook identify explosive charge diameter. | The code passes hole diameter and retains exponent 0.33. Verify the originating publication and its burden conditions; the later handbook is not a complete original-source audit. |
| Konya 1983 | The MSc equation shares the preceding charge-diameter context. | This is a thesis-context reading. Verify the original 1983 variable definitions and burden conditions; do not treat the handbook's 1972 definition as independent verification of this version. |
| Rustan | The existing source audit records borehole diameter and the 89–381 mm interval. | Eq. 18 defines normalized practical burden B_p1 = sqrt(B_p * S_p), and Eq. 22 estimates B_p1 for S/B = 1. Retain the documented 18.1/18.8 source discrepancy and establish any mapping to another burden target. |
| Tatiya–Al-Ajmi | The thesis and authors' institutional abstract identify blast-hole diameter. | The full coefficient table and precise burden convention remain unchecked. Record the ANFO condition and reported 25–304 mm study scope. |

## Interpretation

Existing ensemble statistics describe reconstructed formula outputs under the
recorded input convention. Equivalence to one identical operational burden
target has not been established across all seven original sources.
The spread may reflect equation differences and unresolved differences in
definitions or source conditions. Their contributions have not been separated.
The historical A/B/C tiers do not certify physical-quantity equivalence.

For a charge-diameter expression, substituting hole diameter supplies a full
radial-coupling diameter assumption. This does not establish complete
longitudinal loading, explosive performance, or applicability to decoupled charges.
Likewise, Rustan's normalized burden must not silently become a practical burden
for arbitrary spacing. A conversion requires documented definitions and inputs.

## Sources and limits

- MSc thesis: Sections 2-2-3 through 2-2-8, Eqs. 2-4 and 2-6 to 2-12,
  Tables 2-3 to 2-5. Recovered thesis text was inspected; complete visual
  inspection of the Word document is not claimed.
- Konya and Walter (1991), FHWA-HI-92-001, printed p. 352:
  [USDOT record](https://rosap.ntl.bts.gov/view/dot/743).
  Indexed equation text was checked on 31 October 2026; the original Ash,
  1972 Konya, and 1983 Konya publications were not newly visually inspected.
- [Rustan source audit](RUSTAN_SOURCE_AUDIT.md): supplied images of printed
  pp. 146–147, Eqs. 18 and 22, visually checked on 25 October 2026.
- [Tatiya and Al-Ajmi institutional abstract](https://squ.elsevierpure.com/en/publications/evaluation-of-the-atlas-copco-relation-between-burden-and-blast-h/):
  checked on 31 October 2026; the full coefficient table remains unchecked.
- [Model provenance review](BURDEN_MODEL_PROVENANCE.md): other source chains
  and outstanding evidence requests.

No equation, numerical artifact, historical tier, API schema, or release version
is changed by this documentation step. Original-source completion and target
harmonization remain open. The decision gate remains
`RESEARCH_COMPARATOR_ONLY`; this audit supplies no operational recommendation.
