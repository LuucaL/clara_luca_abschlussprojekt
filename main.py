# main.py
import streamlit as st
import numpy as np
from four_bar import animate_4bar_kinematics
from crank_rod import animate_crank_kinematics

def main():
    st.title("Ebene Mechanismen")
    choice = st. radio(
        "Welches Modell wollen Sie wählen?",
        ("Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "freier Mechanismus")
    )

    if choice == "Geschlossenes 4-Gelenk":
        choice = st. radio("Standardpunkte oder eigene Punkte?", ("Standardpunkte", "Eigene Punkte"))
        if choice == "Standardpunkte":
            st.write("Geschlossenes 4-Gelenk")
            points = {
                "p0": np.array([ 0.0,  0.0 ]),
                "p1": np.array([10.0, 10.0 ]),
                "p2": np.array([25.0,  5.0 ]),
                "p3": np.array([10.0,  0.0 ])
            }
            if st.button("Simulation starten"):
                gif_buffer = animate_4bar_kinematics(points)
                st.image(gif_buffer, caption="4-Gelenk-Simulation")
            
        elif choice == "Eigene Punkte":
            st.write("Geschlossenes 4-Gelenk")
            p0_x = st.number_input("p0_x", value=0.0)
            p0_y = st.number_input("p0_y", value=0.0)
            p1_x = st.number_input("p1_x", value=10.0)
            p1_y = st.number_input("p1_y", value=10.0)
            p2_x = st.number_input("p2_x", value=25.0)
            p2_y = st.number_input("p2_y", value=5.0)
            p3_x = st.number_input("p3_x", value=10.0)
            p3_y = st.number_input("p3_y", value=0.0)
            points = {
                "p0": np.array([p0_x, p0_y]),
                "p1": np.array([p1_x, p1_y]),
                "p2": np.array([p2_x, p2_y]),
                "p3": np.array([p3_x, p3_y])
            }

            if st.button("Simulation starten"):
                gif_buffer = animate_4bar_kinematics(points)
                st.image(gif_buffer, caption="4-Gelenk-Simulation")
    
    elif choice == "Kolben-Kurbel-Mechanismus":
        st.write("Kolben-Kurbel-Mechanismus")
        choice = st.radio("Standardpunkte oder eigene Punkte?", ("Standardpunkte", "Eigene Punkte"))
        if choice == "Standardpunkte":
            points = {
                "p0": np.array([ 0.0,  0.0 ]),
                "p1": np.array([10.0, 10.0 ]),
                "p2": np.array([30.0,  30.0 ]),
                "p3": np.array([30.0,  0.0 ])
            }

            choice_path = st.radio("Mit Bahnkurve oder ohne?", ("Mit Bahnkurve", "Ohne Bahnkurve"))
            show_path = (choice_path == "Mit Bahnkurve")

            if st.button("Simulation starten"):
                gif_buffer = animate_crank_kinematics(points, show_path=show_path)
                st.image(gif_buffer, caption="crank-Simulation (Pfad = {})".format(show_path))
        
        elif choice == "Eigene Punkte":
            p0_x = st.number_input("p0_x", value=0.0)
            p0_y = st.number_input("p0_y", value=0.0)
            p1_x = st.number_input("p1_x", value=10.0)
            p1_y = st.number_input("p1_y", value=10.0)
            p2_x = st.number_input("p2_x", value=30.0)
            p2_y = st.number_input("p2_y", value=30.0)
            p3_x = st.number_input("p3_x", value=30.0)
            p3_y = st.number_input("p3_y", value=0.0)
            points = {
                "p0": np.array([p0_x, p0_y]),
                "p1": np.array([p1_x, p1_y]),
                "p2": np.array([p2_x, p2_y]),
                "p3": np.array([p3_x, p3_y])
            }

            choice_path = st.radio("Mit Bahnkurve oder ohne?", ("Mit Bahnkurve", "Ohne Bahnkurve"))
            show_path = (choice_path == "Mit Bahnkurve")

            if st.button("Simulation starten"):
                gif_buffer = animate_crank_kinematics(points, show_path=show_path)
                st.image(gif_buffer, caption="crank-Simulation (Pfad = {})".format(show_path))

    elif choice == "Freier-Mechanismus":
        st.write("Freier-Mechanismus")
        choice_points = st.radio("Standardpunkte oder eigene Punkte?", ("Standardpunkte", "Eigene Punkte"))
    
        if choice_points == "Standardpunkte":
            points = {
                "p0": np.array([0.0, 0.0]),
                "p1": np.array([10.0, 10.0]),
                "p2": np.array([30.0, 30.0]),
                "p3": np.array([30.0, 0.0]),
            }
            st.write("Standardpunkte werden verwendet.")
    
        elif choice_points == "Eigene Punkte":
            st.write("Bitte eigene Punkte eingeben:")
            p0_x = st.number_input("p0_x", value=0.0)
            p0_y = st.number_input("p0_y", value=0.0)
            p1_x = st.number_input("p1_x", value=10.0)
            p1_y = st.number_input("p1_y", value=10.0)
            p2_x = st.number_input("p2_x", value=30.0)
            p2_y = st.number_input("p2_y", value=30.0)
            p3_x = st.number_input("p3_x", value=30.0)
            p3_y = st.number_input("p3_y", value=0.0)
        
            points = {
                "p0": np.array([p0_x, p0_y]),
                "p1": np.array([p1_x, p1_y]),
                "p2": np.array([p2_x, p2_y]),
                "p3": np.array([p3_x, p3_y]),
            }

            if st.button("Simulation starten"):
                gif_buffer = animate_4bar_kinematics(points)
                st.image(gif_buffer, caption="4-Gelenk-Simulation")



if __name__ == "__main__":
    main()
