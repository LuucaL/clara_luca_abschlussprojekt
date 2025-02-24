
import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import streamlit as st


def animate_strandbeest(start_pos):
    """
    
    start_pos: Basisposition (x,y) des gesamten Mechanismus (z. B. die Hüfte).
    
    Verwendete Parameter (in Längeeinheiten), analog zu dem MATLAB-Script:
      L1 = 6,  L2 = 1,  L3 = 8,  L4 = 5,  L5 = 5,  L8 = 0.5.
      
    Der Mechanismus basiert auf dem Vier-Gelenk-Ansatz:
      - A = Basis (0,0)
      - B = Endpunkt des rotierenden Kurbelarms (L2, Winkel A2)
      - Mit der Funktion four_bar_mechanism wird für ein gegebenes A2 der
        Coupler‑Winkel A3 und der Rocker‑Winkel A4 bestimmt, sodass gilt:
          L2·e^(iA2) + L3·e^(iA3) = E_complex + L4·e^(iA4)
        wobei der feste Auflagepunkt E komplex durch E_complex = L1 - i·L8 definiert ist.
      - Anschließend wird ein Zusatzwinkel A5 definiert (A5 = (π - A4) + (π/2)),
        über den der Punkt D aus E abgeleitet wird.
      
    Es werden A, B, C, D und E berechnet und miteinander verbunden.
    """
    # Parameter gemäß MATLAB (für einen einzelnen Beinzyklus)
    L1 = 6.0    # Abstand A -> E (horizontale Grundlänge)
    L2 = 1.0    # Länge des Kurbelarms (A -> B)
    L3 = 8.0    # Länge des Couplers (B -> C)
    L4 = 5.0    # Länge des Rockers (E -> C)
    L5 = 5.0    # Länge für Zusatzglied (E -> D)
    L8 = 0.5    # Vertikaler Offset: E = (L1, -L8)
    
    # Basis A und fixer Punkt E (ohne Offset)
    A0 = np.array([0.0, 0.0])
    E0 = np.array([L1, -L8])
    # Komplexe Darstellung des festen Punkts (E0)
    E_complex = L1 - 1j * L8

    # Vier-Gelenk-Berechnung: Gegeben A2 (Kurbelwinkel) und den festen Vektor E_complex,
    # soll A3 (Couplerwinkel) und A4 (Rockerwinkel) gefunden werden,
    # sodass gilt:
    #    L2·e^(iA2) + L3·e^(iA3) = E_complex + L4·e^(iA4)
    def four_bar_mechanism(E_complex, L2, L3, L4, A2, branch='cross'):
        # Setze den Vektor von A nach E minus den Beitrag des Kurbelarms:
        Z = E_complex - L2 * np.exp(1j * A2)
        r = np.abs(Z)
        phi = np.angle(Z)
        # Berechne den Wert, der aus der Gleichung resultiert:
        D_val = (L3**2 - r**2 - L4**2) / (2 * L4)
        if r == 0 or np.abs(D_val) > r:
            return None, None
        acos_val = np.arccos(D_val / r)
        # Wähle den "cross"-Zweig (andernfalls branch='open' möglich)
        if branch == 'cross':
            A4 = phi - acos_val
        else:
            A4 = phi + acos_val
        # Bestimme A3 aus dem Schleifenabschluss:
        vec = E_complex + L4 * np.exp(1j * A4) - L2 * np.exp(1j * A2)
        A3 = np.angle(vec)
        return A3, A4

    # Animationsparameter
    NUM_FRAMES = 120
    FPS = 20

    fig, ax = plt.subplots()
    ax.set_title("Jansen-Mechanismus (vereinfachte Simulation)")
    ax.set_aspect("equal", adjustable="box")
    # Achsen so wählen, dass der Mechanismus gut sichtbar ist (relativ zur Basis A0)
    ax.set_xlim(-10, 20)
    ax.set_ylim(-15, 10)
    
    # Erzeuge Plotobjekte für die Punkte und eine Linie, die sie verbindet.
    line, = ax.plot([], [], 'k-', lw=2)
    marker_A, = ax.plot([], [], 'ro', ms=8, label='A')
    marker_B, = ax.plot([], [], 'bo', ms=8, label='B')
    marker_C, = ax.plot([], [], 'go', ms=8, label='C')
    marker_D, = ax.plot([], [], 'mo', ms=8, label='D')
    marker_E, = ax.plot([], [], 'co', ms=8, label='E')

    def init():
        
        line.set_data([], [])
        marker_A.set_data([], [])
        marker_B.set_data([], [])
        marker_C.set_data([], [])
        marker_D.set_data([], [])
        marker_E.set_data([], [])
        return line, marker_A, marker_B, marker_C, marker_D, marker_E
    
    trajectory=[]

    def update(frame):
        A2 = 2 * np.pi * frame / NUM_FRAMES
        B_complex = L2 * np.exp(1j * A2)
        B = np.array([B_complex.real, B_complex.imag])
        
        result = four_bar_mechanism(E_complex, L2, L3, L4, A2, branch='cross')
        if result[0] is None:
            print(f"Kein Lösung bei A2 = {A2:.2f}")
            if last_valid_artists is not None:
                return last_valid_artists
            return line, marker_A, marker_B, marker_C, marker_D, marker_E

        A3, A4 = result

        C_complex = B_complex + L3 * np.exp(1j * A3)
        C = np.array([C_complex.real, C_complex.imag])
        
        A5 = (np.pi - A4) + (np.pi / 2)
        D = np.array([E0[0] + L5 * np.cos(np.pi - A5),
                    E0[1] + L5 * np.sin(np.pi - A5)])
        
        A_pt = A0 + np.array(start_pos)
        B = B + np.array(start_pos)
        C = C + np.array(start_pos)
        D = D + np.array(start_pos)
        E_pt = E0 + np.array(start_pos)
        
        x_vals = [A_pt[0], B[0], C[0], D[0], E_pt[0]]
        y_vals = [A_pt[1], B[1], C[1], D[1], E_pt[1]]
        line.set_data(x_vals, y_vals)
        
        # Ändern Sie hier die set_data-Aufrufe, damit sie Sequenzen erhalten:
        marker_A.set_data([A_pt[0]], [A_pt[1]])
        marker_B.set_data([B[0]], [B[1]])
        marker_C.set_data([C[0]], [C[1]])
        marker_D.set_data([D[0]], [D[1]])
        marker_E.set_data([E_pt[0]], [E_pt[1]])

        trajectory.append([D[0], D[1]])
        
        last_valid_artists = (line, marker_A, marker_B, marker_C, marker_D, marker_E)
        return last_valid_artists


    ani = FuncAnimation(
        fig, update, frames=range(NUM_FRAMES), init_func=init,
        interval=1000 // FPS, blit=False, save_count=NUM_FRAMES
    )

    
    tmpfile = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp_filename = tmpfile.name
    tmpfile.close()
    fig.canvas.draw()
    ani.save(tmp_filename, writer=PillowWriter(fps=FPS))
    with open(tmp_filename, "rb") as f:
        gif_bytes = f.read()
    os.remove(tmp_filename)
    plt.close(fig)
    return io.BytesIO(gif_bytes), trajectory
