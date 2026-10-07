"""Phase 1 concept figures (schematic, NOT construction drawings)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "..", "docs", "figs")
os.makedirs(FIG, exist_ok=True)
R = json.load(open(os.path.join(HERE, "..", "..", "docs", "phase1_results.json")))
S = R["schemes"]
LX, LY = 16.0, 12.0
CX, CY = (3.5, 12.5), (3.5, 8.5)
SEC_X = [0.0, 1.75, 3.5, 5.75, 8.0, 10.25, 12.5, 14.25, 16.0]
C_PRI, C_SEC, C_PUR, C_COL, C_ENV = "#1f4e79", "#c55a11", "#8c8c8c", "#2e7d32", "#7030a0"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans"})


def outline(ax):
    ax.add_patch(Rectangle((0, 0), LX, LY, fill=False, lw=1.2, ec="k"))
    ax.set_xlim(-1.2, LX + 1.2); ax.set_ylim(-1.6, LY + 1.0); ax.set_aspect("equal"); ax.axis("off")


def cols(ax, kind="o"):
    for x in CX:
        for y in CY:
            if kind == "o":
                ax.add_patch(Circle((x, y), 0.25, fc=C_COL, ec="k", zorder=5))
            else:
                ax.add_patch(Rectangle((x - 0.18, y - 0.18), 0.36, 0.36, fc=C_COL, ec="k", zorder=5))


def zig(ax, p, q, color, amp=0.12, n=None):
    p, q = np.array(p), np.array(q)
    L = np.linalg.norm(q - p); n = n or int(L / 0.45)
    t = (q - p) / L; nrm = np.array([-t[1], t[0]])
    ax.plot(*np.c_[p + nrm * amp, q + nrm * amp], color=color, lw=1.0)
    ax.plot(*np.c_[p - nrm * amp, q - nrm * amp], color=color, lw=1.0)
    pts = [p + t * L * k / n + nrm * amp * (1 if k % 2 else -1) for k in range(n + 1)]
    ax.plot(*np.array(pts).T, color=color, lw=0.6)


def plan_A(ax, truss=False):
    outline(ax)
    for y in np.linspace(0, LY, 11):
        ax.plot([0, LX], [y, y], color=C_PUR, lw=0.5)
    for x in SEC_X:
        if truss:
            zig(ax, (x, 0), (x, LY), C_SEC, amp=0.10)
        else:
            ax.plot([x, x], [0, LY], color=C_SEC, lw=1.8)
    for y in CY:
        if truss:
            zig(ax, (0, y), (LX, y), C_PRI, amp=0.16)
        else:
            ax.plot([0, LX], [y, y], color=C_PRI, lw=3.2)
    cols(ax, "o" if truss else "s")


def plan_C(ax, marks=False):
    outline(ax)
    lb_y = list(np.linspace(0, LY, 11))   # 1.2 m grid as analysed
    for k, y in enumerate(lb_y):
        ax.plot([0, LX], [y, y], color=C_SEC, lw=1.4)
        if marks:
            ax.text(LX + 0.15, y, f"LB{k+1}", va="center", fontsize=6.5, color=C_SEC)
        for xs in (LX / 2 - 2.83, LX / 2 + 2.83):          # contraflexure splices
            ax.plot(xs, y, marker="|", ms=7, color="k", mew=1.2)
    for x in CX:
        ax.add_patch(Polygon([(x - 0.12, 0), (x - 0.18, CY[0]), (x - 0.21, LY / 2), (x - 0.18, CY[1]),
                              (x - 0.12, LY), (x + 0.12, LY), (x + 0.18, CY[1]), (x + 0.21, LY / 2),
                              (x + 0.18, CY[0]), (x + 0.12, 0)], fc=C_PRI, ec=C_PRI, alpha=0.9, zorder=4))
    for y in CY:
        ax.plot([CX[0], CX[1]], [y, y], color=C_PRI, lw=2.2, ls=(0, (4, 2)), zorder=4)
    cols(ax, "o")
    if marks:
        for k, x in enumerate(CX):
            ax.text(x, -0.55, f"TG{k+1}", ha="center", color=C_PRI, fontweight="bold")
        ax.text(LX / 2, CY[0] - 0.45, "HB1", ha="center", color=C_PRI)
        ax.text(LX / 2, CY[1] + 0.25, "HB2", ha="center", color=C_PRI)
        n = 1
        for y in CY:
            for x in CX:
                ax.text(x + 0.35, y + 0.3, f"C{n}", color=C_COL, fontweight="bold"); n += 1
        ax.annotate("", (0, -1.15), (LX, -1.15), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(LX / 2, -1.45, "16.0 m (3.5 + 9.0 + 3.5)", ha="center")
        ax.annotate("", (-0.7, 0), (-0.7, LY), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(-1.05, LY / 2, "12.0 m (3.5 + 5.0 + 3.5)", rotation=90, va="center")
        ax.text(LX / 2 + 2.83, LY + 0.35, "| = LB splice at contraflexure (1.67 m from support)",
                ha="center", fontsize=6.5)


def section_y(ax, scheme, D0=0.40):
    """Transverse section through column line (y-direction)."""
    ax.plot([-0.8, LY + 0.8], [0, 0], color="k", lw=1.2)
    ax.add_patch(Rectangle((0, 6.25), LY, 0.75, fill=False, ls="--", ec=C_ENV, lw=0.9))
    for y in CY:
        ax.add_patch(Rectangle((y - 0.17, 0), 0.34, 6.31, fc=C_COL, ec="k"))
    if scheme == "C":
        ys = np.linspace(0, LY, 97)
        def D(y):
            if y <= CY[0]: return D0 - 0.175 * (CY[0] - y) / 3.5
            if y >= CY[1]: return D0 - 0.175 * (y - CY[1]) / 3.5
            return D0 + 0.05 * (1 - abs(y - 6) / 2.5)
        top = np.array([6.31 + D(y) for y in ys])
        ax.fill_between(ys, 6.31, top, color=C_PRI, alpha=0.85)
        ax.plot(ys, top + 0.2, color=C_SEC, lw=0.8)
        for y in np.linspace(0, LY, 11):
            ax.add_patch(Rectangle((y - 0.05, 6.31 + D(y)), 0.10, 0.20, fc=C_SEC, ec="k", lw=0.3))
        ax.plot(ys, top + 0.235, color="#555", lw=1.2)
    else:
        Dm = 0.30 if scheme == "A" else 0.50
        if scheme == "A":
            ax.add_patch(Rectangle((0, 6.31), LY, Dm, fc=C_SEC, alpha=0.8))
        else:
            zig(ax, (0, 6.31 + Dm / 2), (LY, 6.31 + Dm / 2), C_SEC, amp=Dm / 2, n=26)
        for y in np.linspace(0, LY, 11):
            pk = (0.225 * (1 - abs(y - 6) / 6) if scheme == "A" else 0.0)
            ax.add_patch(Rectangle((y - 0.05, 6.31 + Dm + pk), 0.10, 0.096, fc=C_PUR, ec="k", lw=0.3))
    ax.set_xlim(-0.9, LY + 0.9); ax.set_ylim(-0.3, 7.6); ax.axis("off")
    ax.text(LY + 0.1, 6.62, "750", color=C_ENV, fontsize=7)
    ax.text(LY / 2, 3.0, "6.25 m clear", ha="center", fontsize=7)


def fig_schemes():
    fig, axs = plt.subplots(2, 3, figsize=(11.7, 7.2), gridspec_kw=dict(height_ratios=[1.25, 1]))
    titles = {
        "A": "SCHEME A - Rolled-I two-way grillage\n(ISMB primaries + secondaries, WPB columns)",
        "B": "SCHEME B - Shallow tubular truss grid\n(SHS Warren trusses both ways, CHS columns)",
        "C1": "SCHEME C - Tapered tree-girders + RHS purlin-beams\n(2 TG + 11 LB + 2 HB, CHS columns)"}
    plan_A(axs[0, 0]); plan_A(axs[0, 1], truss=True); plan_C(axs[0, 2])
    for k, key in enumerate(("A", "B", "C1")):
        axs[0, k].set_title(titles[key], fontsize=8.5, fontweight="bold")
        r = S[key]
        axs[0, k].text(LX / 2, -1.2, f"Steel {r['total_kg']/1000:.1f} t  |  {r['kg_m2']:.1f} kg/m$^2$",
                       ha="center", fontsize=8.5, fontweight="bold")
        section_y(axs[1, k], key[0], D0=S["C1"]["TG"]["D0"])
    axs[1, 0].set_title("Section through column line (y-direction) - purlins on packers", fontsize=7.5)
    axs[1, 1].set_title("Section - truss top chord follows drainage", fontsize=7.5)
    axs[1, 2].set_title("Section - moment-shaped tapered girder gives the fall", fontsize=7.5)
    fig.suptitle("PHASE 1 - Structural concept alternatives (schematic, not to scale)", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_scheme_alternatives.png"), dpi=170); plt.close(fig)


def fig_selected():
    r = S["C1"]; tg = r["TG"]
    fig = plt.figure(figsize=(11.7, 8.3))
    ax1 = fig.add_axes([0.02, 0.34, 0.52, 0.56]); plan_C(ax1, marks=True)
    ax1.set_title("ROOF FRAMING PLAN (schematic)", fontweight="bold")
    ax2 = fig.add_axes([0.56, 0.52, 0.42, 0.36])
    D0 = tg["D0"]
    section_y(ax2, "C", D0=D0)
    ax2.set_title(f"SECTION A-A through TG (y-direction)\nTG: {tg['bf']}x{tg['tf']} flanges, {tg['tw']} web, "
                  f"D = {tg['D_tip']*1000:.0f} / {D0*1000:.0f} / {tg['D_ridge']*1000:.0f} mm (tip / column / ridge)",
                  fontsize=8, fontweight="bold")
    for y, lab in ((1.75, "fall 1:20 -> gutter"), (6.0, "ridge"), (10.25, "fall 1:20 -> gutter")):
        ax2.text(y, 7.35, lab, ha="center", fontsize=6.5)
    ax2.text(CY[0], -0.25, "C1", ha="center"); ax2.text(CY[1], -0.25, "C3", ha="center")
    ax3 = fig.add_axes([0.56, 0.10, 0.42, 0.36])
    ax3.plot([-0.8, LX + 0.8], [0, 0], "k", lw=1.2)
    ax3.add_patch(Rectangle((0, 6.25), LX, 0.75, fill=False, ls="--", ec=C_ENV))
    for x in CX:
        ax3.add_patch(Rectangle((x - 0.17, 0), 0.34, 6.31, fc=C_COL, ec="k"))
        ax3.add_patch(Rectangle((x - 0.125, 6.31), 0.25, D0, fc=C_PRI))
    ax3.add_patch(Rectangle((CX[0], 6.31 + D0 - 0.25), CX[1] - CX[0], 0.25, fc=C_PRI, alpha=0.5))
    ax3.add_patch(Rectangle((0, 6.31 + D0), LX, 0.20, fc=C_SEC, alpha=0.9))
    for xs in (LX / 2 - 2.83, LX / 2 + 2.83):
        ax3.plot([xs, xs], [6.31 + D0 - 0.05, 6.31 + D0 + 0.25], "k", lw=1.2)
    ax3.text(LX / 2, 6.31 + D0 + 0.32, f"LB {r['LB']} continuous, spliced at contraflexure", ha="center", fontsize=7)
    ax3.text(LX / 2, 6.31 + D0 - 0.42, f"HB {r['COL']['head_beam']} (moment-connected)", ha="center", fontsize=7)
    ax3.text(LX / 2, 3.0, "9.0 m column grid  |  6.25 m clear", ha="center", fontsize=7)
    ax3.set_xlim(-0.9, LX + 0.9); ax3.set_ylim(-0.3, 7.6); ax3.axis("off")
    ax3.set_title(f"SECTION B-B through column line (x-direction)  |  Columns {r['COL']['section']}",
                  fontsize=8, fontweight="bold")
    ax4 = fig.add_axes([0.03, 0.03, 0.50, 0.30]); ax4.axis("off")
    stack = [("Roof sheet (rib)", 35, "#999"), (f"Purlin-beam LB ({r['LB_h']:.0f} deep)", r["LB_h"], C_SEC),
             (f"Tapered girder TG at ridge ({tg['D_ridge']*1000:.0f})", tg["D_ridge"] * 1000, C_PRI),
             ("Soffit sheet + fixing", 60, "#bbb")]
    z = 0; tot = sum(s[1] for s in stack)
    for name, d, c in reversed(stack):
        ax4.add_patch(Rectangle((0, z), 1.2, d, fc=c, ec="k", lw=0.5)); ax4.text(1.3, z + d / 2, f"{name}: {d:.0f} mm", va="center")
        z += d
    ax4.plot([-0.2, -0.2], [0, 750], color=C_ENV, lw=1.5); ax4.text(-0.3, 375, "750 mm envelope", rotation=90, va="center", ha="right", color=C_ENV)
    ax4.text(1.3, 760, f"Stack at ridge = {tot:.0f} mm <= 750 mm", fontweight="bold")
    ax4.set_xlim(-0.8, 6); ax4.set_ylim(-20, 820)
    fig.suptitle("SCHEME C (selected) - Tapered tree-girder canopy: concept layout", fontweight="bold", y=0.985)
    fig.savefig(os.path.join(FIG, "fig2_selected_scheme_layout.png"), dpi=170); plt.close(fig)


def fig_iso():
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    r = S["C1"]; D0 = r["TG"]["D0"]
    fig = plt.figure(figsize=(9, 6.5)); ax = fig.add_subplot(111, projection="3d")
    z0 = 6.31
    def D(y):
        if y <= CY[0]: return D0 - 0.175 * (CY[0] - y) / 3.5
        if y >= CY[1]: return D0 - 0.175 * (y - CY[1]) / 3.5
        return D0 + 0.05 * (1 - abs(y - 6) / 2.5)
    ys = np.linspace(0, LY, 49)
    for x in CX:
        ax.plot([x, x], [CY[0], CY[0]], [0, z0], color=C_COL, lw=5)
        ax.plot([x, x], [CY[1], CY[1]], [0, z0], color=C_COL, lw=5)
        ax.plot([x] * len(ys), ys, [z0] * len(ys), color=C_PRI, lw=2)
        ax.plot([x] * len(ys), ys, [z0 + D(y) for y in ys], color=C_PRI, lw=2)
        for y in ys[::4]:
            ax.plot([x, x], [y, y], [z0, z0 + D(y)], color=C_PRI, lw=0.6)
    for y in CY:
        ax.plot([CX[0], CX[1]], [y, y], [z0 + D0 - 0.15] * 2, color=C_PRI, lw=2.5)
    for y in np.linspace(0, LY, 11):
        ax.plot([0, LX], [y, y], [z0 + D(y) + 0.1] * 2, color=C_SEC, lw=1.4)
    for (xa, ya), (xb, yb) in (((0, 0), (LX, 0)), ((LX, 0), (LX, LY)), ((LX, LY), (0, LY)), ((0, LY), (0, 0))):
        for zz in (6.25, 7.0):
            ax.plot([xa, xb], [ya, yb], [zz, zz], color=C_ENV, lw=0.8, ls="--")
    ax.set_box_aspect((16, 12, 7)); ax.view_init(24, -58)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.set_zlabel("z (m)")
    ax.set_title("SCHEME C - isometric wireframe (fascia envelope dashed)", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_selected_scheme_iso.png"), dpi=170); plt.close(fig)


if __name__ == "__main__":
    fig_schemes(); fig_selected(); fig_iso(); print("figures written to", FIG)
