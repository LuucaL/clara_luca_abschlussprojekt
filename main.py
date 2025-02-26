import streamlit as st
import numpy as np
import os
import csv
import io
import matplotlib.pyplot as plt
from four_bar import animate_4bar_kinematics
from crank_rod import animate_crank_kinematics
from strandbeest import animate_strandbeest
from advanced_strandbeest import animate_strandbeest_full
from slider_crank import animate_slider_crank

def save_gif(gif_buffer, filename_gif):
    """Speichert die GIF-Animation unter dem angegebenen Dateinamen."""
    try:
        with open(filename_gif, "wb") as f:
            f.write(gif_buffer.getvalue())
        st.success(f"Animation gespeichert als {filename_gif}")
    except Exception as e:
        st.error(f"Fehler beim Speichern der GIF: {e}")

def save_trajectory(trajectory, trajectory_p1, filename):
    """Speichert die Bahnkurven in einer CSV-Datei."""
    if not trajectory and not trajectory_p1:
        st.error("Fehler: Die Bahnkurve enthält keine Daten.")
        return

    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if trajectory and trajectory_p1:
                writer.writerow(["x_p1", "y_p1", "x_p2", "y_p2"])
                for p1, p2 in zip(trajectory, trajectory_p1):
                    writer.writerow([p1[0], p1[1], p2[0], p2[1]])
            elif trajectory:
                writer.writerow(["x_p", "y_p"])
                for p in trajectory:
                    writer.writerow([p[0], p[1]])
            elif trajectory_p1:
                writer.writerow(["x_p1", "y_p1"])
                for p1 in trajectory_p1:
                    writer.writerow([p1[0], p1[1]])

        st.success(f"Bahnkurve gespeichert als {filename}")
    except Exception as e:
        st.error(f"Fehler beim Speichern der Bahnkurve: {e}")

def load_trajectory(filename):
    """Lädt eine gespeicherte Bahnkurve aus einer CSV-Datei."""
    trajectory, trajectory_p1 = [], []
    try:
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                if len(row) == 4:
                    trajectory_p1.append([float(row[0]), float(row[1])])
                    trajectory.append([float(row[2]), float(row[3])])
                elif len(row) == 2:
                    trajectory.append([float(row[0]), float(row[1])])
        return trajectory, trajectory_p1
    except Exception as e:
        st.error(f"Fehler beim Laden der Bahnkurve: {e}")
        return None, None        

def main():
    st.title("Ebene Mechanismen")

    choice = st.radio(
        "Welches Modell wollen Sie wählen?",
        ["Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Schubkurbel-Mechanismus", "Freier-Mechanismus", 
         "Strandbeest", "Advanced-Strandbeest", "Gespeicherte Bahnkurven anzeigen", "Gespeicherte Animationen anzeigen"]
    )

    if choice in ("Geschlossenes 4-Gelenk", "Kolben-Kurbel-Mechanismus", "Schubkurbel-Mechanismus", "Freier-Mechanismus"):
        show_path = st.checkbox("Mit Bahnkurve")

        sub_choice = st.radio("Standardpunkte oder eigene Punkte?", ("Standardpunkte", "Eigene Punkte"))
        if sub_choice == "Eigene Punkte":
            p0_x = st.number_input("p0_x", value=0.0)
            p0_y = st.number_input("p0_y", value=0.0)
            p1_x = st.number_input("p1_x", value=10.0)
            p1_y = st.number_input("p1_y", value=10.0)
            p2_x = st.number_input("p2_x", value=25.0)
            p2_y = st.number_input("p2_y", value=5.0)
            p3_x = st.number_input("p3_x", value=50.0)
            p3_y = st.number_input("p3_y", value=0.0)
            points = {
                "p0": np.array([p0_x, p0_y]),
                "p1": np.array([p1_x, p1_y]),
                "p2": np.array([p2_x, p2_y]),
                "p3": np.array([p3_x, p3_y])
            }
        else:
            points = {
                "p0": np.array([0.0, 0.0]),
                "p1": np.array([10.0, 10.0]),
                "p2": np.array([40.0, 30.0]),
                "p3": np.array([50.0, 0.0])
            }
    else:
        show_path = False
        points = None  
        
    animation_func = None
    if choice == "Geschlossenes 4-Gelenk":
        animation_func = lambda: animate_4bar_kinematics(points, show_path)
    elif choice == "Kolben-Kurbel-Mechanismus":
        animation_func = lambda: animate_crank_kinematics(points, show_path)
    elif choice == "Schubkurbel-Mechanismus":
        animation_func = lambda: animate_slider_crank(show_path)    
    elif choice == "Freier-Mechanismus":
        animation_func = lambda: animate_4bar_kinematics(points, show_path)
    elif choice == "Strandbeest":
        animation_func = lambda: animate_strandbeest(np.array([0.0, 0.0]))
    elif choice == "Advanced-Strandbeest":
        animation_func = lambda: animate_strandbeest_full(np.array([0.0, 0.0]))
        
    
    
    if choice not in ["Gespeicherte Bahnkurven anzeigen", "Gespeicherte Animationen anzeigen"]:
        
     filename_gif = st.text_input("Gib den Dateinamen für die GIF-Animation ein (mit .gif):", "animation.gif")   
     if choice not in ["Strandbeest", "Advanced-Strandbeest"]:  
      filename_traj = st.text_input("Gib den Dateinamen für die Bahnkurve ein (mit .csv):", "bahnkurve.csv")
                                    
     save_gif_checkbox = st.checkbox("GIF speichern")
     save_traj_checkbox = st.checkbox("Bahnkurve speichern") if choice not in ["Strandbeest", "Advanced-Strandbeest"] else False
    
    if animation_func and st.button("Simulation starten"):      
        try:
            
            result = animation_func()
            if result is None:
              st.error("Fehler: Die Simulation konnte nicht durchgeführt werden. Bitte überprüfen Sie die Eingaben.")
              return
            gif_buffer, trajectory, trajectory_p1 = result if len(result) == 3 else (result[0], result[1], None)

            st.image(gif_buffer, caption=f"{choice}-Simulation")
            
            if save_gif_checkbox:
              save_gif(gif_buffer, filename_gif)

            if save_traj_checkbox and show_path and (trajectory or trajectory_p1):
              save_trajectory(trajectory, trajectory_p1, filename_traj)


        except Exception as e:
            st.error(f"Fehler bei der Simulation: {e}")
    
    if choice == "Gespeicherte Animationen anzeigen":
        files = [f for f in os.listdir() if f.endswith(".gif")]
        if files:
            selected_file = st.selectbox("Wähle eine gespeicherte Animation", files)
            if st.button("Animation anzeigen"):
                st.image(selected_file, caption=f"Gespeicherte Animation: {selected_file}")
        else:
            st.warning("Keine gespeicherten Animationen gefunden.")

    elif choice == "Gespeicherte Bahnkurven anzeigen":
        files = [f for f in os.listdir() if f.endswith(".csv")]
        if files:
            selected_file = st.selectbox("Wähle eine gespeicherte Bahnkurve", files)
            if st.button("Bahnkurve anzeigen"):
                trajectory, trajectory_p1 = load_trajectory(selected_file)
                if trajectory or trajectory_p1:
                    fig, ax = plt.subplots()
                    if trajectory:
                        ax.plot(*zip(*trajectory), "b--", label="Bahnkurve p1 (blau)")
                    if trajectory_p1:
                        ax.plot(*zip(*trajectory_p1), "g--", label="Bahnkurve p2 (grün)")
                    ax.grid(True)
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.error("Die Datei enthält ungültige Daten.")
        else:
            st.warning("Keine gespeicherten Bahnkurven gefunden.") 
                                  

if __name__ == "__main__":
    main()

