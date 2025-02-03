import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def animate_4bar_gif(points):

    NUM_FRAMES = 80
    FPS = 10

    # Kreise p2 um p1
    p0 = points["p0"]
    p1 = points["p1"]
    p2_start = points["p2"]

    start_vec = p2_start - p1
    radius = np.linalg.norm(start_vec)
    start_angle = np.arctan2(start_vec[1], start_vec[0])
    dtheta = 2*np.pi / NUM_FRAMES

    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlim(-50, 130)
    ax.set_ylim(-40, 100)
    ax.set_title("Viergelenk-Simulation")

    (pnt0,) = ax.plot([], [], "ro", ms=8)
    (pnt1,) = ax.plot([], [], "ro", ms=8)
    (pnt2,) = ax.plot([], [], "ro", ms=8)
    (lin01,) = ax.plot([], [], "b-", lw=2)
    (lin12,) = ax.plot([], [], "b-", lw=2)

    def init():
        pnt0.set_data([], [])
        pnt1.set_data([], [])
        pnt2.set_data([], [])
        lin01.set_data([], [])
        lin12.set_data([], [])
        return (pnt0, pnt1, pnt2, lin01, lin12)

    def update(frame):
        angle = start_angle + frame*dtheta
        p2x = p1[0] + radius*np.cos(angle)
        p2y = p1[1] + radius*np.sin(angle)

        # Einzelne Punkte -> Listen (Länge 1)
        pnt0.set_data([p0[0]], [p0[1]])
        pnt1.set_data([p1[0]], [p1[1]])
        pnt2.set_data([p2x],   [p2y])

        # Linien -> 2 Punkte
        lin01.set_data([p0[0], p1[0]], [p0[1], p1[1]])
        lin12.set_data([p1[0], p2x],   [p1[1], p2y])

        return (pnt0, pnt1, pnt2, lin01, lin12)

    anim = FuncAnimation(
        fig,
        update,
        frames=NUM_FRAMES,
        interval=1000//FPS,
        init_func=init,
        blit=True
    )

    # Windows-kompatibler Weg
    tmpfile = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp_filename = tmpfile.name
    tmpfile.close()  # Schließt die Datei, Windows hebt Lock auf

    # Jetzt kann Matplotlib die Datei öffnen
    anim.save(tmp_filename, writer=PillowWriter(fps=FPS))

    # Einlesen in Bytes
    with open(tmp_filename, "rb") as f:
        gif_bytes = f.read()

    # Datei entfernen
    os.remove(tmp_filename)

    plt.close(fig)
    return io.BytesIO(gif_bytes)
