import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def circle_intersections(c1, r1, c2, r2):
    (x1, y1), (x2, y2) = c1, c2
    d = np.hypot(x2 - x1, y2 - y1)
    if d > (r1 + r2) or d < abs(r1 - r2):
        return []
    if d == 0 and abs(r1 - r2) < 1e-9:
        return []
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(r1**2 - a**2, 0.0))
    xm = x1 + a * (x2 - x1) / d
    ym = y1 + a * (y2 - y1) / d
    if abs(h) < 1e-12:
        return [(xm, ym)]
    rx = -(y2 - y1) * (h / d)
    ry =  (x2 - x1) * (h / d)
    return [(xm + rx, ym + ry), (xm - rx, ym - ry)]

def animate_crank_kinematics(points, show_path=False):
    p0 = points["p0"]
    p1_init = points["p1"]
    p2_init = points["p2"]
    p3 = points["p3"]
    
    L0 = np.linalg.norm(p1_init - p0)   
    L1 = np.linalg.norm(p2_init - p1_init)
    L2 = np.linalg.norm(p2_init - p3)
    L3 = np.linalg.norm(p3 - p0)
    
    NUM_FRAMES = 80
    FPS = 10
    
    fig, ax = plt.subplots()
    ax.set_title("Echte 4-Gelenk-Kinematik")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    
    ln_p0, = ax.plot([], [], "ro", ms=8)
    ln_p1, = ax.plot([], [], "bo", ms=8)
    ln_p2, = ax.plot([], [], "go", ms=8)
    ln_p3, = ax.plot([], [], "ro", ms=8)
    bar_01, = ax.plot([], [], "k-", lw=2)
    bar_12, = ax.plot([], [], "k-", lw=2)
    bar_23, = ax.plot([], [], "k-", lw=2)
    circle = plt.Circle((p0[0], p0[1]), L0, fill=False, color="blue", lw=2)
    ax.add_patch(circle)
    
    trajectory, trajectory_p1 = [], []
    
    if show_path:
        p1_path, = ax.plot([], [], "b--", lw=1)
        p2_path, = ax.plot([], [], "g--", lw=1)
    else:
        p1_path, p2_path = None, None
    
    def init():
        return ln_p0, ln_p1, ln_p2, ln_p3, bar_01, bar_12, bar_23, circle, p1_path, p2_path
    
    def update(frame):
        alpha = 2*np.pi*frame/NUM_FRAMES
        px1 = p0[0] + L0*np.cos(alpha)
        py1 = p0[1] + L0*np.sin(alpha)
        p1 = np.array([px1, py1])
        
        hits = circle_intersections(p1, L1, p3, L2)
        p2 = np.array(hits[0]) if hits else np.array([np.nan, np.nan])
        
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
        
        return ln_p0, ln_p1, ln_p2, ln_p3, bar_01, bar_12, bar_23, circle, p1_path, p2_path
    
    ani = FuncAnimation(fig, update, frames=NUM_FRAMES, init_func=init, interval=1000//FPS, blit=True)
    
    tmpfile = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp_filename = tmpfile.name
    tmpfile.close()
    ani.save(tmp_filename, writer=PillowWriter(fps=FPS))
    with open(tmp_filename, "rb") as f:
        gif_bytes = f.read()
    os.remove(tmp_filename)
    plt.close(fig)
    
    return io.BytesIO(gif_bytes), trajectory, trajectory_p1