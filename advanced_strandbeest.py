import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import least_squares
import tempfile, os
from io import BytesIO

# Konstanten für den Solver
FTOL = 1e-7
XTOL = 1e-7
GTOL = 1e-7
MAX_NFEV = 1000

class MechanismSimulator:
    """
    Diese Klasse kapselt die Logik eines starren Stabsystems, bei dem zwei Punkte fest (Y, Z) sind, 
    X sich auf einem Kreis um Z bewegt und die übrigen Punkte (W, V, T, U, S) so angepasst werden,
    dass alle Kanten (Stäbe) ihre Länge beibehalten.
    """
    def __init__(self, fixed_points: dict, init_positions: dict, edges: list):
        self.fixed_points = fixed_points
        self.init_positions = init_positions
        self.edges = edges
        self.free_labels = ["W", "V", "T", "U", "S"]
        self.current_free_positions = {k: v.copy() for k, v in init_positions.items() if k in self.free_labels}
        self.rod_lengths = self._compute_rod_lengths()
        # Kreisparameter: X bewegt sich um Z, der Kreisradius wird aus der Anfangsposition von X bestimmt.
        self.X0 = init_positions["X"]
        self.R = np.linalg.norm(np.array(self.X0) - np.array(self.fixed_points["Z"]))

    def _compute_rod_lengths(self) -> dict:
        rod_lengths = {}
        for (p1, p2) in self.edges:
            p1_pos = self.init_positions.get(p1, self.fixed_points.get(p1))
            p2_pos = self.init_positions.get(p2, self.fixed_points.get(p2))
            length = np.linalg.norm(np.array(p1_pos) - np.array(p2_pos))
            rod_lengths[(p1, p2)] = length
            rod_lengths[(p2, p1)] = length  # symmetrisch
        return rod_lengths

    def crank_position(self, theta_deg: float) -> np.ndarray:
        theta = math.radians(theta_deg)
        cx = self.fixed_points["Z"][0] + self.R * math.cos(theta)
        cy = self.fixed_points["Z"][1] + self.R * math.sin(theta)
        return np.array([cx, cy], dtype=float)

    def pack_positions(self, positions_dict: dict) -> np.ndarray:
        return np.array([pos for label in self.free_labels for pos in positions_dict[label]], dtype=float)

    def unpack_positions(self, param_vector: np.ndarray) -> dict:
        free_positions = {}
        for i, label in enumerate(self.free_labels):
            free_positions[label] = param_vector[2*i:2*i+2]
        return free_positions

    def constraint_equations(self, param_vector: np.ndarray, X_current: np.ndarray) -> np.ndarray:
        free_pos = self.unpack_positions(param_vector)
        all_pos = {**self.fixed_points, "X": X_current, **free_pos}
        residuals = []
        for (p1, p2) in self.edges:
            target_length = self.rod_lengths[(p1, p2)]
            current_length = np.linalg.norm(all_pos[p1] - all_pos[p2])
            residuals.append(current_length - target_length)
        return np.array(residuals)

    def update(self, frame_deg: float) -> dict:
        X_current = self.crank_position(frame_deg)
        start_vec = self.pack_positions(self.current_free_positions)
        sol = least_squares(
            fun=self.constraint_equations,
            x0=start_vec,
            args=(X_current,),
            ftol=FTOL, xtol=XTOL, gtol=GTOL,
            max_nfev=MAX_NFEV
        )
        if not sol.success:
            print(f"Warnung: least_squares hat bei Winkel {frame_deg}° nicht konvergiert.")
        free_solution = self.unpack_positions(sol.x)
        self.current_free_positions = free_solution
        all_points = {**self.fixed_points, "X": X_current, **free_solution}
        return all_points

def animate_strandbeest_full(points, show_path=False):
    trajectory=[]
    
    """
    Erzeugt die Animation für den Mechanismus.
    Falls show_path True ist, wird zusätzlich die Bahnkurve des Punktes S als grüne, 
    gestrichelte Linie gezeichnet.
    """
    # Definition der Punkte (Standardwerte oder aus points übernommene Werte)
    # Hier ein Beispiel:
    Y = (-3, 0)
    Z = (10.1, 0)
    X0 = (15.6, 0.5)
    W = (3.3, 9)
    V = (-12.4, 5.7)
    T = (-8.3, -4.5)
    U = (1.1, -10.2)
    S = (-2.9, -23.7)

    fixed_points = {
        "Y": np.array(Y, dtype=float),
        "Z": np.array(Z, dtype=float)
    }
    init_positions = {
        "X": np.array(X0, dtype=float),
        "W": np.array(W, dtype=float),
        "V": np.array(V, dtype=float),
        "T": np.array(T, dtype=float),
        "U": np.array(U, dtype=float),
        "S": np.array(S, dtype=float)
    }

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
    
    simulator = MechanismSimulator(fixed_points, init_positions, edges)

    # Erstelle die Figur und Achsen
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-35, 35)
    ax.set_title("Strandbeest-Kinematik")
    ax.grid(True)

    # Erzeuge Linien-Objekte für die Kanten
    lines = []
    for _ in edges:
        line, = ax.plot([], [], 'k-', lw=2)
        lines.append(line)

    # Erzeuge Punkt-Markierungen und Labels für alle Punkte
    all_labels = list(fixed_points.keys()) + ["X"] + simulator.free_labels
    point_markers = {}
    for label in all_labels:
        marker, = ax.plot([], [], 'ro')
        text = ax.text(0, 0, label, fontsize=8)
        point_markers[label] = (marker, text)
    
    # Falls wir die Bahnkurve für S wollen, initialisieren wir die entsprechenden Daten und den Plot
    if show_path:
        S_path_xdata, S_path_ydata = [], []
        S_path_line, = ax.plot([], [], "g--", lw=2, label="Bahnkurve von S")
    else:
        S_path_line = None

    def init():
        for line in lines:
            line.set_data([], [])
        for marker, text in point_markers.values():
            marker.set_data([], [])
            text.set_position((0, 0))
        if show_path:
            S_path_line.set_data([], [])
        # Rückgabe aller zu aktualisierenden Artist-Objekte
        artists = list(point_markers.values()) + lines
        if show_path:
            artists.append(S_path_line)
        return artists
    

    def animate(frame_deg):
        all_points = simulator.update(frame_deg)
        # Aktualisiere die Linien (Kanten)
        for i, (p1, p2) in enumerate(edges):
            xdata = [all_points[p1][0], all_points[p2][0]]
            ydata = [all_points[p1][1], all_points[p2][1]]
            lines[i].set_data(xdata, ydata)
        # Aktualisiere die Punkte und Labels
        for label, (marker, text) in point_markers.items():
            x, y = all_points[label]
            marker.set_data([x], [y])
            text.set_position((x + 0.3, y + 0.3))
        # Aktualisiere die Bahnkurve für S
        trajectory = []  # Liste zur Speicherung der Bahnkurve von S
        if show_path:
            S = all_points["S"]
            S_path_xdata.append(S[0])
            S_path_ydata.append(S[1])
            S_path_line.set_data(S_path_xdata, S_path_ydata)
            trajectory = [(x, y) for x, y in zip(S_path_xdata, S_path_ydata)]  # Speichern der Bahnkurve
        artists = list(point_markers.values()) + lines
        if show_path:
            artists.append(S_path_line)
        return artists, trajectory 

    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=np.arange(0, 360, 2),  # z. B. von 0° bis 358° in 2°-Schritten
        init_func=init,
        blit=False,
        interval=50
    )
    
    # Speichere die Animation in eine temporäre Datei und lese den Inhalt ein
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmpfile:
        tmp_filename = tmpfile.name
    try:
        ani.save(tmp_filename, writer="pillow", fps=20)
        with open(tmp_filename, "rb") as f:
            buf = f.read()
    finally:
        os.remove(tmp_filename)
    plt.close(fig)
    return buf,trajectory
