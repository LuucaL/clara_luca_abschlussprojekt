import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

# --- Festpunkte ---
Y = (-3, 0)     
Z = (10, 0)     # Drehzentrum der Kurbel
W = (3.3, 9)
V = (-12.4, 5.7)
T = (-8.3, -4.5)
U = (1.1, -10.2)
S = (-2.9, -23.7)

# Ursprüngliches X (Startposition)
X_start = (15.6, 0.5)

# Kanten (Stäbe) - beachten Sie, dass hier "X" als Label auftaucht
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

# Dictionary der festen Punkte (ohne X, da X animiert wird):
fixed_points = {
    "Y": Y,
    "Z": Z,
    "W": W,
    "V": V,
    "T": T,
    "U": U,
    "S": S
}

# ------------------------ Animation vorbereiten ------------------------

# Abstand (Radius) zwischen Z und dem ursprünglichen X:
R = math.dist(Z, X_start)  # ~5.62

# Abbildung: frames --> (x,y) von X
def compute_X(theta_degrees):
    """Berechnet die aktuelle Position von X in Abhängigkeit des Winkels (Grad)."""
    theta = math.radians(theta_degrees)
    x = Z[0] + R * math.cos(theta)
    y = Z[1] + R * math.sin(theta)
    return (x, y)

# ------------------------ Plot-Grundgerüst ------------------------

fig, ax = plt.subplots(figsize=(6,6))
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-30, 30)
ax.set_ylim(-35, 35)
ax.set_title("Strandbeest-Grundskizze (Z->X als Kurbel)")
ax.grid(True)

# Wir erzeugen jeweils ein Line2D-Objekt pro Kante:
lines = []
for _ in edges:
    line, = ax.plot([], [], 'k-', lw=2)
    lines.append(line)

# Punkte und Labels als Marker + Textobjekt
point_markers = {}
for label in list(fixed_points.keys()) + ["X"]:
    pm, = ax.plot([], [], 'ro')  # ein roter Punkt
    txt = ax.text(0, 0, label, fontsize=12)
    point_markers[label] = (pm, txt)

# ------------------------ Animationsfunktionen ------------------------

def init():
    """Init-Funktion für FuncAnimation (leere Startwerte)."""
    for line in lines:
        line.set_data([], [])
    for (pm, txt) in point_markers.values():
        pm.set_data([], [])
        txt.set_position((0,0))
    return list(point_markers.values()) + lines

def update(frame):
    """Wird für jeden Frame aufgerufen: frame ist hier ein Winkel in Grad."""
    # 1) X-Koordinate aktualisieren:
    X_current = compute_X(frame)

    # 2) Neues Dictionary aller Punkte:
    all_points = dict(fixed_points)
    all_points["X"] = X_current

    # 3) Linien-Koordinaten aktualisieren
    for i, (p1, p2) in enumerate(edges):
        x1, y1 = all_points[p1]
        x2, y2 = all_points[p2]
        lines[i].set_data([x1, x2], [y1, y2])

    # 4) Punkt-Marker und Label anpassen
    for label, (pm, txt) in point_markers.items():
        xx, yy = all_points[label]
        pm.set_data(xx, yy)
        txt.set_position((xx+0.5, yy+0.5))

    # Muss die geänderten Artists zurückgeben
    return list(point_markers.values()) + lines

# ------------------------ Animation starten ------------------------

# frames=range(0, 360, 2) => rotiere X in 2°-Schritten einmal rundherum
ani = animation.FuncAnimation(
    fig,
    update,
    frames=range(0, 360, 2),
    init_func=init,
    blit=False,    # bei Bedarf True setzen, wenn das Backend es unterstützt
    interval=50    # Zeit zwischen Frames in ms
)

plt.show()
