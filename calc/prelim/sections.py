"""Preliminary section library and IS 800:2007 member-capacity helpers.

PRELIMINARY USE ONLY (Phase 1 concept sizing).
* Properties are computed from nominal plate dimensions (no root radii / corner radii),
  so areas and inertias are slightly different from catalogue values. Final design
  (Phase 5) must use manufacturer / SP 6(1) / IS 808 / IS 4923 / IS 1161 tabulated values.
* Rolled-section dimensions are nominal IS 808 / SP 6(1) values; hollow-section sizes are
  nominal IS 4923 / IS 1161 sizes. Availability must be confirmed from the INSDAG
  website or a manufacturer's catalogue (brochure P5, Guideline 4).
Units: N, mm, MPa unless noted.
"""
import math

E = 2.0e5          # MPa, IS 800 cl. 2.2.4.1
GAMMA_M0 = 1.10    # IS 800 Table 5
RHO = 7850e-9      # kg/mm^3


class Section:
    def __init__(self, name, kind, A, Ix, Zex, Zpx, Iy=None, ry=None, fy=250.0,
                 D=None, bf=None, tf=None, tw=None, t=None, Av=None, cls=None,
                 Zey=None, Zpy=None, welded=False, buck_alpha=0.34):
        self.name, self.kind = name, kind
        self.A, self.Ix, self.Zex, self.Zpx = A, Ix, Zex, Zpx
        self.Iy, self.ry, self.fy = Iy, ry, fy
        self.D, self.bf, self.tf, self.tw, self.t = D, bf, tf, tw, t
        self.Av, self.cls, self.welded = Av, cls, welded
        self.Zey, self.Zpy = Zey, Zpy
        self.buck_alpha = buck_alpha
        self.mass = A * RHO * 1000.0      # kg/m

    @property
    def rx(self):
        return math.sqrt(self.Ix / self.A)

    def __repr__(self):
        return f"{self.name} ({self.mass:.1f} kg/m)"


def eps(fy):
    return math.sqrt(250.0 / fy)


def i_section(name, D, bf, tf, tw, fy=250.0, welded=False):
    hw = D - 2 * tf
    A = 2 * bf * tf + hw * tw
    Ix = (bf * D ** 3 - (bf - tw) * hw ** 3) / 12.0
    Zex = Ix / (D / 2)
    Zpx = bf * tf * (D - tf) + tw * hw ** 2 / 4.0
    Iy = 2 * tf * bf ** 3 / 12.0 + hw * tw ** 3 / 12.0
    Zey = Iy / (bf / 2)
    Zpy = 2 * tf * bf ** 2 / 4.0 + hw * tw ** 2 / 4.0
    ry = math.sqrt(Iy / A)
    e = eps(fy)
    b_t = (bf / 2) / tf
    d_t = hw / tw
    fl = (8.4, 9.4, 13.6) if welded else (9.4, 10.5, 15.7)   # IS 800 Table 2
    if b_t <= fl[0] * e and d_t <= 84 * e:
        cls = "plastic"
    elif b_t <= fl[1] * e and d_t <= 105 * e:
        cls = "compact"
    elif b_t <= fl[2] * e and d_t <= 126 * e:
        cls = "semi-compact"
    else:
        cls = "slender"
    return Section(name, "I", A, Ix, Zex, Zpx, Iy, ry, fy, D, bf, tf, tw,
                   Av=D * tw, cls=cls, Zey=Zey, Zpy=Zpy, welded=welded,
                   buck_alpha=0.34 if not welded else 0.49)


def rhs(H, B, t, fy=310.0):
    name = f"{'SHS' if H == B else 'RHS'} {H:g}x{B:g}x{t:g}"
    h, b = H - 2 * t, B - 2 * t
    A = H * B - h * b
    Ix = (B * H ** 3 - b * h ** 3) / 12.0
    Iy = (H * B ** 3 - h * b ** 3) / 12.0
    Zpx = (B * H ** 2 - b * h ** 2) / 4.0
    Zpy = (H * B ** 2 - h * b ** 2) / 4.0
    e = eps(fy)
    bf_t = (B - 3 * t) / t
    dw_t = (H - 3 * t) / t
    if bf_t <= 29.3 * e and dw_t <= 84 * e:
        cls = "plastic"
    elif bf_t <= 33.5 * e and dw_t <= 105 * e:
        cls = "compact"
    elif bf_t <= 42 * e and dw_t <= 126 * e:
        cls = "semi-compact"
    else:
        cls = "slender"
    # cold-formed ERW hollow sections: buckling class 'b' (IS 800 Table 10)
    return Section(name, "RHS", A, Ix, Ix / (H / 2), Zpx, Iy, math.sqrt(Iy / A), fy,
                   D=H, bf=B, t=t, Av=A * H / (B + H), cls=cls,
                   Zey=Iy / (B / 2), Zpy=Zpy, buck_alpha=0.34)


def chs(D, t, fy=310.0):
    d = D - 2 * t
    A = math.pi / 4 * (D ** 2 - d ** 2)
    I = math.pi / 64 * (D ** 4 - d ** 4)
    Zp = (D ** 3 - d ** 3) / 6.0
    e2 = 250.0 / fy
    r = D / t
    if r <= 42 * e2:
        cls = "plastic"
    elif r <= 52 * e2:
        cls = "compact"
    elif r <= 146 * e2:
        cls = "semi-compact"
    else:
        cls = "slender"
    return Section(f"CHS {D:g}x{t:g}", "CHS", A, I, I / (D / 2), Zp, I, math.sqrt(I / A), fy,
                   D=D, t=t, Av=2 * A / math.pi, cls=cls, Zey=I / (D / 2), Zpy=Zp,
                   buck_alpha=0.34)


# ---- Libraries (nominal dimensions) -------------------------------------------------
# ISMB: D, bf, tf, tw  (IS 808 / SP 6(1) nominal)
ISMB = [i_section(f"ISMB {D}", D, bf, tf, tw) for D, bf, tf, tw in [
    (200, 100, 10.8, 5.7), (250, 125, 12.5, 6.9), (300, 140, 12.4, 7.5),
    (350, 140, 14.2, 8.1), (400, 140, 16.0, 8.9), (450, 150, 17.4, 9.4),
    (500, 180, 17.2, 10.2), (550, 190, 19.3, 11.2), (600, 210, 20.8, 12.0)]]
# Wide parallel-flange / heavy columns (WPB per IS 808 = HE series)
WPB = [i_section(n, D, bf, tf, tw) for n, D, bf, tf, tw in [
    ("ISHB 300", 300, 250, 10.6, 7.6), ("ISHB 350", 350, 250, 11.6, 8.3),
    ("ISHB 400", 400, 250, 12.7, 9.1), ("ISHB 450", 450, 250, 13.7, 9.8),
    ("WPB 260x260 (HE260A)", 250, 260, 12.5, 7.5), ("WPB 280x280 (HE280A)", 270, 280, 13.0, 8.0),
    ("WPB 300x300 (HE300A)", 290, 300, 14.0, 8.5), ("WPB 320x300 (HE320A)", 310, 300, 15.5, 9.0),
    ("WPB 300x300 (HE300B)", 300, 300, 19.0, 11.0), ("WPB 340x300 (HE340B)", 340, 300, 21.5, 12.0),
    ("WPB 360x300 (HE360B)", 360, 300, 22.5, 12.5)]]
RHS_LIST = [rhs(H, B, t) for H, B, t in [
    (96, 48, 3.2), (96, 48, 4.0), (122, 61, 3.6), (122, 61, 4.5), (145, 82, 4.8),
    (172, 92, 4.8), (200, 100, 4.0), (200, 100, 5.0), (200, 100, 6.0), (240, 120, 4.8),
    (240, 120, 6.0), (250, 150, 6.0), (300, 200, 6.0), (300, 200, 8.0)]]
SHS_LIST = [rhs(B, B, t) for B, t in [
    (40, 3.2), (49.5, 3.2), (60, 3.2), (72, 3.2), (72, 4.0), (91.5, 3.6), (91.5, 4.5),
    (100, 5.0), (113.5, 4.5), (113.5, 5.4), (132, 4.8), (132, 5.4), (150, 6.0),
    (180, 6.0), (180, 8.0)]]
CHS_LIST = [chs(D, t) for D, t in [
    (219.1, 5.9), (219.1, 8.0), (273.0, 6.3), (273.0, 8.0), (323.9, 6.3), (323.9, 8.0),
    (355.6, 8.0), (355.6, 10.0), (406.4, 8.0), (406.4, 10.0), (457.0, 10.0),
    (508.0, 10.0), (508.0, 12.0)]]


# ---- Capacities (IS 800:2007) ---------------------------------------------------------
def chi(lam, alpha):
    phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
    return min(1.0, 1.0 / (phi + math.sqrt(max(phi ** 2 - lam ** 2, 0.0))))


def Nd_compression(s, KL, r=None):
    """cl. 7.1.2.1 design compressive strength (N). r defaults to minimum radius."""
    r = r or min(s.rx, s.ry)
    lam = math.sqrt(s.fy * (KL / r) ** 2 / (math.pi ** 2 * E))
    return chi(lam, s.buck_alpha) * s.A * s.fy / GAMMA_M0, KL / r


def Nd_tension_yield(s):
    """cl. 6.2 gross-section yielding (N). Net-section rupture checked at connection stage."""
    return s.A * s.fy / GAMMA_M0


def beta_b(s):
    return 1.0 if s.cls in ("plastic", "compact") else s.Zex / s.Zpx


def Md(s, LLT=None):
    """cl. 8.2.1.2 / 8.2.2 design bending strength about major axis (N mm).
    LLT = None -> laterally supported (or closed section)."""
    bb = beta_b(s)
    Mrd = bb * s.Zpx * s.fy / GAMMA_M0
    if s.kind != "I" or not LLT:
        return Mrd, 1.0
    hf = s.D - s.tf
    # IS 800 Annex E, E-1.2 (simplified Mcr for doubly-symmetric I sections)
    Mcr = (math.pi ** 2 * E * s.Iy * hf / (2 * LLT ** 2)) * math.sqrt(
        1 + ((LLT / s.ry) / (hf / s.tf)) ** 2 / 20.0)
    lamLT = math.sqrt(bb * s.Zpx * s.fy / Mcr)
    aLT = 0.49 if s.welded else 0.21
    x = chi(lamLT, aLT)
    return min(Mrd, x * bb * s.Zpx * s.fy / GAMMA_M0), x


def Vd(s):
    """cl. 8.4.1 plastic shear resistance (N). Shear buckling flagged separately."""
    return s.Av * s.fy / (math.sqrt(3) * GAMMA_M0)
