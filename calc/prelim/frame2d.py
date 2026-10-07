"""Minimal 2D frame (direct stiffness) solver for preliminary / verification analysis.

Units are consistent user units (here: kN, m, kN/m^2 for E). Elements are Euler-Bernoulli
beam-columns with uniform transverse load in local coordinates. Self-check: sum of
reactions is reported so equilibrium can be confirmed for every run.
"""
import numpy as np


class Frame2D:
    def __init__(self):
        self.nodes = []        # (x, y)
        self.elems = []        # dict(i, j, E, A, I, w)  w = local transverse UDL (kN/m)
        self.supports = {}     # node -> (fx, fy, fr) booleans
        self.loads = {}        # node -> [Fx, Fy, M]

    def node(self, x, y):
        for k, (a, b) in enumerate(self.nodes):
            if abs(a - x) < 1e-9 and abs(b - y) < 1e-9:
                return k
        self.nodes.append((x, y))
        return len(self.nodes) - 1

    def elem(self, i, j, E, A, I, w=0.0, tag=""):
        self.elems.append(dict(i=i, j=j, E=E, A=A, I=I, w=w, tag=tag))
        return len(self.elems) - 1

    def support(self, n, fx=True, fy=True, fr=True):
        self.supports[n] = (fx, fy, fr)

    def load(self, n, Fx=0.0, Fy=0.0, M=0.0):
        l = self.loads.setdefault(n, [0.0, 0.0, 0.0])
        l[0] += Fx; l[1] += Fy; l[2] += M

    @staticmethod
    def _geom(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = np.hypot(dx, dy)
        return L, dx / L, dy / L

    def _k_local(self, e, L):
        E, A, I = e["E"], e["A"], e["I"]
        a, b, c, d = E * A / L, 12 * E * I / L ** 3, 6 * E * I / L ** 2, E * I / L
        return np.array([[a, 0, 0, -a, 0, 0],
                         [0, b, c, 0, -b, c],
                         [0, c, 4 * d, 0, -c, 2 * d],
                         [-a, 0, 0, a, 0, 0],
                         [0, -b, -c, 0, b, -c],
                         [0, c, 2 * d, 0, -c, 4 * d]])

    @staticmethod
    def _T(c, s):
        T = np.zeros((6, 6))
        R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T[:3, :3] = R; T[3:, 3:] = R
        return T

    def solve(self):
        n = len(self.nodes)
        K = np.zeros((3 * n, 3 * n)); F = np.zeros(3 * n)
        self._cache = []
        for e in self.elems:
            p, q = self.nodes[e["i"]], self.nodes[e["j"]]
            L, c, s = self._geom(p, q)
            kl = self._k_local(e, L); T = self._T(c, s)
            w = e["w"]
            feq = np.array([0, w * L / 2, w * L ** 2 / 12, 0, w * L / 2, -w * L ** 2 / 12])
            dofs = [3 * e["i"], 3 * e["i"] + 1, 3 * e["i"] + 2, 3 * e["j"], 3 * e["j"] + 1, 3 * e["j"] + 2]
            K[np.ix_(dofs, dofs)] += T.T @ kl @ T
            F[dofs] += T.T @ feq
            self._cache.append((kl, T, feq, dofs, L))
        for nd, l in self.loads.items():
            F[3 * nd:3 * nd + 3] += l
        fixed = []
        for nd, (fx, fy, fr) in self.supports.items():
            for k, flag in enumerate((fx, fy, fr)):
                if flag:
                    fixed.append(3 * nd + k)
        free = [d for d in range(3 * n) if d not in fixed]
        u = np.zeros(3 * n)
        u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
        R = K @ u - F
        self.u, self.R, self.F_applied = u, R, F
        self.forces = []
        for kl, T, feq, dofs, L in self._cache:
            f = kl @ (T @ u[dofs]) - feq       # local end forces acting on element
            self.forces.append(f)
        return self

    # --- result helpers -------------------------------------------------------------
    def reactions(self):
        return {nd: self.R[3 * nd:3 * nd + 3].copy() for nd in self.supports}

    def equilibrium(self):
        """Return (sum applied Fx, Fy) and (sum reactions Fx, Fy)."""
        Fx = self.F_applied[0::3].sum(); Fy = self.F_applied[1::3].sum()
        Rx = sum(r[0] for r in self.reactions().values())
        Ry = sum(r[1] for r in self.reactions().values())
        return (Fx, Fy), (Rx, Ry)

    def member_results(self, tag):
        """List of (elem index, N_i, V_i, M_i(sagging+), M_j(sagging+)) for elements with tag."""
        out = []
        for k, e in enumerate(self.elems):
            if e["tag"] == tag:
                f = self.forces[k]
                out.append((k, -f[0], f[1], -f[2], f[5]))
        return out

    def disp(self, nd):
        return self.u[3 * nd:3 * nd + 3]
