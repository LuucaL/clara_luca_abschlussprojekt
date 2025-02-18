import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def build_points():
    # Standard-Punkte mal als Beispiel 
    return {
        "p0": np.array([  0.0,   0.0]),
        "p1": np.array([ 10.0,  35.0]),
        "p2": np.array([-25.0,  10.0]),
        "p3": np.array([  5.0, -30.0])
    }

def build_matrix_4bars():
    # 8x8-Matrix A für vier Stäbe (p0->p1, p1->p2, p2->p3, p3->p0).
    
    A = np.zeros((8, 8))
    # Stab 1: p0 -> p1
    A[0, 0] =  1.0; A[0, 2] = -1.0
    A[1, 1] =  1.0; A[1, 3] = -1.0
    # Stab 2: p1 -> p2
    A[2, 2] =  1.0; A[2, 4] = -1.0
    A[3, 3] =  1.0; A[3, 5] = -1.0
    # Stab 3: p2 -> p3
    A[4, 4] =  1.0; A[4, 6] = -1.0
    A[5, 5] =  1.0; A[5, 7] = -1.0
    # Stab 4: p3 -> p0
    A[6, 6] =  1.0; A[6, 0] = -1.0
    A[7, 7] =  1.0; A[7, 1] = -1.0
    return A

def compute_bar_lengths(A, x):
    # A*x -> Differenzvektoren, daraus euklidische Längen der 4 Stäbe.
    diffs = A @ x  # Vektor der Länge 8
    diffs_2d = diffs.reshape(-1, 2)  # (4,2)
    lengths = np.linalg.norm(diffs_2d, axis=1)
    return lengths

def run_4bar_calculation(points):
    # Beispiel-Funktion zum direkten Abrufen
    x = np.array([
        points["p0"][0], points["p0"][1],
        points["p1"][0], points["p1"][1],
        points["p2"][0], points["p2"][1],
        points["p3"][0], points["p3"][1],
    ])
    A = build_matrix_4bars()
    lengths = compute_bar_lengths(A, x)
    return lengths



def circle_intersections(c1, r1, c2, r2):
    """
    Berechnet die Schnittpunkte zweier Kreise:
      - Kreis 1: Mittelpunkt c1, Radius r1
      - Kreis 2: Mittelpunkt c2, Radius r2
    Gibt eine Liste von 0, 1 oder 2 2D-Punkten zurück.
    """
    (x1, y1), (x2, y2) = c1, c2
    d = np.hypot(x2 - x1, y2 - y1)  # Abstand der Mittelpunkte

    # Kein Schnitt (zu weit auseinander oder einer ist im anderen)
    if d > (r1 + r2) or d < abs(r1 - r2):
        return []
    # Zufall: identische Kreise (unendlich viele Schnittpunkte)
    if d == 0 and abs(r1 - r2) < 1e-9:
        return []

    # Einfache Geometrie
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(r1**2 - a**2, 0.0))  # kann bei float-Fehler minimal negativ sein

    # Mittelpunkt der Sehne
    xm = x1 + a * (x2 - x1) / d
    ym = y1 + a * (y2 - y1) / d

    # Falls h==0, genau 1 Schnittpunkt (Tangente)
    if abs(h) < 1e-12:
        return [(xm, ym)]

    # Sonst 2 Schnittpunkte
    rx = -(y2 - y1) * (h / d)
    ry =  (x2 - x1) * (h / d)
    p1 = (xm + rx, ym + ry)
    p2 = (xm - rx, ym - ry)
    return [p1, p2]

def animate_4bar_kinematics(points):
    trajectory = []
    """
    Erwartet Dictionary 'points' mit p0, p1, p2, p3.
    p0 und p3 werden als fix angenommen.
    p1 und p2 sind Gelenkpunkte. 
    Wir drehen p1 um p0, und p2 findet sich durch Koppeln an p1->p2 und p3->p2.
    """

    p0 = points["p0"]
    p1_init = points["p1"]
    p2_init = points["p2"]
    p3 = points["p3"]

    # Vier Stablängen:
    L0 = np.linalg.norm(p1_init - p0)   # p0->p1 (driver)
    L1 = np.linalg.norm(p2_init - p1_init)  # p1->p2 (coupler)
    L2 = np.linalg.norm(p2_init - p3)   # p2->p3 (rocker)
    L3 = np.linalg.norm(p3 - p0)        # p3->p0 (ground)

    # Grashof-Check (vereinfacht):
    lengths_sorted = sorted([L0, L1, L2, L3])
    if lengths_sorted[0] + lengths_sorted[1] > lengths_sorted[2] + lengths_sorted[3]:
        print("WARNUNG: Grashof-Kriterium nicht erfüllt. Evtl. keine vollständige Rotation möglich.")

    # Animation-Parameter
    NUM_FRAMES = 80
    FPS = 10

    # Matplotlib-Setup
    fig, ax = plt.subplots()
    ax.set_title("Echte 4-Gelenk-Kinematik")
    ax.set_aspect("equal", adjustable="box")  # 1:1
    # Limits kannst du anpassen oder automatisiert setzen
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)

    # Marker: p0, p1, p2, p3
    (ln_p0,) = ax.plot([], [], "ro", ms=8)  # fixed ground pivot
    (ln_p1,) = ax.plot([], [], "bo", ms=8)
    (ln_p2,) = ax.plot([], [], "go", ms=8)
    (ln_p3,) = ax.plot([], [], "ro", ms=8)  # fixed ground pivot

    # Stäbe als Linien
    (bar_01,) = ax.plot([], [], "k-", lw=2)
    (bar_12,) = ax.plot([], [], "k-", lw=2)
    (bar_23,) = ax.plot([], [], "k-", lw=2)
    (bar_30,) = ax.plot([], [], "k-", lw=2)

    

    def init():
        ln_p0.set_data([], [])
        ln_p1.set_data([], [])
        ln_p2.set_data([], [])
        ln_p3.set_data([], [])
        bar_01.set_data([], [])
        bar_12.set_data([], [])
        bar_23.set_data([], [])
        bar_30.set_data([], [])
        return (ln_p0, ln_p1, ln_p2, ln_p3,
                bar_01, bar_12, bar_23, bar_30)

    def update(frame):
        # Drehe p1 um p0
        alpha = 2 * np.pi * frame / NUM_FRAMES  # 0..2pi
        px1 = p0[0] + L0 * np.cos(alpha)
        py1 = p0[1] + L0 * np.sin(alpha)
        p1 = np.array([px1, py1])

        # Finde p2 als Schnittpunkt:
        #  - Kreis um p1, Radius = L1
        #  - Kreis um p3, Radius = L2
        hits = circle_intersections(p1, L1, p3, L2)
        if len(hits) == 0:
            # kein Schnitt -> Stabkonfiguration nicht möglich
            p2 = np.array([np.nan, np.nan])
        else:
            # nimm z.B. den ERSTEN Schnitt
            p2 = np.array(hits[0])
            # Optional: je nach Mechanismus (Ober-/Unterbau), kannst du hits[1] nehmen.

        trajectory.append([p2[0], p2[1]])    

        # Updaten der Scatter/Line-Daten
        ln_p0.set_data([p0[0]], [p0[1]])
        ln_p1.set_data([p1[0]], [p1[1]])
        ln_p2.set_data([p2[0]], [p2[1]])
        ln_p3.set_data([p3[0]], [p3[1]])

        bar_01.set_data([p0[0], p1[0]], [p0[1], p1[1]])
        bar_12.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        bar_23.set_data([p2[0], p3[0]], [p2[1], p3[1]])
        bar_30.set_data([p3[0], p0[0]], [p3[1], p0[1]])

        return (ln_p0, ln_p1, ln_p2, ln_p3,
                bar_01, bar_12, bar_23, bar_30)

    ani = FuncAnimation(
        fig, update, 
        frames=NUM_FRAMES, 
        init_func=init,
        interval=1000//FPS, 
        blit=True
    )

    # In GIF speichern
    import tempfile, os, io
    tmpfile = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp_filename = tmpfile.name
    tmpfile.close()

    ani.save(tmp_filename, writer=PillowWriter(fps=FPS))
    with open(tmp_filename, "rb") as f:
        gif_bytes = f.read()
    os.remove(tmp_filename)
    plt.close(fig)

    return io.BytesIO(gif_bytes),trajectory
