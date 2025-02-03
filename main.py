import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

def main():
    st.title("Viergelenkkette – Demo")
    st.write(
        """
        Dieses Beispiel zeigt eine stark vereinfachte Darstellung einer Viergelenkkette.
        Über zwei Slider lässt sich der Winkel am Punkt O2 und der Winkel am Punkt O0 anpassen.
        """
    )

    # ------------------------------------
    # Parameter & Benutzereingaben
    # ------------------------------------
    # (Vereinfacht angenommene) Längen
    L_O2P2 = 30     # Länge vom festen Gelenk O2 zum Knoten P2
    L_P2P1 = 30     # Länge vom Knoten P2 zum Koppelpunkt P1
    L_O0P1 = 20     # Länge vom festen Gelenk O0 zum Koppelpunkt P1

    # Slider für Eingabewinkel in Grad
    alpha = st.slider("Winkel an O2 (Grad):", 0, 360, 0)
    beta  = st.slider("Winkel an O0 (Grad):", 0, 360, 60)

    # Umwandlung in Radianten
    alpha_rad = np.deg2rad(alpha)
    beta_rad  = np.deg2rad(beta)

    # ------------------------------------
    # Positionen berechnen
    # ------------------------------------
    # Festgelegte Punkte (feste Gelenke)
    O2x, O2y = -30.0, 0.0   # z.B. linkes Gelenk
    O0x, O0y =  0.0, 0.0    # z.B. rechtes Gelenk

    # Knoten P2 (je nach Winkel alpha)
    P2x = O2x + L_O2P2 * math.cos(alpha_rad)
    P2y = O2y + L_O2P2 * math.sin(alpha_rad)

    # Koppelpunkt P1 (hier stark vereinfacht: eigener Winkel beta statt 
    # aus Kinematikgleichungen berechnet)
    P1x = O0x + L_O0P1 * math.cos(beta_rad)
    P1y = O0y + L_O0P1 * math.sin(beta_rad)

    # ------------------------------------
    # Plot erstellen
    # ------------------------------------
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='datalim')  # gleicher Maßstab auf x- und y-Achse

    # Kreis um O2 (zeigt mögliche Positionen von P2)
    circle = plt.Circle((O2x, O2y), L_O2P2, color='red', fill=False, linestyle='--')
    ax.add_patch(circle)

    # Punkte zeichnen
    ax.plot([O2x], [O2y], 'ro', label="O2")
    ax.plot([O0x], [O0y], 'ro', label="O0")
    ax.plot([P2x], [P2y], 'ro', label="P2")
    ax.plot([P1x], [P1y], 'ro', label="P1")

    # Verbindende Stäbe/Gelenke (Linien)
    ax.plot([O2x, P2x], [O2y, P2y], 'r-', label="Glied O2–P2")
    ax.plot([P2x, P1x], [P2y, P1y], 'g-', label="Koppelglied P2–P1")
    ax.plot([O0x, P1x], [O0y, P1y], 'b-', label="Glied O0–P1")

    ax.set_xlim(-60, 30)
    ax.set_ylim(-40, 40)
    ax.set_xlabel("X-Achse")
    ax.set_ylabel("Y-Achse")
    ax.set_title("Viergelenkkette – Schematische Darstellung")
    ax.legend()

    # Darstellung in Streamlit
    st.pyplot(fig)

if __name__ == "__main__":
    main()
