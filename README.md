# INSDAG NACS (C) 2026 — Fuel Station Canopy

Steel Intensive Supporting & Roof Structure for a Fuel Station Canopy, Visakhapatnam.

| Phase | Document | Status |
|---|---|---|
| 0 — Document audit | [docs/00_Phase0_Document_Audit.md](docs/00_Phase0_Document_Audit.md) | Approved (defaults) |
| 1 — Structural concept | [docs/01_Phase1_Structural_Concept.md](docs/01_Phase1_Structural_Concept.md) | **For approval** — Scheme C-1 recommended |
| 2 — Preliminary design | — | Awaiting Phase 1 approval |

Figures: `docs/figs/`. Official brief: [reference/INSDAG_NACS_C_2026_Brochure.pdf](reference/INSDAG_NACS_C_2026_Brochure.pdf)

## Preliminary calculation tools (`calc/prelim/`)
- `frame2d.py` — 2D direct-stiffness frame solver (validated against closed-form cases)
- `sections.py` — section library + IS 800:2007 capacity helpers (nominal properties, prelim only)
- `phase1_concepts.py` — sizes Schemes A, B, C, C-1 → `docs/phase1_results.json`
- `phase1_compare.py` — quantities, relative cost index → `docs/phase1_comparison.json`
- `phase1_figures.py` — concept figures

```
pip install numpy matplotlib
cd calc/prelim && python3 -c "import phase1_concepts as P, json; P.run_all(); P.OUT['schemes']['C1']=P.run_C1(); json.dump(P.OUT, open('../../docs/phase1_results.json','w'), indent=1, default=str)"
python3 phase1_compare.py && python3 phase1_figures.py
```

Final entry due **15-Nov-2026** to competitions@insdag.com.
