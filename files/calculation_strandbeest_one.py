import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import least_squares

# ---------------------------------------------------------
# 1) Ursprüngliche Koordinaten (werden nur genutzt, um Stablängen zu messen)
# ---------------------------------------------------------
Y = (-3, 0)     
Z = (10.1, 0)     
X_0 = (15.6, 0.5)
W = (3.3, 9)
V = (-12.4, 5.7)
T = (-8.3, -4.5)
U = (1.1, -10.2)
S = (-2.9, -23.7)

# Wir nehmen an, dass X, W, V, T, U, S alle "frei" beweglich sind
# – nur Y und Z sind starr, X "zwingt" sich allerdings auf eine Kreisbahn.
fixed_points = {
    "Y": np.array(Y, dtype=float),
    "Z": np.array(Z, dtype=float)
}

# Startwerte der "frei beweglichen" (einschl. X):
init_positions = {
    "X": np.array(X_0, dtype=float),
    "W": np.array(W,   dtype=float),
    "V": np.array(V,   dtype=float),
    "T": np.array(T,   dtype=float),
    "U": np.array(U,   dtype=float),
    "S": np.array(S,   dtype=float),
}

# ---------------------------------------------------------
# 2) Stäbe (Edges) und deren Längen (aus den Originaldaten)
# ---------------------------------------------------------
# Wichtig: Alle Verbindungen, deren Länge fix bleiben soll.
# Sie sagten z.B.:
edges = [
    ("Y", "V"),  
    ("V", "W"),
    ("W", "X"), 
    ("X", "Z"),  
    ("Y", "W"),
    ("T", "U"),
    ("U", "S"),
    ("S", "T"),  
    ("V", "T"),  
    ("Y", "U"),
    ("U", "X"),
]

# Hilfsfunktion zum Distanzberechnen
def dist(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

# Wir messen nun die originalen Längen einmalig und speichern sie in einem Dictionary.
rod_lengths = {}
for (p1, p2) in edges:
    p1_pos = init_positions.get(p1, fixed_points.get(p1))
    p2_pos = init_positions.get(p2, fixed_points.get(p2))
    length = dist(p1_pos, p2_pos)
    rod_lengths[(p1, p2)] = length
    rod_lengths[(p2, p1)] = length  # gleiche Länge in beiden Richtungen

# ---------------------------------------------------------
# 3) X rotiert um Z: Definiere Radius & Trajektorie
# ---------------------------------------------------------
R = dist(Z, X_0)  # Kreisradius (aus originaler Position)
def crank_position(theta_deg):
    """Setzt X auf den Kreis um Z mit Radius R."""
    theta = math.radians(theta_deg)
    cx = Z[0] + R * math.cos(theta)
    cy = Z[1] + R * math.sin(theta)
    return np.array([cx, cy], dtype=float)

# ---------------------------------------------------------
# 4) Solver-Funktion: given X, Y, Z => bestimme W, V, T, U, S
# ---------------------------------------------------------
# Wir werden die "frei beweglichen" Punkte (W, V, T, U, S) in einem langen Vektor packen.
# Die Funktion 'constraint_equations' gibt Differenzen von SOLL-Länge - IST-Länge zurück.
# least_squares versucht diese auf 0 zu bringen.

free_labels = ["W", "V", "T", "U", "S"]  # Reihenfolge im Parametervektor

def pack_positions(positions_dict):
    """
    positions_dict: z.B. {"W": (xw,yw), "V": (xv,yv), ...}
    Liefert ein np.array in der Reihenfolge free_labels = [W, V, T, U, S].
    """
    data = []
    for label in free_labels:
        data.append(positions_dict[label][0])
        data.append(positions_dict[label][1])
    return np.array(data, dtype=float)

def unpack_positions(param_vector):
    """
    param_vector: 1D array, len=10 (5 Punkte * 2 Koordinaten)
    -> dict {"W": (xw,yw), "V": (xv,yv), ...}
    """
    out = {}
    idx = 0
    for label in free_labels:
        out[label] = np.array([param_vector[idx], param_vector[idx+1]])
        idx += 2
    return out

def constraint_equations(param_vector, X_current):
    """
    param_vector: enthält (xW, yW, xV, yV, xT, yT, xU, yU, xS, yS)
    X_current: Koord. von X im aktuellen Frame (vorgegeben)
    Y, Z: fest aus fixed_points
    rod_lengths: globale dict mit SOLL-Längen
    
    --> Rückgabe: array der Abweichungen (SOLL - IST) für alle Edges
    """
    free_pos = unpack_positions(param_vector)

    # Alle absoluten Positionen in einem dict:
    # Y und Z sind fest, X ist übergeben (Kreis), Rest "free_pos"
    all_pos = {}
    all_pos.update(fixed_points)  # Y, Z
    all_pos["X"] = X_current
    for lbl in free_labels:
        all_pos[lbl] = free_pos[lbl]

    residuals = []
    for (p1, p2) in edges:
        soll = rod_lengths[(p1, p2)]
        ist = dist(all_pos[p1], all_pos[p2])
        residuals.append(ist - soll)
    return residuals

# ---------------------------------------------------------
# 5) Animation mit matplotlib
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(6,6))
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-30, 30)
ax.set_ylim(-35, 35)
ax.set_title("Nur Y und Z fest, X kreist — alle anderen Punkte frei (Stäbe mit fixer Länge)")
ax.grid(True)

# Linienobjekte (eines pro Kante)
lines = []
for _ in edges:
    line, = ax.plot([], [], 'k-', lw=2)
    lines.append(line)

# Punkt-Markierungen (+ Label) für ALLE labels (inkl. Y,Z,X)
all_labels = list(fixed_points.keys()) + ["X"] + free_labels  # "Y","Z","X","W","V","T","U","S"
point_markers = {}
for label in all_labels:
    pm, = ax.plot([], [], 'ro')  # roter Marker
    txt = ax.text(0,0, label, fontsize=8)
    point_markers[label] = (pm, txt)

# ---- wir pflegen eine "globale" Variable als Startwert für den Solver
current_free_positions = dict((k,v.copy()) for (k,v) in init_positions.items() if k in free_labels)

def init():
    """Erst-Frame: alles leer"""
    for line in lines:
        line.set_data([], [])
    for (pm, txt) in point_markers.values():
        pm.set_data([], [])
        txt.set_position((0,0))
    return list(point_markers.values()) + lines

def update(frame_deg):
    """
    1) Setze X auf Kreis
    2) Löse Constraints => W, V, T, U, S
    3) Zeichne
    """
    global current_free_positions

    # 1) X auf aktuellen Winkel:
    X_curr = crank_position(frame_deg)

    # 2) Lösen: Startwert = current_free_positions aus dem letzten Frame
    start_vec = pack_positions(current_free_positions)

    # Wir nutzen least_squares, um Abweichungen (SOLL - IST) -> 0 zu minimieren
    sol = least_squares(
        fun=constraint_equations,
        x0=start_vec,
        args=(X_curr,),
        ftol=1e-7, xtol=1e-7, gtol=1e-7,
        max_nfev=1000
    )

    free_solution = unpack_positions(sol.x)
    # Im nächsten Frame nehmen wir diese Lösung als Startwert (=> "kontinuierliche" Bewegung)
    current_free_positions = free_solution

    # 3) Zeichnen
    # 3a) Dictionary aller Punkte
    all_pos = {}
    all_pos.update(fixed_points)   # Y, Z
    all_pos["X"] = X_curr
    for lbl in free_labels:
        all_pos[lbl] = free_solution[lbl]

    # 3b) Linien updaten
    for i, (p1, p2) in enumerate(edges):
        x1, y1 = all_pos[p1]
        x2, y2 = all_pos[p2]
        lines[i].set_data([x1, x2], [y1, y2])

    # 3c) Punkte & Labels
    for label, (pm, txt) in point_markers.items():
        (xx, yy) = all_pos[label]
        pm.set_data([xx], [yy])
        txt.set_position((xx+0.3, yy+0.3))

    # Rückgabe: alle geänderten Artists
    return list(point_markers.values()) + lines

ani = animation.FuncAnimation(
    fig,
    update,
    frames=np.arange(0, 360, 2),  # 0..358 in 2°-Schritten
    init_func=init,
    blit=False,
    interval=50
)

plt.show()
