# PHASE 1 — STRUCTURAL CONCEPT DEVELOPMENT
## INSDAG NACS (C) 2026 — Fuel Station Canopy, Visakhapatnam

| Item | Value |
|---|---|
| Document | Phase 1 Structural Concept (Rev 01) |
| Basis | Phase 0 audit (`00_Phase0_Document_Audit.md`). Defaults confirmed by the team on 07-Oct-2026: structure inside the 750 mm envelope, soffit included, terrain category 2, k4 = 1.15, SBC 150 kN/m², M30, STAAD.Pro |
| Calculations | `calc/prelim/phase1_concepts.py` (2D frame solver + IS 800 preliminary checks), `phase1_compare.py`. Results in `docs/phase1_results.json` and `docs/phase1_comparison.json` |
| Figures | `docs/figs/fig1_scheme_alternatives.png`, `fig2_selected_scheme_layout.png`, `fig3_selected_scheme_iso.png` |
| Status | **Concept for approval. Preliminary sizing only. Not a final design.** |

> Every load value in this phase is tagged **[PRELIM]**. It was chosen conservatively so that schemes can be compared fairly, and will be re-derived from the IS 875-3:2015 tables in Phase 3. No member size here is final.

---

## 1. DESIGN OBJECTIVE

Find the structural system that best satisfies the brief, which asks for the "most economical and efficient scheme" (P4). Comparing it on evidence against at least two genuine alternatives under identical loads, geometry and criteria.

## 2. INPUT DATA AND SOURCE

### 2.1 Fixed constraints (cannot change)

| Constraint | Value | Source |
|---|---|---|
| Plan | 16.0 × 12.0 m | [OFFICIAL] P4, P8 |
| Column grid | 9.0 m (x) × 5.0 m (y), 4 columns at (3.5, 3.5), (12.5, 3.5), (3.5, 8.5), (12.5, 8.5) | [OFFICIAL] P8 |
| Overhang | 3.5 m on all sides from column CL; corner cantilever diagonal 4.95 m | [OFFICIAL] P4, P8 |
| Clear height | 6.25 m to underside of soffit/cover sheet | [OFFICIAL] P4 |
| Envelope | Whole roof structure within the 750 mm façade depth → top of fascia +7.00 m | [OFFICIAL] P4 + decision A1 |
| Circulation | No column or bracing in the 7.0 m drive between islands, nor across the drive lanes | [OFFICIAL] P8 |
| Steel | E250A minimum; IS 808 / IS 4923 / IS 1161 sections | [OFFICIAL] P5, P6 |
| Roof system | Beams/trusses on steel columns | [OFFICIAL] P4 Sl 4 |

### 2.2 Flexible parameters (ours to optimise)
Member type and orientation; primary/secondary hierarchy; roof slope and drainage direction (within the envelope); column section shape; base fixity; connection type (bolted/welded); splice positions; steel grade above E250A.

### 2.3 Coordinate system used throughout
x runs along the 16 m length and y along the 12 m width; the origin is at a canopy corner. z is measured from FFL.

---

## 3. PRELIMINARY LOAD BASIS [PRELIM]

### 3.1 Wind (governs; see 3.4)

| Step | Value | Basis |
|---|---|---|
| Vb | 50 m/s | IS 875-3:2015 Annex A, Visakhapatnam [PRELIM: verify] |
| k1 (risk, 50 yr) | 1.00 | IS 875-3 Table 1 [PRELIM] |
| k2 (TC2, h ≤ 10 m) | 1.00 | IS 875-3 Table 2 [PRELIM] |
| k3 (flat) | 1.00 | A7 |
| k4 (cyclonic, post-cyclone serviceability) | 1.15 | A8 (team approved) |
| Vz = Vb k1 k2 k3 k4 | **57.5 m/s** | — |
| pz = 0.6 Vz² | **1.984 kN/m²** | IS 875-3 cl. 5.4 |
| pd = Kd Ka Kc pz | **1.984 kN/m²** | Kd = 1.0 (cyclonic), Ka = Kc = 1.0 (no reduction taken: conservative) [PRELIM] |
| Roof net overall Cp | **−1.3 (uplift) / +0.5 (down)** | Free-standing canopy, solid blockage under the canopy (dispensers, vehicles) [PRELIM: replace with IS 875-3:2015 canopy table values] |
| Local net Cp (purlins/sheet) | ±1.8 | Edge zones [PRELIM] |
| Fascia Cf | 2.0 on one face area | Windward + leeward fascia combined [PRELIM] |
| Column Cf | 0.8 (CHS), 2.0 (I/RHS) | [PRELIM] |
| Friction (top + soffit) | 0.03 × pd × 192 m² = 11.4 kN | [PRELIM] |
| **WL uplift** | **−2.58 kN/m²** | −1.3 × 1.984 |
| **WL downward** | **+0.99 kN/m²** | +0.5 × 1.984 |

### 3.2 Gravity

| Load | Value | Status |
|---|---|---|
| Roof sheet + soffit sheet + services | 0.06 + 0.06 + 0.10 = 0.22 kN/m² | [ASSUMPTION] |
| Steel self-weight | Iterated from each scheme's own steel (0.43–0.65 kN/m²) | Calculated |
| Fascia line load | 0.25 kN/m around the 56 m perimeter | [ASSUMPTION] |
| Roof imposed (no access, maintenance only) | 0.75 kN/m² | IS 875-2 [PRELIM: verify table] |

### 3.3 ULS area loads (IS 800 Table 4), Scheme C example (DL = 0.68 kN/m²)

| Combination | Factored load |
|---|---|
| 1.5 (DL + LL) | 1.5 (0.68 + 0.75) = 2.15 kN/m² ↓ |
| 1.2 (DL + LL + WL↓) | 1.2 (0.68 + 0.75 + 0.99) = **2.91 kN/m² ↓** (gravity governs) |
| 1.5 (DL + WL↓) | 1.5 (0.68 + 0.99) = 2.51 kN/m² ↓ |
| 0.9 DL + 1.5 WL↑ | 0.9 × 0.68 − 1.5 × 2.58 = **−3.26 kN/m² ↑** (uplift governs) |

Taking roof live load concurrently with full wind in 1.2(DL + LL + WL) is conservative. The final combination set comes in Phase 3.

### 3.4 Key finding: wind uplift governs this structure
- The factored **net uplift (3.26 kN/m²) is larger than the factored gravity load (2.91 kN/m²)**. The total ULS uplift is ≈ 3.26 × 192 = **626 kN**, about 156 kN of tension per column.
- **Every connection must transmit tension.** That includes the purlin cleats, girder seats, column caps, base plates and anchors. The footings are sized by uplift and overturning, not by bearing.
- **Stress reversal:** the flange that is in tension under gravity goes into compression under uplift. Every member's lateral-torsional buckling check must cover both flanges.
- **Seismic (preliminary):** taking Zone II (Z = 0.10), I = 1.0, R = 3 and Sa/g = 2.5 gives Ah = 0.042. With seismic weight W ≈ 0.68 × 192 + 0.25 × 56 ≈ 145 kN, the base shear is Vb ≈ **6 kN**. Service wind horizontal is 60–75 kN. Even with R = 1.5 and I = 1.5, Vb ≈ 18 kN. **Wind governs lateral design by a factor of more than 3.** Seismic will be shown but will not control. [PRELIM: verify zone, R and I in Phase 3]
- **Temperature (15 °C):** the free expansion between columns is 12×10⁻⁶ × 9000 × 15 = **1.6 mm**. The tall, flexible columns absorb this at negligible force, so no expansion joint is needed. This is confirmed numerically in Phase 4.

### 3.5 Serviceability targets (project decision; stricter than IS 800 Table 6 elastic-cladding values)

| Member | Target | Reason |
|---|---|---|
| Spans | L/300 | Flat soffit and branding fascia must stay visually straight |
| Cantilevers | L/150 | Same |
| Purlins | L/180 | Same |
| Column drift | H/150 | IS 800 Table 6 value for columns with elastic cladding [verify] |

Deflection was checked under wind alone (2.58 kN/m²), which exceeds live load (0.75 kN/m²).

---

## 4. CONSTRAINTS THAT SHAPE THE CONCEPT

1. **Four columns only, on the island lines.** Vertical bracing is impossible across the drives. In the island plane it would clash with the dispensers and hoses. **Lateral stability must come from moment frames and fixed-base columns.**
2. **750 mm envelope.** The structure, purlins, sheet, soffit **and the drainage fall** must all fit inside it. Any depth spent on packers for the fall is depth taken from the main members.
3. **Balanced cantilevers.** With a 9.0 m span and 3.5 m overhangs, the hogging moment at the support is wa²/2 = 6.125w and the midspan sagging moment is wL²/8 − wa²/2 = 4.0w. That is close to the ideal balance (L = 2√2·a = 9.9 m). Continuous members over the columns are therefore very efficient in x. In y (5.0 m span), the whole member is in hogging (−6.125w at the supports, −3.0w at midspan).
4. **Corner cantilevers (3.5 × 3.5 m).** These deflect by both the x- and y-cantilever actions together. They will govern serviceability.
5. **Live fuel station (constructability).** Site welding is hot work and needs special permits at an operating fuel station. **All site connections will be bolted.**

---

## 5. CONCEPTS SCREENED OUT AT STAGE 0

| Concept | Why rejected |
|---|---|
| D. Double-layer space frame with proprietary ball nodes (MERO-type) | Node systems are proprietary, so their design is not to IS 800 connection rules and cannot be submitted fully. At 750 mm depth the module is ~0.6 m, which means hundreds of nodes and members. High cost, and P6 asks for "beams/trusses" |
| E. Branched "tree" columns with struts below the roof | The struts would sit below +6.25 m and violate the clear-height requirement around the islands. Branches near vehicles also create an impact risk |
| F. Deep trusses projecting above the roof | Violates the 750 mm envelope (A1). Visible structure above the fascia also defeats the flat branding band |
| G. Mast and tie-rod (cable-stayed) canopy | Masts project above the roof (envelope). Tie rods slacken under uplift, which governs here, so a stiff compression system would be needed anyway. Cables at a coastal site raise durability and inspection concerns |
| H. Fixed-base cantilever columns + single-direction girders only | Studied as C-0 below. It works, but its columns are 59% heavier than C-1's because of x-direction drift |

---

## 6. THE THREE SCHEMES

See **Figure 1** (`docs/figs/fig1_scheme_alternatives.png`).

### SCHEME A — Conventional rolled-I two-way grillage
- **Primaries:** 2 × ISMB girders along x on the column lines (16 m, continuous, spliced).
- **Secondaries:** 9 × ISMB beams along y at ≤ 2.25 m, flush top and bottom with the primaries, so they are cut and moment-spliced across each primary (cover plates top and bottom).
- **Purlins:** RHS along x at 1.2 m, on **tapered packers of up to 225 mm** to create the drainage fall.
- **Columns:** wide-flange I (WPB/ISHB), moment-connected in both directions. These are two-way moment frames.
- **Load path:** sheet → purlin → secondary (y) → primary (x) → column → base.

### SCHEME B — Shallow tubular truss grid
- **Primary trusses:** 2 along x on the column lines. Secondary trusses: 9 along y at ≤ 2.25 m. All are SHS Warren trusses about 0.5 m deep, flush, with the top chords following the roof fall.
- **Columns:** CHS, moment-connected through the chords in both directions.
- **Load path:** the same as A, but members work by axial force (chord couple) instead of bending.

### SCHEME C — Tapered "tree-girder" canopy with continuous RHS purlin-beams (hybrid)
- **TG1, TG2 (primary):** 2 transverse welded plate girders along y, one on each column pair. Each is **moment-shaped (tapered)**: 400 mm deep at the column (where the moment peaks), 450 mm at the ridge and 225 mm at the cantilever tip (where the moment is zero). The sloping top flange **forms the roof fall itself**, so no packers are needed and the soffit stays flat.
- **LB1–LB11 (secondary = purlin):** continuous RHS purlin-beams along x at 1.2 m. They **bear on top of the TGs** and span 9.0 m with 3.5 m cantilevers each end, exploiting the balanced-cantilever geometry. They are spliced at the **points of contraflexure** (~1.67 m from the supports), where moments are near zero. That gives simple splices and 5–6 m transport pieces.
- **HB1, HB2:** 2 moment-connected head beams (RHS) between the column heads along x. They turn the x-direction free cantilevers into fixed-base portals, which halves the column moments, reduces drift and adds two-way robustness. Variant C-0 without them is reported for comparison.
- **C1–C4:** CHS columns, fixed base. Equal stiffness in every direction, low wind drag, and they **house the rainwater downpipes** in a protective sleeve.
- **Fascia:** posts and girts on the LB tips (short sides) and on the eaves LBs (long sides). The eaves LB doubles as the edge member, giving a continuous flat branding surface.
- **Load path:** sheet → LB (purlin-beam) → TG (bearing cleats, tension-capable) → column capital → CHS column → base plate → anchors → pedestal → footing → soil. Only **two levels of hierarchy**, against three in A and B.

---

## 7. PRELIMINARY SIZING RESULTS (identical loads and criteria for all schemes)

Method: each member was analysed with the 2D direct-stiffness solver (`frame2d.py`, validated against closed-form results: wL²/8, 5wL⁴/384EI and PL³/3EI all exact). Each was checked to IS 800:2007 for bending with lateral-torsional buckling (Annex E Mcr), shear, axial + bending (conservative linear interaction) and deflection. The lightest passing section was selected. Self-weight was iterated to convergence.

### 7.1 Scheme A

| Mark | Section | Governing | Util. (strength) | Deflection ratio |
|---|---|---|---|---|
| Purlin | RHS 96×48×3.2 (span 2.25 m) | Strength/defl. | 0.38 | 0.15 |
| Secondary | ISMB 300 (ISMB 250 end lines) | **Deflection, depth-capped at 334 mm** | 0.37 | 0.79 |
| Primary | ISMB 300 | Strength, depth-capped | 0.91 | 0.67 |
| Columns | WPB 300×300 (HE300B), 117 kg/m | Weak-axis bending in the y-frame | 0.65 | drift 39/43 mm |
| Footing | 2.55 m sq. × 0.6 m at 1.5 m depth | Overturning/uplift | FOS 1.61/2.05 | — |

### 7.2 Scheme B

| Mark | Section | Governing | Util. | Deflection ratio |
|---|---|---|---|---|
| Purlin | RHS 96×48×3.2 | — | 0.38 | 0.15 |
| Secondary trusses | Chords SHS 60–72×3.2, webs SHS 40×3.2, D = 509 | Chord force / deflection | 0.67–0.89 | 0.84–0.94 |
| Primary trusses | Chords SHS 91.5×4.5, webs SHS 40×3.2 | Chord compression | 0.90 | 0.49 |
| Columns | CHS 323.9×6.3 | Drift | 0.79 | 37/44 mm |
| Footing | 2.45 m sq. | Overturning | FOS 1.56 | — |
| Welded nodes | **≈ 634** shop nodes | — | — | — |

### 7.3 Scheme C (C-1 with head beams; C-0 without)

| Mark | Section | Governing | Util. | Deflection |
|---|---|---|---|---|
| LB1–LB11 | **RHS 200×100×4** | **Deflection, span 29.2 mm vs 30.0 mm (L/300)** | 0.56 | 0.97 |
| TG1, TG2 | Welded tapered I: flanges 250×12, web 6; D = 225 / 400 / 450 | **Cantilever tip deflection, 22.5 mm vs 23.3 mm** | 0.56 | 0.96 |
| HB1, HB2 | RHS 250×150×6 | Portal action | — | — |
| C1–C4 | **CHS 323.9×6.3** (C-0: CHS 406.4×8) | Drift 42.1/43.4 mm; interaction 0.94 | 0.94 | 0.97 |
| Footing | **2.50 m sq.** (C-0: 2.75 m) | Overturning, FOS 1.61; uplift FOS 1.91 | — | — |
| Envelope stack at the ridge | 60 + 450 + 200 + 35 = **745 mm ≤ 750** | — | — | — |

**Engineering interpretation:** in every scheme the members are **stiffness-governed**, at strength utilisation of only 0.4–0.6. So **E250A is the right grade**: a higher grade adds cost without adding stiffness, since E does not change. Steel efficiency comes from **depth**, which is why the scheme that wastes the least envelope depth wins.

---

## 8. QUANTITIES AND RELATIVE COST

All weights include the common items: fascia frame 497 kg, soffit runners 792 kg and roof bracing 250 kg. They also include a connection/base-plate allowance of 10% (A), 15% (B) or 8% (C).

| | **A** Rolled-I grillage | **B** Truss grid | **C-0** | **C-1 (selected)** |
|---|---:|---:|---:|---:|
| Total structural steel | 12.81 t | **8.49 t** | 9.07 t | 8.99 t |
| Steel per m² of canopy | 66.7 kg/m² | **44.2 kg/m²** | 47.2 kg/m² | 46.8 kg/m² |
| Shop-welded truss nodes | 0 | ≈ 634 | 0 | **0** |
| Site bolted joints (approx.) | 135 | 127 | 48 | **52** |
| Erection pieces (main) | 57 | 39 + grid assembly | 39 | 41 |
| Footing size / total RCC | 2.55 m / 18.0 m³ | 2.45 m / 16.8 m³ | 2.75 m / 20.5 m³ | 2.50 m / 17.4 m³ |
| **Relative cost index (A = 100)** | 100 | 84.8 | 80.2 | **77.7** |

**Cost-index assumptions [ASSUMPTION; no market prices used].** Cost is expressed as kg of fabricated-and-erected rolled steel:

| Item | Factor |
|---|---|
| Rolled sections | 1.00 |
| Hollow sections | 1.10 (material premium) |
| Welded tapered plate girder (PEB automated line) | 1.20 |
| Tubular truss work (manual fit-up and node welding) | 1.60 |
| Connection plates and bolts | 1.50 |
| 1 m³ RCC footing | 90 kg-equivalent |

These ratios will be replaced by dated CPWD DSR / AP SSR rates in Phase 6.
**Sensitivity:** Scheme B only matches C-1 if truss fabrication costs ≤ **1.28×** rolled work per kg. That is unrealistic for ~634 hand-fitted SHS nodes.

---

## 9. WEIGHTED DECISION MATRIX

Scores run from 1 (poor) to 5 (best). Quantitative criteria are scored from Section 8; qualitative ones carry their reasons.

| Criterion | Weight | A | B | C-1 | Basis of score |
|---|---:|---:|---:|---:|---|
| Structural efficiency | 12 | 2 | 4 | 4 | A: depth lost to packers, members at 0.3–0.4 utilisation, weak-axis columns. B: axial action. C: girder depth follows the moment diagram; 2-level hierarchy |
| Steel weight | 12 | 1 | 5 | 4.5 | 12.81 / 8.49 / 8.99 t (linear scale) |
| Wind/uplift performance | 12 | 3 | 3 | 4 | B: thin 3.2 mm chords buckling under reversal, many members to check. C: closed RHS purlin-beams (no LTB), TG compression flange restrained by LBs at 1.2 m, short tension load path |
| Economy (cost index) | 15 | 2 | 4 | 5 | 100 / 84.8 / 77.7 |
| Constructability | 12 | 3 | 2 | 5 | C: 2 TGs, 4 columns, 2 HBs, 33 LB pieces, all bolted on site. B: 634 nodes, tolerance-critical grid assembly at height. A: 18 moment splices across girders |
| Connections | 8 | 2 | 1 | 4 | Site joints 135 / 127 + nodes / 52, repetitive and simple |
| Foundation | 6 | 3 | 4 | 3.5 | 18.0 / 16.8 / 17.4 m³. Uplift-governed, so similar for all |
| Aesthetics and branding | 8 | 2 | 4 | 5 | C: flat soffit, slim fascia, round columns with concealed downpipes. A: exposed H-columns |
| Coastal durability | 9 | 3 | 2 | 4 | B: hundreds of weld nodes and 3.2 mm walls are defect and crevice sites. C: few joints, sealed closed sections, ≥ 4 mm walls |
| Innovation (measurable) | 6 | 1 | 3 | 4 | See Section 10.3 |
| **Weighted score (out of 100)** | **100** | **44.2** | **65.6** | **87.6** | Σ(w·s)/5 |

**Robustness of the ranking:** C-1 stays first unless steel weight alone is given more than ~45% of the total weight, or truss fabrication costs ≤ 1.28× rolled work.

---

## 10. SELECTED SCHEME: C-1 "Tapered tree-girder canopy"

See **Figure 2** (layout and sections) and **Figure 3** (isometric).

### 10.1 Why it is expected to outperform the alternatives (evidence)
| Claim | Evidence (this phase) |
|---|---|
| 30% less steel than the conventional rolled-I solution | 8.99 t vs 12.81 t (Section 8) |
| Lowest overall cost index | 77.7, against 84.8 (B) and 100 (A) |
| Near-truss weight without truss fabrication | +0.50 t (+6%) vs B, but **0 vs 634** welded nodes and **52 vs 127** site joints |
| Uses the full envelope depth | Girder depth 400–450 mm vs 334 mm in A (+20 to +35%, and stiffness ∝ D²), because the fall is built into the girder, not added as packers |
| Two-way lateral robustness | x: HB portals; y: TG portals. Against C-0, the HBs add 0.69 t but save 0.76 t of column steel (net −0.07 t) and 3.1 m³ of footing concrete, and cut column moment by 43% |
| Every member directly checkable by hand | Statically simple: LB is a 2-support beam with overhangs; TG is a 2-column portal |

### 10.2 Structural system

| Element | Marks | Function |
|---|---|---|
| Columns | C1–C4 (CHS) | Gravity + uplift tension; fixed-base cantilevers/portals for lateral load; downpipe sleeves |
| Primary girders | TG1, TG2 (tapered welded I) | Carry LB reactions to the columns; y-direction portal beams; form the drainage fall |
| Head beams | HB1, HB2 (RHS) | x-direction portal beams; tie the column heads; robustness |
| Purlin-beams | LB1–LB11 (RHS) | Support the sheeting and span between the TGs; LB1/LB11 are the long-side edge members |
| Fascia frame | FP (posts), FG (girts) | Flat 750 mm branding surface; wind on the fascia |
| Soffit runners | SR | Soffit sheet support |
| Roof plan bracing | RB (rods/angles) | Delivers x-direction fascia/friction load from the LBs to the column heads without weak-axis bending of the TG top flange |
| Base | BP + AB (grade ≥ 4.6, IS 5624), pedestal, isolated footing | Moment + tension + shear to the ground |

### 10.3 Innovation, each with a measurable benefit
1. **Moment-shaped girder with integral drainage.** The girder depth follows the bending-moment diagram (225 → 400 → 450 mm), and its top flange is the roof fall. This recovers 66–116 mm of structural depth compared with prismatic beams on packers (Scheme A), and removes all packers.
2. **Balanced-cantilever continuous purlin-beams spliced at contraflexure.** The splices sit where the moment is ≈ 0, so they are light, simple splices (which also gives the brochure's mandatory splice detail a reason to exist). Transport lengths are ≤ 6 m.
3. **Column-head portals (HB).** Measured benefit vs C-0: −43% column moment (173 → 98 kNm), CHS 406.4×8 → 323.9×6.3, footing 2.75 → 2.50 m (−3.1 m³ RCC), with a net steel change of −0.07 t. The main gain is robustness: both directions become frames.
4. **CHS column as a downpipe sleeve.** No external downpipes for vehicles to hit, and the low drag coefficient (0.8 vs 2.0) reduces wind on the columns by 60%.
5. **All-bolted site assembly.** No hot work in a live fuel station.

### 10.4 Lateral stability system
- **y-direction:** 2 fixed-base portals (TG + 2 columns each).
- **x-direction:** 2 fixed-base portals (HB + 2 columns each).
- **Roof plane:** plan bracing (RB) collects the fascia and friction loads and delivers them to the four column heads. The roof acts as a horizontal truss-diaphragm for torsion.
- No vertical bracing anywhere, so circulation is unobstructed.

### 10.5 Load paths
- **Gravity:** sheet → LB → TG seat → column capital → CHS column → base plate (bearing) → pedestal → footing → soil.
- **Uplift:** sheet fixings (tension) → LB → **TG seat bolts in tension** → capital → column in tension → **anchor bolts in tension** → pedestal/footing **self-weight + soil wedge** → equilibrium.
- **Lateral (x):** fascia → LB tips (axial) → plan bracing → column heads → HB-column portals → base moment + shear → anchor bolts and footing (overturning).
- **Lateral (y):** fascia → eaves LB → plan bracing / TG → TG-column portals → base moment + shear → footing.

---

## 11. VERIFICATION (Level 1 hand checks of the software)

| Check | Hand calculation | Program | Status |
|---|---|---|---|
| Design pressure | pz = 0.6 × 57.5² = 1983.75 N/m² | 1.984 kPa | ✓ |
| LB midspan deflection | δ = wL²(5L² − 24a²)/(384EI) = 3.095 × 81 × (405 − 294)/(384 × 2480) = 29.2 mm | 29.21 mm | ✓ |
| TG root moment (uplift) | w = 3.26 × 8.0 = 26.0 kN/m; M = 26.0 × 3.5²/2 = 159 kNm; Md(400 deep) = Zp fy/γm0 = 1.376×10⁶ × 250/1.1 = 313 kNm → 0.51 | 0.556 (includes LTB reduction) | ✓ |
| Total ULS uplift | 3.26 × 192 = 626 kN → 156 kN per column | N_min = −165 kN (adds lateral overturning) | ✓ consistent |
| Fascia + friction + column wind (x) | 2.0 × 1.984 × 0.75 × 12 + 11.4 + 4 × 0.8 × 1.984 × 0.324 × 6.25 = 60.0 kN | 59.98 kN | ✓ |
| Frame solver | Simply-supported beam wL²/8, 5wL⁴/384EI; cantilever PL³/3EI | Exact | ✓ |

---

## 12. RISKS AND OPEN ITEMS CARRIED TO PHASE 2

| # | Item | Action |
|---|---|---|
| R1 | **Corner deflection:** TG tip 22.5 + LB cantilever 11.1 = 33.6 mm, against 4950/150 = 33.0 mm (1.02) | Phase 2: stiffen the TG tip or make the eaves edge member work two-way. Confirm in the 3D model |
| R2 | Wind coefficients are preliminary (Cp −1.3/+0.5, fascia 2.0, Ka = 1) | Phase 3: exact IS 875-3:2015 free-standing canopy and hoarding provisions, plus asymmetric (eccentric) pressure patterns |
| R3 | LB deflection ratio 0.97 and column interaction 0.94 are tight | Phase 2/6 optimisation: LB grid (put a line on the column lines), the LB/TG depth split, and deflection limits (project vs code) |
| R4 | Roof slope 1:20 in the cantilevers and 1:50 in the centre (1.7° change at the column lines) | Confirm a low-slope concealed-fix/standing-seam colour-coated sheet with the manufacturer |
| R5 | 12 m TG vs galvanizing bath length | Phase 7 durability: galvanize if the bath allows, otherwise a high-performance coating system |
| R6 | Column capital: the TG–HB–CHS moment joint is the critical connection | Phase 5: detailed design and a 1:5 detail |
| R7 | Section properties computed from nominal plates (no radii) | Phase 5: catalogue values (SP 6(1), IS 4923/1161, manufacturer) |
| R8 | Soil SBC 150 kN/m² is an assumption | Sensitivity at 100 and 200 in Phase 5 |
| R9 | IS 1893 zone and R value for a cantilever-column system | Phase 3 |

---

## 13. REVISION LOG

| Rev | Date | Change | Reason | Steel | Cost index | Safety | Drawings |
|---|---|---|---|---|---|---|---|
| 00 | 07-Oct-2026 | Phase 0 audit | — | — | — | — | — |
| 01 | 07-Oct-2026 | Concepts A, B, C-0, C-1 sized. C-1 selected for approval | Phase 1 | 8.99 t (46.8 kg/m²) | 77.7 | All prelim checks ≤ 1.0 except corner deflection 1.02 (R1) | Figs 1–3 (schematic) |

---

## STOP: APPROVAL REQUIRED BEFORE PHASE 2

Please confirm:
1. **Scheme C-1** (tapered tree-girders + continuous RHS purlin-beams + head beams + CHS columns) as the scheme to develop.
2. **Project deflection targets** (L/300 span, L/150 cantilever, L/180 purlins, H/150 drift). These are stricter than IS 800's elastic-cladding values. Relaxing them to code values would save steel but could leave the branding fascia visibly wavy.
3. **Drainage concept:** fall 1:20 to concealed perimeter box gutters on the two long sides, downpipes inside the CHS columns.
