import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def circle_intersections(c1, r1, c2, r2, last_p2=None):
    """Berechnet die Schnittpunkte zweier Kreise und wählt den kontinuierlichsten Punkt."""
    (x1, y1), (x2, y2) = c1, c2
    d = np.hypot(x2 - x1, y2 - y1)
    
    if d > (r1 + r2) or d < abs(r1 - r2):
        return last_p2  # Keine gültigen Schnittpunkte -> alten Wert behalten
    
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(r1**2 - a**2, 0.0))
    xm = x1 + a * (x2 - x1) / d
    ym = y1 + a * (y2 - y1) / d
    
    rx = -(y2 - y1) * (h / d)
    ry = (x2 - x1) * (h / d)
    
    p1 = np.array([xm + rx, ym + ry])
    p2 = np.array([xm - rx, ym - ry])
    
    if last_p2 is not None:
        return p1 if np.linalg.norm(last_p2 - p1) < np.linalg.norm(last_p2 - p2) else p2
    
    return p1  # Falls kein vorheriger Punkt existiert

def animate_crank_kinematics(points, show_path=False, save_filename=None):
    p0 = points["p0"]  
    p1_init = points["p1"]  
    p2_init = points["p2"]  
    p3 = points["p3"]  
    
    L0 = np.linalg.norm(p1_init - p0)  
    L1 = np.linalg.norm(p2_init - p1_init) 
    L2 = np.linalg.norm(p2_init - p3) 
    
    NUM_FRAMES = 120
    FPS = 20
    
    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-80, 120)
    ax.set_ylim(-80, 80)
    
    ln_p0, = ax.plot([], [], "ro", ms=8)
    ln_p1, = ax.plot([], [], "bo", ms=8)
    ln_p2, = ax.plot([], [], "go", ms=8)
    ln_p3, = ax.plot([], [], "ro", ms=8)
    bar_01, = ax.plot([], [], "k-", lw=2)
    bar_12, = ax.plot([], [], "k-", lw=2)
    bar_23, = ax.plot([], [], "k-", lw=2)
    
    p1_path, p2_path = None, None
    if show_path:
        p1_path, = ax.plot([], [], "b--", lw=1)
        p2_path, = ax.plot([], [], "g--", lw=1)
    
    trajectory, trajectory_p1 = [], []
    last_p2 = p2_init.copy()
    
    def init():
        artists = [ln_p0, ln_p1, ln_p2, ln_p3, bar_01, bar_12, bar_23]
        if show_path:
            artists += [p1_path, p2_path]
        return artists
    
    def update(frame):
        nonlocal last_p2
        alpha = 2 * np.pi * frame / NUM_FRAMES
        
        px1 = p0[0] + L0 * np.cos(alpha)
        py1 = p0[1] + L0 * np.sin(alpha)
        p1 = np.array([px1, py1])
        
        p2 = circle_intersections(p1, L1, p3, L2, last_p2)
        last_p2 = p2  # Wert immer aktualisieren
        
        if show_path:
            trajectory.append(p1.tolist())
            trajectory_p1.append(p2.tolist())
            p1_path.set_data(*zip(*trajectory))
            p2_path.set_data(*zip(*trajectory_p1))
        
        ln_p0.set_data([p0[0]], [p0[1]])
        ln_p1.set_data([p1[0]], [p1[1]])
        ln_p2.set_data([p2[0]], [p2[1]])
        ln_p3.set_data([p3[0]], [p3[1]])
        bar_01.set_data([p0[0], p1[0]], [p0[1], p1[1]])
        bar_12.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        bar_23.set_data([p2[0], p3[0]], [p2[1], p3[1]])
        
        artists = [ln_p0, ln_p1, ln_p2, ln_p3, bar_01, bar_12, bar_23]
        if show_path:
            artists += [p1_path, p2_path]
        return artists
    
    ani = FuncAnimation(fig, update, frames=NUM_FRAMES, init_func=init, interval=1000//FPS, blit=True)
    
    tmpfile = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp_filename = tmpfile.name
    tmpfile.close()
    ani.save(tmp_filename, writer=PillowWriter(fps=FPS))
    with open(tmp_filename, "rb") as f:
        gif_bytes = f.read()
    
    if save_filename:
        with open(save_filename, "wb") as f:
            f.write(gif_bytes)
    
    os.remove(tmp_filename)
    plt.close(fig)
    
    return io.BytesIO(gif_bytes), trajectory, trajectory_p1
