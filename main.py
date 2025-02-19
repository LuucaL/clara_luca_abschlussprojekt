import streamlit as st
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from four_bar import animate_4bar_kinematics
from crank_rod import animate_crank_kinematics
from strandbeest import animate_strandbeest
from advanced_strandbeest import animate_strandbeest_full


def save_trajectory(trajectory, trajectory_p1, filename):

    if not trajectory or not trajectory_p1:
        st.error("Fehler: Die Bahnkurve enthält keine Daten.")
        return
    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["x_p1", "y_p1", "x_p2", "y_p2"])
            for p1, p2 in zip(trajectory, trajectory_p1):
                writer.writerow([p1[0], p1[1], p2[0], p2[1]])
        st.success(f"Bahnkurve gespeichert als {filename}")
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")


def load_saved_trajectory(filename):
    trajectory_p1, trajectory = [], []
    try:
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                trajectory_p1.append([float(row[0]), float(row[1])])
                trajectory.append([float(row[2]), float(row[3])]) 
    except Exception as e:
        st.error(f"Fehler beim Laden der Bahnkurve: {e}")
    return trajectory, trajectory_p1

def display_saved_trajectory(filename):
    trajectory, trajectory_p1 = load_saved_trajectory(filename)

    if trajectory and trajectory_p1:
        fig, ax = plt.subplots()
        data_p1 = np.array(trajectory)
        data_p2 = np.array(trajectory_p1)
        ax.plot(data_p1[:, 0], data_p1[:, 1], "b--", label="Bahnkurve p1 (blau)")
        ax.plot(data_p2[:, 0], data_p2[:, 1], "g--", label="Bahnkurve p2 (grün)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
    else:
        st.error("Die Datei enthält ungültige Daten und kann nicht als Zahlen interpretiert werden.")

def main():
    st.title("Ebene Mechanismen")

    if "trajectory" not in st.session_state:
        st.session_state.trajectory = None

    choice = st.radio(
        "Welches Modell wollen Sie wählen?",
        ("Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Freier-Mechanismus", "Strandbeest", "Advanced-Strandbeest", "Gespeicherte Bahnkurven anzeigen")
    )


    if choice == "Gespeicherte Bahnkurven anzeigen":
        files = [f for f in os.listdir() if f.endswith(".csv")]
        selected_file = st.selectbox("Wähle eine gespeicherte Bahnkurve", files)
        if st.button("Bahnkurve anzeigen"):
            display_saved_trajectory(selected_file)

    elif choice in ["Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Strandbeest", "Advanced-Strandbeest", "Freier-Mechanismus"]:
        show_path = st.checkbox("Mit Bahnkurve")
        trajectory, trajectory_p1=[], []

        if choice in ["Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Freier-Mechanismus"]:
            sub_choice = st.radio("Standardpunkte oder eigene Punkte?", ("Standardpunkte", "Eigene Punkte"))
            if sub_choice == "Standardpunkte":
                points = {
                    "p0": np.array([0.0, 0.0]),
                    "p1": np.array([10.0, 10.0]),
                    "p2": np.array([25.0, 5.0]) if choice == "Geschlossenes 4-Gelenk" else np.array([30.0, 30.0]),
                    "p3": np.array([10.0, 0.0])
                }
            elif sub_choice == "Eigene Punkte":
                p0_x = st.number_input("p0_x", value=0.0)
                p0_y = st.number_input("p0_y", value=0.0)
                p1_x = st.number_input("p1_x", value=10.0)
                p1_y = st.number_input("p1_y", value=10.0)
                p2_x = st.number_input("p2_x", value=25.0 if choice == "Geschlossenes 4-Gelenk" else 30.0)
                p2_y = st.number_input("p2_y", value=5.0 if choice == "Geschlossenes 4-Gelenk" else 30.0)
                p3_x = st.number_input("p3_x", value=10.0 if choice == "Geschlossenes 4-Gelenk" else 30.0)
                p3_y = st.number_input("p3_y", value=0.0)
                points = {
                    "p0": np.array([p0_x, p0_y]),
                    "p1": np.array([p1_x, p1_y]),
                    "p2": np.array([p2_x, p2_y]),
                    "p3": np.array([p3_x, p3_y])
                }
            if choice == "Geschlossenes 4-Gelenk":
                animation_func = lambda: animate_4bar_kinematics(points, show_path)
            elif choice == "Kolben-Kurbel-Mechanismus":
                animation_func = lambda: animate_crank_kinematics(points, show_path)
            elif choice == "Freier-Mechanismus":
                animation_func = lambda: animate_4bar_kinematics(points)
        
        elif choice in ["Strandbeest", "Advanced-Strandbeest"]:
            start_pos = np.array([0.0, 0.0])
            if choice == "Strandbeest":
                animation_func = lambda: animate_strandbeest(start_pos)
            else:
                animation_func = lambda: animate_strandbeest_full(start_pos, show_path)

        if st.button("Simulation starten"):
          try:
            result = animation_func()
            if len(result) == 2:
             gif_buffer, trajectory_p1 = result
             trajectory = []
            elif len(result) == 3:
             gif_buffer, trajectory, trajectory_p1 = result
            else:
             raise ValueError(f"Unerwartete Anzahl an Rückgabewerten: {len(result)}")

            st.image(gif_buffer, caption=f"{choice}-Simulation")

            if trajectory and trajectory_p1 and show_path:
             st.session_state.trajectory = trajectory
             st.session_state.trajectory_p1 = trajectory_p1
          except Exception as e:
            st.error(f"Fehler bei der Simulation: {e}")
            print(f"DEBUG-Fehlerdetails: {e}")    


        if show_path and st.session_state.get("trajectory") and st.session_state.get("trajectory_p1"):
            filename = st.text_input("Dateiname für die Bahnkurven eingeben:", "trajectory.csv")
            if filename and st.button("Bahnkurven speichern"):
                save_trajectory(st.session_state.trajectory, st.session_state.trajectory_p1, filename)
           


if __name__ == "__main__":
    main()
