import streamlit as st
import numpy as np
from calculation import build_points, build_matrix_4bars, compute_bar_lengths
from framework import animate_4bar_gif

def main():
    st.title("Ebene Mechanismen - Viergelenk")

    # --- Teil 1: Eingabe / Längenberechnung ---
    choice = st.radio(
        "Welche Punkte möchten Sie verwenden?",
        ("Standardpunkte", "Eigene Eingabe")
    )

    if choice == "Standardpunkte":
        points = build_points()
    else:
        st.write("Bitte Koordinaten angeben ...")
        def_x = {"p0x": "0.0", "p0y": "0.0", 
                 "p1x": "10.0", "p1y": "35.0",
                 "p2x": "-25.0", "p2y": "10.0",
                 "p3x": "5.0", "p3y": "-30.0"}

        p0x = st.text_input("p0.x", value=def_x["p0x"])
        p0y = st.text_input("p0.y", value=def_x["p0y"])
        p1x = st.text_input("p1.x", value=def_x["p1x"])
        p1y = st.text_input("p1.y", value=def_x["p1y"])
        p2x = st.text_input("p2.x", value=def_x["p2x"])
        p2y = st.text_input("p2.y", value=def_x["p2y"])
        p3x = st.text_input("p3.x", value=def_x["p3x"])
        p3y = st.text_input("p3.y", value=def_x["p3y"])

        def to_float(s):
            try:
                return float(s.strip())
            except ValueError:
                return 0.0

        points = {
            "p0": np.array([to_float(p0x), to_float(p0y)]),
            "p1": np.array([to_float(p1x), to_float(p1y)]),
            "p2": np.array([to_float(p2x), to_float(p2y)]),
            "p3": np.array([to_float(p3x), to_float(p3y)]),
        }

    st.write("---")
    if st.button("Stablängen berechnen"):
        x = np.array([
            points["p0"][0], points["p0"][1],
            points["p1"][0], points["p1"][1],
            points["p2"][0], points["p2"][1],
            points["p3"][0], points["p3"][1],
        ])
        A = build_matrix_4bars()
        lengths = compute_bar_lengths(A, x)

        st.write("**Stablängen**:")
        for i, L in enumerate(lengths, start=1):
            st.write(f"Stab {i}: {L:.4f}")

    # --- Teil 2: Simulation starten ---
    st.write("---")
    if st.button("Simulation starten"):
        gif_buffer = animate_4bar_gif(points)   # Punkte als Argument
        st.image(gif_buffer, caption="Animiertes Viergelenk")


if __name__ == "__main__":
    main()