import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import least_squares

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
        """
        :param fixed_points: Dictionary fester Punkte, z. B. {"Y": np.array(...), "Z": np.array(...)}
        :param init_positions: Dictionary der Anfangspositionen aller Punkte (inkl. X und der freien Punkte)
        :param edges: Liste von Tupeln, die die Verbindungen (Stäbe) definieren
        """
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
        """
        Berechnet die Längen aller Stäbe (Edges) anhand der initialen Konfiguration.
        """
        rod_lengths = {}
        for (p1, p2) in self.edges:
            p1_pos = self.init_positions.get(p1, self.fixed_points.get(p1))
            p2_pos = self.init_positions.get(p2, self.fixed_points.get(p2))
            length = np.linalg.norm(np.array(p1_pos) - np.array(p2_pos))
            rod_lengths[(p1, p2)] = length
            rod_lengths[(p2, p1)] = length  # symmetrisch
        return rod_lengths

    def crank_position(self, theta_deg: float) -> np.ndarray:
        """
        Bestimmt die Position von X auf dem Kreis um Z mit Radius R.
        
        :param theta_deg: Winkel in Grad
        :return: np.array([x, y]) der aktuellen Position von X
        """
        theta = math.radians(theta_deg)
        cx = self.fixed_points["Z"][0] + self.R * math.cos(theta)
        cy = self.fixed_points["Z"][1] + self.R * math.sin(theta)
        return np.array([cx, cy], dtype=float)

    def pack_positions(self, positions_dict: dict) -> np.ndarray:
        """
        Packt die Positionen der freien Punkte in einen flachen Vektor.
        
        :param positions_dict: Dictionary mit Positionen der freien Punkte (z. B. {"W": np.array([x, y]), ...})
        :return: 1D np.array in der Reihenfolge self.free_labels
        """
        return np.array([pos for label in self.free_labels for pos in positions_dict[label]], dtype=float)

    def unpack_positions(self, param_vector: np.ndarray) -> dict:
        """
        Entpackt den Parameter-Vektor in ein Dictionary der freien Punkte.
        
        :param param_vector: 1D np.array, Länge = 2 * Anzahl freier Punkte
        :return: Dictionary, z. B. {"W": np.array([x, y]), ...}
        """
        free_positions = {}
        for i, label in enumerate(self.free_labels):
            free_positions[label] = param_vector[2*i:2*i+2]
        return free_positions

    def constraint_equations(self, param_vector: np.ndarray, X_current: np.ndarray) -> np.ndarray:
        """
        Berechnet die Differenz zwischen der aktuellen Länge und der Soll-Länge für jeden Stab.
        
        :param param_vector: Vektor der freien Punkte (W, V, T, U, S)
        :param X_current: Aktuelle Position von X
        :return: np.array der Residuen (aktueller Abstand - Soll-Länge) für alle Edges
        """
        free_pos = self.unpack_positions(param_vector)
        # Kombiniere alle Punkte: Feste, X und die freien Punkte.
        all_pos = {**self.fixed_points, "X": X_current, **free_pos}
        residuals = []
        for (p1, p2) in self.edges:
            target_length = self.rod_lengths[(p1, p2)]
            current_length = np.linalg.norm(all_pos[p1] - all_pos[p2])
            residuals.append(current_length - target_length)
        return np.array(residuals)

    def update(self, frame_deg: float) -> dict:
        """
        Führt ein Update für den gegebenen Winkel aus, löst die Constraints und liefert die
        aktuellen Positionen aller Punkte zurück.
        
        :param frame_deg: Aktueller Winkel für die Position von X in Grad
        :return: Dictionary mit allen Positionen (z. B. {"Y": ..., "Z": ..., "X": ..., "W": ..., ...})
        """
        # 1) Setze X auf die Kreisposition
        X_current = self.crank_position(frame_deg)
        
        # 2) Lösen der Constraints mit dem Solver (least_squares)
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
        # Aktualisiere den Startwert für den nächsten Frame
        self.current_free_positions = free_solution
        
        # Kombiniere alle Punkte in ein Dictionary
        all_points = {**self.fixed_points, "X": X_current, **free_solution}
        return all_points

def main():
    # ---------------------------------------------------------
    # Ursprüngliche Koordinaten (werden nur genutzt, um Stablängen zu messen)
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Stäbe (Edges) und deren Längen (aus den Originaldaten)
    # ---------------------------------------------------------
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
    
    # Erzeuge den Simulator
    simulator = MechanismSimulator(fixed_points, init_positions, edges)

    # ---------------------------------------------------------
    # Animation und Darstellung mit matplotlib
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-35, 35)
    ax.set_title("Nur Y und Z fest, X kreist – alle anderen Punkte frei (Stäbe mit fixer Länge)")
    ax.grid(True)

    # Erzeuge Linien-Objekte für alle Kanten
    lines = []
    for _ in edges:
        line, = ax.plot([], [], 'k-', lw=2)
        lines.append(line)
    
    # Erzeuge Punkt-Markierungen und Labels für alle Punkte (inkl. Y, Z, X und freie Punkte)
    all_labels = list(fixed_points.keys()) + ["X"] + simulator.free_labels
    point_markers = {}
    for label in all_labels:
        marker, = ax.plot([], [], 'ro')  # Roter Marker
        text = ax.text(0, 0, label, fontsize=8)
        point_markers[label] = (marker, text)
    
    def init():
        """Initialisiert alle Grafik-Elemente."""
        for line in lines:
            line.set_data([], [])
        for marker, text in point_markers.values():
            marker.set_data([], [])
            text.set_position((0, 0))
        return list(point_markers.values()) + lines
    
    def animate(frame_deg: float):
        """
        Aktualisiert den Plot für einen gegebenen Winkel.
        
        :param frame_deg: aktueller Winkel in Grad
        :return: Liste der aktualisierten Artist-Objekte
        """
        all_points = simulator.update(frame_deg)
        
        # Aktualisiere die Linien (Kanten)
        for i, (p1, p2) in enumerate(edges):
            xdata = [all_points[p1][0], all_points[p2][0]]
            ydata = [all_points[p1][1], all_points[p2][1]]
            lines[i].set_data(xdata, ydata)
        
        # Aktualisiere die Punkte und Labels; marker.set_data erwartet Sequenzen:
        for label, (marker, text) in point_markers.items():
            x, y = all_points[label]
            marker.set_data([x], [y])
            text.set_position((x + 0.3, y + 0.3))
        
        return list(point_markers.values()) + lines
    
    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=np.arange(0, 360, 2),  # 0° bis 358° in 2°-Schritten
        init_func=init,
        blit=False,  # Blitting bleibt deaktiviert
        interval=50
    )
    
    plt.show()

if __name__ == "__main__":
    main()
