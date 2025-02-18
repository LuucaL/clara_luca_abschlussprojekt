import streamlit as st
import numpy as np
import csv
import os
from four_bar import animate_4bar_kinematics
from crank_rod import animate_crank_kinematics
from strandbeest import animate_strandbeest
from advanced_strandbeest import animate_strandbeest_full


def save_trajectory(trajectory, filename):

    if trajectory is None or len(trajectory) == 0:
        st.error("Fehler: Die Bahnkurve enthält keine Daten.")
        return
    
    trajectory = [[float(x), float(y)] for x, y in trajectory]

    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["x", "y"])
            writer.writerows(trajectory)
        st.success(f"Bahnkurve gespeichert als {filename}")
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")




def load_saved_trajectories():
    files = [f for f in os.listdir() if f.endswith(".csv")]
    return files

def display_saved_trajectory(filename):
    if filename:
        with open(filename, 'r') as file:
            first_line = file.readline().strip()

        try:
            data = np.loadtxt(filename, delimiter=",", skiprows=1)
            st.line_chart(data)
        except ValueError:
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
        files = load_saved_trajectories()
        selected_file = st.selectbox("Wähle eine gespeicherte Bahnkurve", files)
        if st.button("Bahnkurve anzeigen"):
            display_saved_trajectory(selected_file)

    elif choice in ["Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Strandbeest", "Advanced-Strandbeest", "Freier-Mechanismus"]:
        show_path = st.checkbox("Mit Bahnkurve") if choice in ["Kolben-Kurbel-Mechanismus", "Advanced-Strandbeest", "Strandbeest"] else False
        trajectory = None
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
                animation_func = animate_4bar_kinematics
            elif choice == "Kolben-Kurbel-Mechanismus":
                animation_func = lambda pts: animate_crank_kinematics(pts, show_path)
            elif choice == "Freier-Mechanismus":
                animation_func = lambda pts: animate_4bar_kinematics(pts)
        
        elif choice in ["Strandbeest", "Advanced-Strandbeest"]:
            start_pos = np.array([0.0, 0.0])
            if choice == "Strandbeest":
                animation_func = lambda pos: animate_strandbeest(pos)
            else:
                animation_func = lambda pos: animate_strandbeest_full(pos, show_path)

        if st.button("Simulation starten"):
          try:
            if choice in ["Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Freier-Mechanismus"]:
                gif_buffer, trajectory = animation_func(points)
            else:
                gif_buffer, trajectory = animation_func(start_pos)

            st.image(gif_buffer, caption=f"{choice}-Simulation")
            if trajectory:
                    st.session_state.trajectory = trajectory
            else:
                    st.warning("Keine Bahnkurve aufgezeichnet.")

          except Exception as e:
            st.error(f"Fehler bei der Simulation: {e}")
            print(f"Fehlerdetails: {e}")


        if st.session_state.trajectory:
            filename = st.text_input("Dateiname für die Bahnkurve eingeben:", "trajectory.csv")
            if st.button("Bahnkurve speichern", key="save_button"):
             save_trajectory(st.session_state.trajectory, filename)  
           


if __name__ == "__main__":
    main()