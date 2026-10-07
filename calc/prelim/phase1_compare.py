"""Phase 1 comparison: quantities, relative cost index and weighted decision matrix.
Relative-cost factors are ENGINEERING ASSUMPTIONS (no market prices used); they are
replaced by dated CPWD DSR / AP SSR rates in Phase 6."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "..", "docs", "phase1_results.json")
R = json.load(open(P)); S = R["schemes"]
F = dict(rolled=1.00, hollow=1.10, welded=1.20, truss=1.60, conn=1.50, conc=90.0)  # kg-steel-equivalent
common = lambda r: r["fascia_kg"] + r["soffit_kg"] + r["bracing_kg"]
q = {}
a = S["A"]; q["A"] = dict(rolled=a["sec_kg"] + 2 * a["primary"]["kg"] + a["COL"]["kg"], welded=0, truss=0,
                          hollow=a["purlin"]["kg"] + common(a), conc=4 * a["COL"]["footing"]["V_conc"],
                          B=a["COL"]["footing"]["B"], site_joints=99 + 18 + 2 + 4 + 4 + 8, shop_nodes=0, pieces=22 + 27 + 4 + 4)
b = S["B"]; q["B"] = dict(rolled=0, welded=0, truss=b["sec_kg"] + 2 * b["primary"]["kg"],
                          hollow=b["purlin"]["kg"] + b["COL"]["kg"] + common(b), conc=4 * b["COL"]["footing"]["V_conc"],
                          B=b["COL"]["footing"]["B"], site_joints=99 + 18 + 2 + 4 + 4,
                          shop_nodes=sum(v.get("n_nodes", 0) for v in b["secondaries"].values()) + 2 * b["primary"]["n_nodes"],
                          pieces=22 + 9 + 4 + 4)
for k in ("C", "C1"):
    c = S[k]; col = c["COL"]
    q[k] = dict(rolled=0, welded=2 * c["TG"]["kg"], truss=0,
                hollow=c["LB_kg"] + col["kg"] + common(c), conc=4 * col["footing"]["V_conc"], B=col["footing"]["B"],
                site_joints=22 + 22 + 4 + (4 if k == "C1" else 0), shop_nodes=0,
                pieces=33 + 2 + 4 + (2 if k == "C1" else 0))
out = {}
for k, v in q.items():
    tot = S[k]["total_kg"]; main = v["rolled"] + v["welded"] + v["truss"] + v["hollow"]; conn = tot - main
    cost = (v["rolled"] * F["rolled"] + v["hollow"] * F["hollow"] + v["welded"] * F["welded"]
            + v["truss"] * F["truss"] + conn * F["conn"] + v["conc"] * F["conc"])
    out[k] = dict(v, conn_kg=conn, total_kg=tot, kg_m2=S[k]["kg_m2"], cost_eq=cost)
base = out["A"]["cost_eq"]
for k in out: out[k]["cost_index"] = 100 * out[k]["cost_eq"] / base
# sensitivity: truss fabrication factor needed for B to equal C1
need = (out["C1"]["cost_eq"] - (out["B"]["cost_eq"] - out["B"]["truss"] * F["truss"])) / out["B"]["truss"]
out["_truss_factor_breakeven"] = need
json.dump(out, open(os.path.join(HERE, "..", "..", "docs", "phase1_comparison.json"), "w"), indent=1)
for k, v in out.items():
    print(k, {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in (v.items() if isinstance(v, dict) else [("v", v)])})
