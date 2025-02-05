# main.py
import streamlit as st
import numpy as np
from Bar_Gelenk import animate_4bar_kinematics
from crank_rod import animate_crank_kinematics

def main():
    st.title("Ebene Mechanismen")
    choice = st. radio(
        "Welches Modell wollen Sie wählen?",
        ("Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "freier Mechanismus")
    )
    

    if choice == "Geschlossenes 4-Gelenk":
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

    elif choice == "Kolben-Kurbel-Mechanismus":
        st.write("Kolben-Kurbel-Mechanismus")
        points = {
            "p0": np.array([ 0.0,  0.0 ]),
            "p1": np.array([10.0, 10.0 ]),
            "p2": np.array([30.0,  30.0 ]),
            "p3": np.array([30.0,  0.0 ])
        }
        if st.button("Simulation starten"):
            gif_buffer = animate_crank_kinematics(points)
            st.image(gif_buffer, caption="crank-Simulation")

    elif choice == "freier Mechanismus":
        st.write("freier Mechanismus")

if __name__ == "__main__":
    main()
