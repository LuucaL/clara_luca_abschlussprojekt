# advanced_strandbeest.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import io
import tempfile
import os

# --- Definierte Stablängen (Maße aus Ihrem Modell) ---
A = 38.0
B = 41.5
C = 39.3
D = 40.1
E = 55.8
F = 39.4
G = 36.7
H = 65.7
I = 49.0
J = 50.0
K = 61.9
L = 7.8
M = 15.0  # Kurbelradius

def circle_intersections(P, r, Q, s):
    """
    Berechnet die beiden Schnittpunkte der Kreise:
      Kreis 1: Mittelpunkt P, Radius r
      Kreis 2: Mittelpunkt Q, Radius s
    Gibt ein Array der beiden Schnittpunkte zurück oder None, wenn kein Schnitt existiert.
    """
    d = np.linalg.norm(Q - P)
    if d > r + s or d < abs(r - s):
        return None  # Kein Schnittpunkt
    a = (r**2 - s**2 + d**2) / (2 * d)
    h = np.sqrt(max(r**2 - a**2, 0))
    P2 = P + a * (Q - P) / d
    intersection1 = P2 + np.array([ h * (Q[1] - P[1]) / d, -h * (Q[0] - P[0]) / d ])
    intersection2 = P2 - np.array([ h * (Q[1] - P[1]) / d, -h * (Q[0] - P[0]) / d ])
    return np.array([intersection1, intersection2])

def default_choice(candidates, label):
    """
    Legt für den ersten Frame (ohne vorherigen Wert) eine Default-Entscheidung fest.
    Für bestimmte Gelenke wählen wir z. B.:
      - Bei P2 und P3: den Kandidaten mit dem kleineren y-Wert
      - Bei P4 bis P7: den Kandidaten mit dem größeren x-Wert
    """
    if label in ['P2', 'P3']:
        return candidates[0] if candidates[0][1] < candidates[1][1] else candidates[1]
    elif label in ['P4', 'P5', 'P6', 'P7']:
        return candidates[0] if candidates[0][0] > candidates[1][0] else candidates[1]
    else:
        return candidates[0]

def pick_solution(candidates, prev, label):
    """
    Wählt den Schnittpunkt.
    Falls ein vorheriger Wert (prev) existiert, wird der Kandidat gewählt, der diesem näher liegt.
    Andernfalls erfolgt die Default-Auswahl.
    """
    if prev is not None:
        if np.linalg.norm(candidates[0] - prev) < np.linalg.norm(candidates[1] - prev):
            return candidates[0]
        else:
            return candidates[1]
    else:
        return default_choice(candidates, label)

def safe_intersection(P, r, Q, s, label, prev_positions):
    """
    Ruft circle_intersections auf. Falls keine Schnittpunkte gefunden werden (sol ist None),
    wird als Fallback entweder der vorherige Wert (sofern vorhanden) oder der Mittelpunkt von P und Q gewählt.
    Andernfalls wird mittels pick_solution der passendste Kandidat ermittelt.
    """
    sol = circle_intersections(P, r, Q, s)
    if sol is None:
        # Fallback: Verwende vorherigen Wert, falls vorhanden, sonst Mittelpunkt von P und Q
        fallback = prev_positions[label] if prev_positions is not None and label in prev_positions else (P + Q) / 2.0
        return fallback
    else:
        prev = prev_positions[label] if prev_positions is not None and label in prev_positions else None
        return pick_solution(sol, prev, label)

def compute_positions_no_offset(theta, prev_positions=None):
    """
    Berechnet in Abhängigkeit des Kurbelwinkels theta die Gelenkpunkte P0 bis P7 
    für den Jansen-Beinmechanismus.
    Falls einzelne Schnittpunkte nicht berechnet werden können, werden Fallback-Werte genutzt.
    """
    # Fester Rahmenpunkt
    P0 = np.array([0.0, 0.0])
    # Kurbelpunkt P1 liegt auf dem Kreis mit Radius M
    P1 = np.array([M * np.cos(theta), M * np.sin(theta)])
    positions = {'P0': P0, 'P1': P1}

    P2 = safe_intersection(P0, A, P1, B, 'P2', prev_positions)
    positions['P2'] = P2
    P3 = safe_intersection(P1, C, P2, D, 'P3', prev_positions)
    positions['P3'] = P3
    P4 = safe_intersection(P0, E, P3, F, 'P4', prev_positions)
    positions['P4'] = P4
    P5 = safe_intersection(P4, G, P2, H, 'P5', prev_positions)
    positions['P5'] = P5
    P6 = safe_intersection(P3, I, P4, J, 'P6', prev_positions)
    positions['P6'] = P6
    P7 = safe_intersection(P4, K, P6, L, 'P7', prev_positions)
    positions['P7'] = P7

    return positions

def animate_strandbeest_full(start_pos=np.array([0.0, 0.0])):
    """
    Erzeugt eine Animation des Advanced-Strandbeest (Jansen-Beinmechanismus) und gibt einen GIF-Buffer zurück.
    Der Parameter start_pos wird zu allen Gelenkpunkten addiert, um den Mechanismus an eine beliebige Position zu verschieben.
    """
    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-100 + start_pos[0], 100 + start_pos[0])
    ax.set_ylim(-100 + start_pos[1], 100 + start_pos[1])
    ax.set_title("Advanced-Strandbeest Simulation")
    
    # Definition der Segmente, die die Gelenkpunkte verbinden (entsprechend der Stäbe)
    segments = [
        ('P0', 'P1'),
        ('P0', 'P2'),
        ('P1', 'P2'),
        ('P1', 'P3'),
        ('P2', 'P3'),
        #('P0', 'P4'),
        ('P3', 'P4'),
        ('P4', 'P5'),
        ('P2', 'P5'),
        ('P3', 'P6'),
        ('P4', 'P6'),
        ('P4', 'P7'),
        ('P6', 'P7'),
    ]
    
    # Erzeugen von Linienobjekten für jedes Segment
    lines = []
    for _ in segments:
        line_obj, = ax.plot([], [], 'ko-', lw=2)
        lines.append(line_obj)
    
    prev_positions = {}

    def init():
        for line_obj in lines:
            line_obj.set_data([], [])
        return lines

    def update(frame):
        nonlocal prev_positions
        theta = 2 * np.pi * frame / 120.0  # Eine volle Umdrehung in 120 Frames
        pos = compute_positions_no_offset(theta, prev_positions)
        prev_positions = pos
        # Verschiebung um start_pos
        pos_offset = {key: pos[key] + start_pos for key in pos}
        for i, (p_start, p_end) in enumerate(segments):
            start = pos_offset[p_start]
            end = pos_offset[p_end]
            lines[i].set_data([start[0], end[0]], [start[1], end[1]])
        return lines

    # Wichtig: blit=False, damit jeder Frame vollständig gezeichnet wird
    ani = FuncAnimation(fig, update, frames=120, init_func=init, blit=False, interval=50)
    
    # Speichern der Animation in eine temporäre Datei und Laden in einen Buffer
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp_file:
        tmp_filename = tmp_file.name
    writer = PillowWriter(fps=20)
    ani.save(tmp_filename, writer=writer)
    plt.close(fig)
    
    with open(tmp_filename, "rb") as f:
        gif_data = f.read()
    os.remove(tmp_filename)
    
    buf = io.BytesIO(gif_data)
    buf.seek(0)
    return buf
