"""PHASE 1 - Preliminary concept sizing of three canopy schemes (A, B, C).

Purpose: give each scheme a defensible preliminary steel quantity, foundation size and
connection count so the schemes can be compared on evidence, not opinion.
NOT a final design. Every load value tagged [PRELIM] is re-derived in Phase 3 with the
actual IS 875-3:2015 tables, and every member is re-designed in Phase 5.

Run:  python3 phase1_concepts.py      (writes ../../docs/phase1_results.json)
"""
import json, math, os
import numpy as np
from frame2d import Frame2D
from sections import (ISMB, WPB, RHS_LIST, SHS_LIST, CHS_LIST, i_section, Md, Vd,
                      Nd_compression, Nd_tension_yield, GAMMA_M0)

E_kN = 2.0e8                      # kN/m^2
OUT = {}

# ======================= 1. GEOMETRY  [OFFICIAL, brochure P4/P8] =======================
LX, LY = 16.0, 12.0               # plan (x along 16 m length, y along 12 m width)
COL_X, COL_Y = (3.5, 12.5), (3.5, 8.5)
OVH = 3.5
H_CLEAR = 6.25                    # FFL to underside of soffit/cover sheet
ENVELOPE = 0.750                  # max fascia depth (A1: whole structure inside)
SOFFIT_BUILDUP = 0.060            # soffit sheet + fixing below steel  [ASSUMPTION]
SHEET_PROFILE = 0.035             # roof sheet rib height              [ASSUMPTION]
RIDGE_RISE = 0.050                # central-zone fall 1:50 over 2.5 m  [ASSUMPTION]
EAVE_FALL = 0.175                 # cantilever-zone fall 1:20 over 3.5 m [ASSUMPTION]
AREA = LX * LY

# ======================= 2. LOADS  [PRELIM - verify in Phase 3] ========================
Vb = 50.0                         # m/s Visakhapatnam, IS 875-3:2015 Annex A  [PRELIM]
k1, k2, k3, k4 = 1.0, 1.0, 1.0, 1.15   # 50 yr; TC2 h<=10 m; flat; cyclonic (A8) [PRELIM]
Vz = Vb * k1 * k2 * k3 * k4
pz = 0.6 * Vz ** 2 / 1000.0       # kN/m^2
Kd, Ka, Kc = 1.0, 1.0, 1.0        # conservative: Kd=1 cyclonic; Ka, Kc not reduced [PRELIM]
pd = Kd * Ka * Kc * pz
CP_UP, CP_DN = -1.3, +0.5         # free-standing canopy, overall net (blockage up to 1) [PRELIM]
CP_LOCAL = 1.8                    # local edge-zone net coefficient for purlins/sheet [PRELIM]
CF_FASCIA = 2.0                   # combined windward+leeward fascia, on one face area [PRELIM]
CF_COL = {"CHS": 0.8, "I": 2.0, "RHS": 2.0}
CF_FRIC = 0.03                    # frictional drag top + soffit surfaces [PRELIM]
WL_UP, WL_DN = CP_UP * pd, CP_DN * pd   # kN/m^2 (sign: + downward)
LL = 0.75                         # IS 875-2 roof, no access except maintenance [PRELIM]
SDL = 0.06 + 0.06 + 0.10          # roof sheet + soffit sheet + services allowance [ASSUMPTION]
FASCIA_DL = 0.25                  # kN/m fascia sheet + back closure + empty gutter [ASSUMPTION]
OUT["loads"] = dict(Vb=Vb, k=[k1, k2, k3, k4], Vz=Vz, pz=pz, pd=pd, WL_up=WL_UP,
                    WL_dn=WL_DN, LL=LL, SDL=SDL)


def q_combos(dl):
    """Factored area loads (kN/m^2, + downward) for IS 800 Table 4 ULS combinations."""
    grav = max(1.5 * (dl + LL), 1.2 * (dl + LL + WL_DN), 1.5 * (dl + WL_DN))
    upl = 0.9 * dl + 1.5 * WL_UP          # negative = upward
    return grav, upl


# Project deflection targets (stricter than IS 800 Table 6 elastic-cladding values) [DECISION]
LIM_SPAN, LIM_CANT, LIM_PURLIN, LIM_DRIFT = 300.0, 150.0, 180.0, 150.0
Q_SERV = abs(WL_UP)               # wind alone governs serviceability (> LL)


# ======================= 3. ANALYSIS HELPERS ===========================================
def beam_line(supports, length, w_fun, EI_fun, point_loads=(), dx=0.125):
    """Continuous beam on knife-edge supports. w_fun(x) kN/m (+down). Returns x, M(sag+), V, defl(+down)."""
    xs = sorted(set(list(np.arange(0, length + 1e-9, dx)) + list(supports) + [p[0] for p in point_loads]))
    f = Frame2D(); nodes = [f.node(x, 0.0) for x in xs]
    for a, b in zip(nodes[:-1], nodes[1:]):
        xm = 0.5 * (f.nodes[a][0] + f.nodes[b][0])
        f.elem(a, b, 1.0, 1e3, EI_fun(xm), w=-w_fun(xm), tag="b")
    for k, x in enumerate(xs):
        if any(abs(x - s) < 1e-9 for s in supports):
            f.support(nodes[k], fx=(abs(x - supports[0]) < 1e-9), fy=True, fr=False)
    for x, P in point_loads:
        f.load(nodes[xs.index(x)], Fy=-P)
    f.solve()
    res = f.member_results("b")
    M = np.array([r[3] for r in res] + [res[-1][4]])
    V = np.array([r[2] for r in res] + [res[-1][2]])
    d = np.array([-f.disp(n)[1] for n in nodes])
    R = {s: f.R[3 * nodes[xs.index(s)] + 1] for s in supports}
    return np.array(xs), M, V, d, R


def defl_ok(xs, d, supports, total):
    """Max span and cantilever deflection ratios against project limits."""
    s0, s1 = supports[0], supports[-1]
    span_d = max(abs(d[(xs > s0) & (xs < s1)]), default=0.0)
    cant_d = max(abs(d[0]), abs(d[-1]))
    span = max(np.diff(supports)) if len(supports) > 1 else 0
    cant = max(s0, total - s1)
    r_span = span_d / (span / LIM_SPAN) if span else 0.0
    r_cant = cant_d / (cant / LIM_CANT) if cant > 0 else 0.0
    return max(r_span, r_cant), span_d, cant_d


# ======================= 4. COMMON ELEMENTS ===========================================
def fascia_system():
    """Fascia posts + 2 girt lines around the perimeter (common to all schemes)."""
    perim = 2 * (LX + LY)
    q = CF_FASCIA * pd                        # kN/m^2 on fascia
    w_girt = 1.5 * q * ENVELOPE / 2           # ULS line load per girt (2 girts)
    span = 2.25
    M = w_girt * span ** 2 / 10
    for s in sorted(RHS_LIST + SHS_LIST, key=lambda s: s.mass):
        if s.Zpx * s.fy / GAMMA_M0 / 1e6 >= M and s.Ix > 0:
            girt = s; break
    posts = math.ceil(perim / span)
    w = 2 * perim * girt.mass + posts * 0.75 * girt.mass * 1.2
    return dict(girt=girt.name, girt_M=M, posts=posts, kg=w)


def column_base_reactions(Pc_down, Pc_up, M_base, H_base):
    return dict(P_down=Pc_down, P_up=Pc_up, M=M_base, H=H_base)


def footing(P_dl, U_wind, M_srv, H_srv, P_grav_srv, SBC=150.0, Df=1.5, t=0.6, ped=0.75):
    """Isolated square footing sized for uplift, overturning, and bearing (service loads).
    U_wind = service wind uplift at column (kN, +up); M_srv, H_srv service wind actions.
    Returns smallest B (0.05 m steps) satisfying FOS>=1.5 on uplift & overturning and
    q_max <= SBC (gravity) / 1.25*SBC (wind) [ASSUMPTION A15]."""
    for B in np.arange(1.5, 6.01, 0.05):
        Wf = 25 * B * B * t + 18 * (B * B - ped ** 2) * (Df - t) + 25 * ped ** 2 * (Df - t + 0.15)
        fos_up = (Wf + P_dl) / max(U_wind, 1e-6)
        Mo = M_srv + H_srv * Df
        fos_ot = ((Wf + P_dl - U_wind) * B / 2) / max(Mo, 1e-6) if Wf + P_dl > U_wind else 0
        q_g = (P_grav_srv + Wf) / B ** 2
        Nw = Wf + P_dl - U_wind
        e = Mo / Nw if Nw > 0 else 99
        q_w = Nw / B ** 2 * (1 + 6 * e / B) if e <= B / 6 else 2 * Nw / (3 * B * (B / 2 - e)) if e < B / 2 else 1e9
        if fos_up >= 1.5 and fos_ot >= 1.5 and q_g <= SBC and q_w <= 1.25 * SBC:
            V = B * B * t + ped ** 2 * (Df - t + 0.15)
            return dict(B=round(B, 2), t=t, Df=Df, W=Wf, FOS_uplift=fos_up, FOS_OT=fos_ot,
                        q_grav=q_g, q_wind=q_w, V_conc=V)
    raise RuntimeError("footing not found")


def lateral_forces(col_kind, col_width):
    col = 4 * CF_COL[col_kind] * pd * col_width * H_CLEAR
    fric = CF_FRIC * pd * AREA
    Fy = CF_FASCIA * pd * ENVELOPE * LX + fric + col   # wind along y (on 16 m faces)
    Fx = CF_FASCIA * pd * ENVELOPE * LY + fric + col   # wind along x (on 12 m faces)
    return Fx, Fy


def check_column(sec, N_c, N_t, M_list, KL):
    """Prelim interaction (conservative linear, IS 800 cl. 9.3 refined in Phase 5)."""
    Ndc, slr = Nd_compression(sec, KL)
    Ndt = Nd_tension_yield(sec)
    Mdx = (1.0 if sec.cls in ("plastic", "compact") else sec.Zex / sec.Zpx) * sec.Zpx * sec.fy / GAMMA_M0
    Mdy = (sec.Zpy if sec.cls in ("plastic", "compact") else sec.Zey) * sec.fy / GAMMA_M0
    ur = 0.0
    for (N, Mx, My) in M_list:
        Nd = Ndc if N > 0 else Ndt
        ur = max(ur, abs(N) * 1e3 / Nd + abs(Mx) * 1e6 / Mdx + abs(My) * 1e6 / Mdy)
    return ur, slr


# ======================= 5. SCHEME C (selected candidate) =============================
def scheme_C(dl_est):
    """Hybrid: 2 tapered welded transverse tree-girders (TG) on CHS column pairs +
    continuous RHS purlin-beams (LB) on top at 1.2 m, spanning 9 m + 3.5 m cantilevers."""
    qg, qu = q_combos(dl_est)
    sp = 1.2
    n_lb = int(round(LY / sp)) + 1
    best = None
    for lb in sorted(RHS_LIST, key=lambda s: s.mass):
        # ---- LB design (interior line, tributary 1.2 m) ----
        EI = E_kN * lb.Ix * 1e-12
        sup = [COL_X[0], COL_X[1]]
        ok = True; urmax = 0
        for q in (qg, qu):
            xs, M, V, d, R = beam_line(sup, LX, lambda x: q * sp + 1.0 * 0, lambda x: EI)
            Mr = Md(lb)[0] / 1e6; Vr = Vd(lb) / 1e3
            urmax = max(urmax, abs(M).max() / Mr, abs(V).max() / Vr)
        xs, M, V, d, R = beam_line(sup, LX, lambda x: Q_SERV * sp, lambda x: EI)
        rd, dspan, dcant = defl_ok(xs, d, sup, LX)
        if urmax > 1.0 or rd > 1.0:
            continue
        D0_max = ENVELOPE - SOFFIT_BUILDUP - RIDGE_RISE - SHEET_PROFILE - lb.D / 1000
        tg = design_TG(qg, qu, D0_max, dl_est)
        if tg is None:
            continue
        cols = design_columns_C(tg, dl_est)
        lb_kg = n_lb * LX * lb.mass
        tot = lb_kg + tg["kg"] * 2 + cols["kg"]
        cand = dict(LB=lb.name, LB_h=lb.D, LB_ur=urmax, LB_defl_ratio=rd, LB_dspan_mm=dspan * 1e3,
                    LB_dcant_mm=dcant * 1e3, n_LB=n_lb, LB_kg=lb_kg, TG=tg, COL=cols, D0_max=D0_max,
                    main_kg=tot)
        if best is None or tot < best["main_kg"]:
            best = cand
    return best


def tg_profile(D0, y):
    """Depth of tapered transverse girder (m) at coordinate y (m)."""
    if y <= COL_Y[0]:
        return D0 - EAVE_FALL * (COL_Y[0] - y) / OVH
    if y >= COL_Y[1]:
        return D0 - EAVE_FALL * (y - COL_Y[1]) / OVH
    return D0 + RIDGE_RISE * (1 - abs(y - LY / 2) / ((COL_Y[1] - COL_Y[0]) / 2))


_TG_CACHE = {}


def design_TG(qg, qu, D0_max, dl_est):
    key = (round(qg, 3), round(qu, 3), round(D0_max, 3))
    if key not in _TG_CACHE:
        _TG_CACHE[key] = _design_TG(qg, qu, D0_max)
    return _TG_CACHE[key]


def _design_TG(qg, qu, D0_max):
    trib = (COL_X[1] - COL_X[0]) / 2 + OVH       # 8.0 m strip carried by each TG
    best = None
    for D0 in np.arange(0.30, D0_max + 1e-9, 0.025):
        for bf in (150, 180, 200, 220, 250, 280, 300):
            for tf in (8, 10, 12, 14, 16, 20):
                for tw in (6, 8):
                    if bf / 2 / tf > 13.6 * math.sqrt(250 / 250):
                        continue
                    secs = {}
                    def sec_at(y):
                        D = round(tg_profile(D0, y) * 1000)
                        if D not in secs:
                            secs[D] = i_section(f"TG {D}", D, bf, tf, tw, fy=250.0, welded=True)
                        return secs[D]
                    EI = lambda y: E_kN * sec_at(y).Ix * 1e-12
                    sup = list(COL_Y)
                    ur = 0
                    for q, LLT in ((qg, 2.4), (qu, 1.2)):  # gravity: bottom fl. fly-braced 2.4 m; uplift: top fl. 1.2 m
                        xs, M, V, d, R = beam_line(sup, LY, lambda y: q * trib, EI)
                        for y, m, v in zip(xs, M, V):
                            s = sec_at(y)
                            ur = max(ur, abs(m) / (Md(s, LLT * 1000)[0] / 1e6), abs(v) / (Vd(s) / 1e3))
                    if ur > 1.0:
                        continue
                    xs, M, V, d, R = beam_line(sup, LY, lambda y: Q_SERV * trib, EI)
                    rd, dspan, dcant = defl_ok(xs, d, sup, LY)
                    if rd > 1.0:
                        continue
                    ys = np.arange(0, LY + 1e-9, 0.125)
                    kg = sum(sec_at(y).mass * 0.125 for y in ys[:-1]) * 1.05   # +5% stiffeners/end plates
                    cand = dict(D0=round(D0, 3), D_tip=round(tg_profile(D0, 0), 3),
                                D_ridge=round(tg_profile(D0, 6), 3), bf=bf, tf=tf, tw=tw,
                                ur=ur, defl_ratio=rd, d_span_mm=dspan * 1e3, d_tip_mm=dcant * 1e3,
                                kg=kg, R_col_grav=None)
                    if best is None or kg < best["kg"]:
                        best = cand
    if best:
        sec0 = i_section("TG0", round(best["D0"] * 1000), best["bf"], best["tf"], best["tw"], welded=True)
        best["Ix0_cm4"] = sec0.Ix / 1e4
        # prismatic equivalent for frame analysis = section at column (conservative-ish)
        best["EI0"] = E_kN * sec0.Ix * 1e-12
        best["A0"] = sec0.A * 1e-6
    return best


def design_columns_C(tg, dl_est):
    """CHS columns. y-direction: TG portal frame (fixed base, rigid TG joint).
    x-direction: free-standing cantilevers (LBs only bear on TG -> no x-frame action)."""
    qg, qu = q_combos(dl_est)
    trib = 8.0
    best = None
    for c in sorted(CHS_LIST, key=lambda s: s.mass):
        Fx, Fy = lateral_forces("CHS", c.D / 1000)
        h = H_CLEAR + SOFFIT_BUILDUP + tg["D0"] / 2
        EIc = E_kN * c.Ix * 1e-12; Ac = c.A * 1e-6
        res = []
        drift = 0
        for q, Hfac in ((qg, 1.5), (qu, 1.5)):   # lateral wind with both vertical wind cases (conservative)
            # y-frame (one TG portal carries Fy/2)
            f = Frame2D()
            yb = [f.node(y, h) for y in np.arange(0, LY + 1e-9, 0.25)]
            for a, b in zip(yb[:-1], yb[1:]):
                f.elem(a, b, E_kN, tg["A0"], tg["EI0"] / E_kN, w=-q * trib, tag="TG")
            for yc in COL_Y:
                top = f.node(yc, h)
                prev = f.node(yc, 0.0); f.support(prev)
                for z in np.arange(0.5, h + 1e-9, 0.5):
                    nz = f.node(yc, min(z, h)) if z < h - 1e-6 else top
                    f.elem(prev, nz, E_kN, Ac, EIc / E_kN, tag=f"C{yc}")
                    prev = nz
                if prev != top:
                    f.elem(prev, top, E_kN, Ac, EIc / E_kN, tag=f"C{yc}")
            f.load(f.node(COL_Y[0], h), Fx=Hfac * Fy / 2 / 2)
            f.load(f.node(COL_Y[1], h), Fx=Hfac * Fy / 2 / 2)
            f.solve()
            for yc in COL_Y:
                r = f.reactions()[f.node(yc, 0.0)]
                N = r[1]
                ktop = [i for i, e in enumerate(f.elems) if e["tag"] == f"C{yc}"][-1]
                Mb = max(abs(r[2]), abs(f.forces[ktop][5]))
                # x-direction cantilever moment for the same wind event (Fx/4 at top + column UDL)
                wcol = Hfac * CF_COL["CHS"] * pd * c.D / 1000
                Mx = Hfac * Fx / 4 * h + wcol * H_CLEAR ** 2 / 2
                res.append((N, Mb, 0.0))      # y-wind case
                res.append((N, 0.0, Mx))      # x-wind case (axial kept: conservative)
        # service drift
        Fx_s, Fy_s = lateral_forces("CHS", c.D / 1000)
        dx = (Fx_s / 4) * h ** 3 / (3 * EIc) + CF_COL["CHS"] * pd * c.D / 1000 * H_CLEAR ** 4 / (8 * EIc)
        ur, slr = check_column(c, 0, 0, res, KL=2.0 * h * 1000)
        if ur <= 1.0 and dx <= h / LIM_DRIFT:
            Pdl = (dl_est * AREA + FASCIA_DL * 2 * (LX + LY)) / 4
            Uw = abs(WL_UP) * AREA / 4
            Ms = Fx_s / 4 * h + CF_COL["CHS"] * pd * c.D / 1000 * H_CLEAR ** 2 / 2
            ft = footing(Pdl, Uw, Ms, Fx_s / 4, Pdl + LL * AREA / 4)
            best = dict(section=c.name, D=c.D, ur=ur, KL_r=slr, drift_mm=dx * 1e3,
                        drift_lim_mm=h / LIM_DRIFT * 1e3, h=h, kg=4 * h * c.mass,
                        N_max=max(r[0] for r in res), N_min=min(r[0] for r in res),
                        M_max=max(max(abs(r[1]), abs(r[2])) for r in res), Fx=Fx_s, Fy=Fy_s,
                        footing=ft, Mbase_srv=Ms, U_srv=Uw, P_dl=Pdl)
            break
    return best


# ======================= 6. SCHEME A (conventional rolled-I grillage) =================
SEC_X = [0.0, 1.75, 3.5, 5.75, 8.0, 10.25, 12.5, 14.25, 16.0]   # secondary lines (x)


def trib_x(i):
    xs = SEC_X
    left = (xs[i] - xs[i - 1]) / 2 if i > 0 else 0
    right = (xs[i + 1] - xs[i]) / 2 if i < len(xs) - 1 else 0
    return left + right


def scheme_A(dl_est, truss=False):
    """Two-way flush grillage: x-primaries on column lines, y-secondaries @ <=2.25 m,
    purlins on packers. truss=True -> Scheme B (shallow tubular trusses, same layout)."""
    qg, qu = q_combos(dl_est)
    sp = 1.2; n_p = int(round(LY / sp)) + 1
    # --- purlins: continuous over secondaries ---
    q_pg = 1.5 * (0.06 + CP_LOCAL * pd) ; q_pu = 1.5 * CP_LOCAL * pd - 0.9 * 0.06
    pur = None
    for s in sorted(RHS_LIST, key=lambda s: s.mass):
        EI = E_kN * s.Ix * 1e-12
        ur = 0
        for q in (q_pg, q_pu):
            xs, M, V, d, R = beam_line(SEC_X, LX, lambda x: q * sp, lambda x: EI)
            ur = max(ur, abs(M).max() / (Md(s)[0] / 1e6), abs(V).max() / (Vd(s) / 1e3))
        xs, M, V, d, R = beam_line(SEC_X, LX, lambda x: CP_LOCAL * pd * sp, lambda x: EI)
        dmax = abs(d).max()
        if ur <= 1.0 and dmax <= 2.25 / LIM_PURLIN:
            pur = dict(section=s.name, h=s.D, ur=ur, d_mm=dmax * 1e3, kg=n_p * LX * s.mass); break
    ph = pur["h"] / 1000
    if truss:
        Dmax = ENVELOPE - SOFFIT_BUILDUP - RIDGE_RISE - ph - SHEET_PROFILE
    else:
        Dmax = ENVELOPE - SOFFIT_BUILDUP - (EAVE_FALL + RIDGE_RISE) - ph - SHEET_PROFILE
    # --- secondaries (y-direction, supports at girders y=3.5, 8.5) ---
    sec_res = {}; sec_kg = 0; reac = {}
    for i, x in enumerate(SEC_X):
        tb = trib_x(i)
        tip = FASCIA_DL * tb
        r = design_beam_member(lambda y: None, list(COL_Y), LY, tb, qg, qu, Dmax, truss,
                               tip_loads=[(0.0, tip), (LY, tip)], LLT=(2.4, 1.2))
        sec_res[x] = r; sec_kg += r["kg"]
        reac[x] = r["R"]
    # --- primaries (x-direction on column lines) with secondary reactions as point loads ---
    prim = design_primary(reac, Dmax, truss, qg, qu)
    # --- columns: two-way moment frames ---
    cols = design_columns_A(prim, sec_res[3.5], truss, dl_est)
    tot = pur["kg"] + sec_kg + 2 * prim["kg"] + cols["kg"]
    return dict(purlin=pur, secondaries={k: {kk: vv for kk, vv in v.items() if kk != "R"} for k, v in sec_res.items()},
                sec_kg=sec_kg, primary=prim, COL=cols, Dmax=Dmax, main_kg=tot)


def truss_section(D, chords):
    """Equivalent beam properties of a shallow truss with identical SHS chords."""
    c = chords
    dc = D - c.D / 1000
    I = 2 * c.A * 1e-6 * (dc / 2) ** 2 * 0.85      # 15% allowance for web shear deformation
    return dc, I


def design_beam_member(_, sup, Ltot, trib, qg, qu, Dmax, truss, tip_loads=(), LLT=(2.4, 1.2)):
    if not truss:
        for s in sorted(ISMB + WPB, key=lambda s: s.mass):
            if s.D / 1000 > Dmax + 1e-9:
                continue
            EI = E_kN * s.Ix * 1e-12
            ur = 0
            for q, Lb in ((qg, LLT[0]), (qu, LLT[1])):
                pl = [(x, P * (1.5 if q > 0 else -0.9)) for x, P in tip_loads]
                xs, M, V, d, R = beam_line(sup, Ltot, lambda y: q * trib, lambda y: EI, point_loads=pl)
                ur = max(ur, abs(M).max() / (Md(s, Lb * 1000)[0] / 1e6), abs(V).max() / (Vd(s) / 1e3))
            xs, M, V, d, Rs = beam_line(sup, Ltot, lambda y: Q_SERV * trib, lambda y: EI)
            rd, ds, dc = defl_ok(xs, d, sup, Ltot)
            if ur <= 1.0 and rd <= 1.0:
                xs, M, V, d, Rg = beam_line(sup, Ltot, lambda y: 1.0, lambda y: EI)
                return dict(section=s.name, D=s.D, ur=ur, defl_ratio=rd, d_span_mm=ds * 1e3,
                            d_tip_mm=dc * 1e3, kg=Ltot * s.mass, R=Rg[sup[0]] / 1.0 * trib,
                            EI=EI, A=s.A * 1e-6)
        raise RuntimeError("no rolled section fits depth")
    # truss: size chords then webs
    D = Dmax
    for ch in sorted(SHS_LIST, key=lambda s: s.mass):
        if ch.D < 60:
            continue
        dc, I = truss_section(D, ch)
        EI = E_kN * I
        Mmax = Vmax = 0
        for q in (qg, qu):
            xs, M, V, d, R = beam_line(sup, Ltot, lambda y: q * trib, lambda y: EI)
            Mmax = max(Mmax, abs(M).max()); Vmax = max(Vmax, abs(V).max())
        Fch = Mmax / dc
        Ndc, _ = Nd_compression(ch, 2400.0)            # out-of-plane restraint 2.4 m (conservative)
        if Fch * 1e3 > min(Ndc, Nd_tension_yield(ch)):
            continue
        xs, M, V, d, Rs = beam_line(sup, Ltot, lambda y: Q_SERV * trib, lambda y: EI)
        rd, ds, dcn = defl_ok(xs, d, sup, Ltot)
        if rd > 1.0:
            continue
        # webs: Warren diagonals at ~45 deg
        Ld = math.hypot(dc, dc)
        Fw = Vmax * Ld / dc
        for wb in sorted(SHS_LIST, key=lambda s: s.mass):
            if Fw * 1e3 <= Nd_compression(wb, 0.9 * Ld * 1000)[0]:
                break
        n_diag = Ltot / dc
        kg = (2 * Ltot * ch.mass + n_diag * Ld * wb.mass) * 1.15     # +15% node plates / gussets
        xs, M, V, d, Rg = beam_line(sup, Ltot, lambda y: 1.0, lambda y: EI)
        return dict(section=f"Truss D={D*1000:.0f}: chords {ch.name}, webs {wb.name}", D=D * 1000,
                    ur=Fch * 1e3 / min(Ndc, Nd_tension_yield(ch)), defl_ratio=rd,
                    d_span_mm=ds * 1e3, d_tip_mm=dcn * 1e3, kg=kg, R=Rg[sup[0]] * trib,
                    EI=EI, A=2 * ch.A * 1e-6, n_nodes=int(2 * n_diag))
    raise RuntimeError("truss chords not found")


def design_primary(reac, Dmax, truss, qg, qu):
    """Primary on y=3.5 line carries reactions of all secondaries (per unit area load)."""
    pts_unit = [(x, reac[x]) for x in SEC_X if x not in COL_X]
    cands = sorted(ISMB + WPB, key=lambda s: s.mass) if not truss else None
    def run(EI, q):
        return beam_line(list(COL_X), LX, lambda x: 0.0, lambda x: EI,
                         point_loads=[(x, P * q) for x, P in pts_unit])
    if not truss:
        for s in cands:
            if s.D / 1000 > Dmax + 1e-9:
                continue
            EI = E_kN * s.Ix * 1e-12
            ur = 0
            for q in (qg, qu):
                xs, M, V, d, R = run(EI, q)
                ur = max(ur, abs(M).max() / (Md(s, 2250.0)[0] / 1e6), abs(V).max() / (Vd(s) / 1e3))
            xs, M, V, d, R = run(EI, Q_SERV)
            rd, ds, dc = defl_ok(xs, d, list(COL_X), LX)
            if ur <= 1.0 and rd <= 1.0:
                return dict(section=s.name, D=s.D, ur=ur, defl_ratio=rd, d_span_mm=ds * 1e3,
                            d_tip_mm=dc * 1e3, kg=LX * s.mass * 1.05, EI=EI, A=s.A * 1e-6, pts=pts_unit)
        raise RuntimeError("no primary")
    for ch in sorted(SHS_LIST, key=lambda s: s.mass):
        if ch.D < 60:
            continue
        dc, I = truss_section(Dmax, ch); EI = E_kN * I
        Mmax = Vmax = 0
        for q in (qg, qu):
            xs, M, V, d, R = run(EI, q); Mmax = max(Mmax, abs(M).max()); Vmax = max(Vmax, abs(V).max())
        Fch = Mmax / dc
        Ndc, _ = Nd_compression(ch, 2250.0)
        if Fch * 1e3 > min(Ndc, Nd_tension_yield(ch)):
            continue
        xs, M, V, d, R = run(EI, Q_SERV)
        rd, ds, dcn = defl_ok(xs, d, list(COL_X), LX)
        if rd > 1.0:
            continue
        Ld = math.hypot(dc, dc); Fw = Vmax * Ld / dc
        for wb in sorted(SHS_LIST, key=lambda s: s.mass):
            if Fw * 1e3 <= Nd_compression(wb, 0.9 * Ld * 1000)[0]:
                break
        n_diag = LX / dc
        kg = (2 * LX * ch.mass + n_diag * Ld * wb.mass) * 1.15
        return dict(section=f"Truss D={Dmax*1000:.0f}: chords {ch.name}, webs {wb.name}", D=Dmax * 1000,
                    ur=Fch * 1e3 / min(Ndc, Nd_tension_yield(ch)), defl_ratio=rd, d_span_mm=ds * 1e3,
                    d_tip_mm=dcn * 1e3, kg=kg, EI=EI, A=2 * ch.A * 1e-6, pts=pts_unit,
                    n_nodes=int(2 * n_diag))
    raise RuntimeError("no primary truss")


def design_columns_A(prim, sec_col, truss, dl_est):
    """Columns in two-way moment frames (x: primary girder; y: column-line secondary)."""
    qg, qu = q_combos(dl_est)
    lib = sorted(CHS_LIST, key=lambda s: s.mass) if truss else sorted(WPB, key=lambda s: s.mass)
    kind = "CHS" if truss else "I"
    for c in lib:
        width = c.D / 1000 if truss else c.bf / 1000
        Fx_s, Fy_s = lateral_forces(kind, width)
        h = H_CLEAR + SOFFIT_BUILDUP + prim["D"] / 2000
        EIc_x = E_kN * c.Ix * 1e-12            # strong axis -> x-frame
        EIc_y = E_kN * (c.Iy if not truss else c.Ix) * 1e-12
        Ac = c.A * 1e-6
        res = []; drifts = []
        for q in (qg, qu, None):
            for direction in ("x", "y"):
                f = Frame2D()
                if direction == "x":
                    L, cols, EIb, Ab, EIc = LX, COL_X, prim["EI"], prim["A"], EIc_x
                    pts = [(x, P) for x, P in prim["pts"]]
                    wline = 0.0; F = Fx_s
                else:
                    L, cols, EIb, Ab, EIc = LY, COL_Y, sec_col["EI"], sec_col["A"], EIc_y
                    pts = []; wline = trib_x(2); F = Fy_s
                xs = sorted(set(list(np.arange(0, L + 1e-9, 0.25)) + [p[0] for p in pts] + list(cols)))
                bn = [f.node(x, h) for x in xs]
                qq = q if q is not None else 0.0
                for a, b in zip(bn[:-1], bn[1:]):
                    f.elem(a, b, E_kN, Ab, EIb / E_kN, w=-qq * wline, tag="B")
                for x, P in pts:
                    f.load(f.node(x, h), Fy=-P * qq)
                for xc in cols:
                    base = f.node(xc, 0.0); f.support(base)
                    f.elem(base, f.node(xc, h), E_kN, Ac, EIc / E_kN, tag="C")
                    if direction == "x":
                        # the y-direction strip at the column line delivers its reaction axially
                        f.load(f.node(xc, h), Fy=-sec_col["R"] * qq)
                Hf = 1.5 if q is not None else 1.0
                for xc in cols:
                    f.load(f.node(xc, h), Fx=Hf * F / 2 / 2)
                f.solve()
                if q is None:
                    drifts.append(abs(f.disp(f.node(cols[0], h))[0]))
                    continue
                for xc in cols:
                    r = f.reactions()[f.node(xc, 0.0)]
                    # moment at column top = from element end forces
                    k = [i for i, e in enumerate(f.elems) if e["tag"] == "C" and f.nodes[e["i"]][0] == xc][0]
                    Mtop = abs(f.forces[k][5]); Mb = abs(r[2])
                    if direction == "x":
                        res.append((r[1], max(Mb, Mtop), 0.0))
                    else:
                        res.append((r[1], 0.0, max(Mb, Mtop)))
        # strip (y-frame) axial: add primary share is already in x-frame N; combine conservatively
        ur, slr = check_column(c, 0, 0, res, KL=1.5 * h * 1000)
        drift = max(drifts)
        if ur <= 1.0 and drift <= h / LIM_DRIFT:
            Pdl = (dl_est * AREA + FASCIA_DL * 2 * (LX + LY)) / 4
            Uw = abs(WL_UP) * AREA / 4
            Ms = Fx_s / 4 * h * 0.6          # partial top fixity in moment frames (prelim)
            ft = footing(Pdl, Uw, Ms, Fx_s / 4, Pdl + LL * AREA / 4)
            return dict(section=c.name, ur=ur, KL_r=slr, drift_mm=drift * 1e3,
                        drift_lim_mm=h / LIM_DRIFT * 1e3, h=h, kg=4 * h * c.mass,
                        M_max=max(max(abs(r[1]), abs(r[2])) for r in res),
                        N_max=max(r[0] for r in res), N_min=min(r[0] for r in res),
                        Fx=Fx_s, Fy=Fy_s, footing=ft)
    raise RuntimeError("no column")


# ======================= 7. RUN, ITERATE SELF-WEIGHT, REPORT ===========================
def run_all():
    results = {}
    fas = fascia_system()
    OUT["fascia"] = fas
    soffit_kg = 11 * LX * 4.5        # soffit runners (light RHS, ~4.5 kg/m) [PRELIM allowance]
    bracing_kg = 250.0               # roof plan bracing allowance [PRELIM]
    for key, fn in (("A", lambda dl: scheme_A(dl)), ("B", lambda dl: scheme_A(dl, truss=True)),
                    ("C", scheme_C)):
        dl = SDL + 0.30
        for _ in range(4):           # iterate self-weight
            r = fn(dl)
            conn = {"A": 0.10, "B": 0.15, "C": 0.08}[key]   # connection/base plate allowance
            steel = (r["main_kg"] + fas["kg"] + soffit_kg + bracing_kg) * (1 + conn)
            new_dl = SDL + steel * 9.81e-3 / AREA
            if abs(new_dl - dl) < 0.005:
                break
            dl = new_dl
        r["fascia_kg"] = fas["kg"]; r["soffit_kg"] = soffit_kg; r["bracing_kg"] = bracing_kg
        r["conn_allow"] = conn
        r["total_kg"] = steel; r["kg_m2"] = steel / AREA; r["dl_used"] = dl
        results[key] = r
    OUT["schemes"] = results
    return results


if __name__ == "__main__":
    res = run_all()
    path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "phase1_results.json")
    with open(path, "w") as fh:
        json.dump(OUT, fh, indent=1, default=str)
    L = OUT["loads"]
    print(f"Vz={L['Vz']:.2f} m/s  pz={L['pz']:.3f} kPa  pd={L['pd']:.3f}  WLup={L['WL_up']:.3f}  WLdn={L['WL_dn']:.3f}")
    for k, r in res.items():
        print(f"\n=== SCHEME {k}: total {r['total_kg']:.0f} kg = {r['kg_m2']:.1f} kg/m2 (DL used {r['dl_used']:.3f} kPa)")
        print(json.dumps({kk: vv for kk, vv in r.items() if kk not in ('secondaries',)}, indent=1, default=str)[:3500])


# ======================= 8. SCHEME C-1: add column-head tie beams (x-portal) ===========
def scheme_C1(dl_est):
    """Scheme C + 2 moment-connected head beams (y = 3.5, 8.5; x = 3.5..12.5) flush with the
    TG at the column heads. Converts x-direction free cantilevers into fixed-base portals."""
    base = scheme_C(dl_est)
    tg = base["TG"]
    qg, qu = q_combos(dl_est)
    D0 = tg["D0"]
    h = H_CLEAR + SOFFIT_BUILDUP + D0 / 2
    trib = 8.0
    # TG reaction per column for the vertical cases (from a beam_line on TG)
    Rv = {}
    for q in (qg, qu):
        xs, M, V, d, R = beam_line(list(COL_Y), LY, lambda y: q * trib, lambda y: tg["EI0"])
        Rv[q] = R[COL_Y[0]]
    best = None
    beams = [s for s in sorted(ISMB + RHS_LIST, key=lambda s: s.mass) if s.D / 1000 <= D0 + 1e-9]
    for c in sorted(CHS_LIST, key=lambda s: s.mass):
        Fx_s, Fy_s = lateral_forces("CHS", c.D / 1000)
        EIc = E_kN * c.Ix * 1e-12; Ac = c.A * 1e-6
        for hb in beams:
            EIb = E_kN * hb.Ix * 1e-12; Ab = hb.A * 1e-6
            res = []; ok = True
            for q in (qg, qu, None):
                f = Frame2D()
                xs = list(np.arange(COL_X[0], COL_X[1] + 1e-9, 0.25))
                bn = [f.node(x, h) for x in xs]
                for a, b in zip(bn[:-1], bn[1:]):
                    f.elem(a, b, E_kN, Ab, EIb / E_kN, w=-(1.5 if q else 0) * hb.mass * 9.81e-3, tag="HB")
                for xc in COL_X:
                    bse = f.node(xc, 0.0); f.support(bse)
                    f.elem(bse, f.node(xc, h), E_kN, Ac, EIc / E_kN, tag=f"C{xc}")
                    if q is not None:
                        f.load(f.node(xc, h), Fy=-Rv[q])
                    f.load(f.node(xc, h), Fx=(1.5 if q is not None else 1.0) * Fx_s / 2 / 2)
                f.solve()
                if q is None:
                    drift = abs(f.disp(f.node(COL_X[0], h))[0]); continue
                for xc in COL_X:
                    r = f.reactions()[f.node(xc, 0.0)]
                    k = [i for i, e in enumerate(f.elems) if e["tag"] == f"C{xc}"][0]
                    Mc = max(abs(r[2]), abs(f.forces[k][5]))
                    res.append((r[1], 0.0, Mc))
                hbr = f.member_results("HB")
                Mhb = max(max(abs(x[3]), abs(x[4])) for x in hbr)
                if Mhb * 1e6 > Md(hb, 2250.0 if hb.kind == "I" else None)[0]:
                    ok = False
            # y-direction portal results from base scheme (TG frame) for this column
            yres = design_columns_C_ywind(c, tg, dl_est)
            ur, slr = check_column(c, 0, 0, res + yres, KL=1.5 * h * 1000)
            if ok and ur <= 1.0 and drift <= h / LIM_DRIFT:
                Pdl = (dl_est * AREA + FASCIA_DL * 2 * (LX + LY)) / 4
                Uw = abs(WL_UP) * AREA / 4
                Ms = max(abs(r[2]) for r in res) / 1.5
                ft = footing(Pdl, Uw, Ms, Fx_s / 4, Pdl + LL * AREA / 4)
                kg = 4 * h * c.mass + 2 * 9.0 * hb.mass * 1.05
                cand = dict(section=c.name, head_beam=hb.name, ur=ur, drift_mm=drift * 1e3,
                            drift_lim_mm=h / LIM_DRIFT * 1e3, h=h, kg=kg, col_kg=4 * h * c.mass,
                            hb_kg=2 * 9.0 * hb.mass * 1.05, footing=ft, M_max=max(abs(r[2]) for r in res + yres),
                            N_max=max(r[0] for r in res), N_min=min(r[0] for r in res), Fx=Fx_s, Fy=Fy_s)
                if best is None or kg < best["kg"]:
                    best = cand
                break
    base["COL_C0"] = base["COL"]
    base["COL"] = best
    base["main_kg"] = base["LB_kg"] + 2 * tg["kg"] + best["kg"]
    return base


def design_columns_C_ywind(c, tg, dl_est):
    qg, qu = q_combos(dl_est)
    Fx_s, Fy_s = lateral_forces("CHS", c.D / 1000)
    h = H_CLEAR + SOFFIT_BUILDUP + tg["D0"] / 2
    EIc = E_kN * c.Ix * 1e-12; Ac = c.A * 1e-6
    out = []
    for q in (qg, qu):
        f = Frame2D()
        yb = [f.node(y, h) for y in np.arange(0, LY + 1e-9, 0.25)]
        for a, b in zip(yb[:-1], yb[1:]):
            f.elem(a, b, E_kN, tg["A0"], tg["EI0"] / E_kN, w=-q * 8.0, tag="TG")
        for yc in COL_Y:
            bse = f.node(yc, 0.0); f.support(bse)
            f.elem(bse, f.node(yc, h), E_kN, Ac, EIc / E_kN, tag=f"C{yc}")
            f.load(f.node(yc, h), Fx=1.5 * Fy_s / 4)
        f.solve()
        for yc in COL_Y:
            r = f.reactions()[f.node(yc, 0.0)]
            k = [i for i, e in enumerate(f.elems) if e["tag"] == f"C{yc}"][0]
            out.append((r[1], max(abs(r[2]), abs(f.forces[k][5])), 0.0))
    return out


def run_C1():
    fas = OUT["fascia"]; soffit_kg = 11 * LX * 4.5; bracing_kg = 250.0
    dl = SDL + 0.30
    for _ in range(4):
        r = scheme_C1(dl)
        steel = (r["main_kg"] + fas["kg"] + soffit_kg + bracing_kg) * 1.08
        new_dl = SDL + steel * 9.81e-3 / AREA
        if abs(new_dl - dl) < 0.005:
            break
        dl = new_dl
    r.update(fascia_kg=fas["kg"], soffit_kg=soffit_kg, bracing_kg=bracing_kg, conn_allow=0.08,
             total_kg=steel, kg_m2=steel / AREA, dl_used=dl)
    return r
