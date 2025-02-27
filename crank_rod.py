import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import streamlit as st

def compute_crank_rod_length_errors(points, theta_range=np.linspace(0, 360, 180)):
    
    p0 = points["p0"]
    p1_init = points["p1"]
    p2_init = points["p2"]
    p3 = points["p3"]
    
    L0 = np.linalg.norm(p1_init - p0)  
    L1 = np.linalg.norm(p2_init - p1_init)  
    L2 = np.linalg.norm(p2_init - p3)  
    errors = {"L0": [], "L1": [], "L2": []}
    theta_values = []
    last_p2 = p2_init.copy()
    for theta in theta_range:
        alpha = np.radians(theta)
        p1 = np.array([p0[0] + L0 * np.cos(alpha), p0[1] + L0 * np.sin(alpha)])
        
        p2 = circle_intersections(p1, L1, p3, L2, last_p2)
        if p2 is None:
            continue  
        last_p2 = p2
        
        curr_L0 = np.linalg.norm(p1 - p0)
        curr_L1 = np.linalg.norm(p2 - p1)
        curr_L2 = np.linalg.norm(p2 - p3)
        
        errors["L0"].append(curr_L0 - L0)
        errors["L1"].append(curr_L1 - L1)
        errors["L2"].append(curr_L2 - L2)
        theta_values.append(theta)
    return theta_values, errors
def plot_crank_rod_length_errors(points):
    
    theta_values, errors = compute_crank_rod_length_errors(points)
    fig, ax = plt.subplots(figsize=(10, 6))
    for link, error_vals in errors.items():
        ax.plot(theta_values, error_vals, label=f'Fehler {link}')
    ax.set_xlabel("Theta (Grad)")
    ax.set_ylabel("Längenfehler")
    ax.set_title("Längenfehler der Glieder als Funktion von Theta (Kolben-Kurbel-Mechanismus)")
    ax.legend()
    ax.grid()
    return fig
  

def circle_intersections(c1, r1, c2, r2, last_p2=None):
    """Berechnet die Schnittpunkte zweier Kreise und wählt den kontinuierlichsten Punkt."""
    (x1, y1), (x2, y2) = c1, c2
    d = np.hypot(x2 - x1, y2 - y1)
    
    if d > (r1 + r2) or d < abs(r1 - r2):
        st.write("Fehler: Kein gültiger Schnittpunkt für den Mechanismus gefunden. Überprüfen Sie die Punkte!")
        return None
    
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
    
    return p1  

def validate_mechanism(points):
    """Überprüft, ob die Punkte gültig sind."""
    p0, p1, p2, p3 = points["p0"], points["p1"], points["p2"], points["p3"]
    distances = {
        "L0": np.linalg.norm(p1 - p0),
        "L1": np.linalg.norm(p2 - p1),
        "L2": np.linalg.norm(p2 - p3),
        "L3": np.linalg.norm(p3 - p0),
    }

    # Überprüfung auf ungültige Abstände
    for key, value in distances.items():
        if value == 0:
            st.write(f"Fehler: {key} ist Null. Punkte überlappen oder sind identisch!")
            return False

    # Prüfen, ob die Mechanismus-Bedingungen erfüllt sind (Grashof-Kriterium)
    lengths_sorted = sorted(distances.values())
    if lengths_sorted[0] + lengths_sorted[1] > lengths_sorted[2] + lengths_sorted[3]:
        st.write("Warnung: Grashof-Kriterium nicht erfüllt. Der Mechanismus könnte sich nicht vollständig bewegen.")

    return True

def animate_crank_kinematics(points, show_path=False, save_filename=None):
    
    if not validate_mechanism(points):
        return None, None, None
    
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
        if p2 is None:
            st.write("Simulation gestoppt: Keine gültige Position für P2 gefunden.")
            return []  # Keine Animation ausführen, falls das Modell fehlschlägt
        
        last_p2 = p2
        
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
