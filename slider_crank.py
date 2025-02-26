import io
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import streamlit as st

def animate_slider_crank(show_path=False):
    
    # Mechanismus-Parameter (Längen der Stäbe)
    L_crank = 5.0   # Kurbel
    L_rod = 10.0    # Koppelstange
    base_x = 0.0    # Position der festen Basis
    base_y = 0.0
    
    NUM_FRAMES = 120
    FPS = 20
    
    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-15, 20)
    ax.set_ylim(-10, 10)
    #ax.set_title("Schubkurbel-Mechanismus")
    #ax.set_xlabel("X-Position")
    #ax.set_ylabel("Y-Position")
    
    
    crank_line, = ax.plot([], [], "k-", lw=2)
    rod_line, = ax.plot([], [], "b-", lw=2)
    slider_line, = ax.plot([], [], "r-", lw=2)
    crank_point, = ax.plot([], [], "ro", ms=6)
    rod_point, = ax.plot([], [], "bo", ms=6)
    slider_point, = ax.plot([], [], "go", ms=6)
    
    trajectory = []
    slider_path = None
    if show_path:
        slider_path, = ax.plot([], [], "g--", lw=1, label="Schieber-Bahn")
    
    def init():
        crank_line.set_data([], [])
        rod_line.set_data([], [])
        slider_line.set_data([], [])
        crank_point.set_data([], [])
        rod_point.set_data([], [])
        slider_point.set_data([], [])
        if show_path:
            slider_path.set_data([], [])
        return crank_line, rod_line, slider_line, crank_point, rod_point, slider_point
    
    def update(frame):
        theta = 2 * np.pi * frame / NUM_FRAMES
        crank_x = base_x + L_crank * np.cos(theta)
        crank_y = base_y + L_crank * np.sin(theta)
        
        # Berechnung der Position des Schiebers
        c = L_crank * np.cos(theta)
        d = L_crank * np.sin(theta)
        e = np.sqrt(L_rod**2 - d**2)
        slider_x = base_x + c + e  # Annahme: Schieber bewegt sich in X-Richtung
        slider_y = base_y  # Bleibt konstant auf der Achse
        
        
        crank_line.set_data([base_x, crank_x], [base_y, crank_y])
        rod_line.set_data([crank_x, slider_x], [crank_y, slider_y])
        slider_line.set_data([slider_x, slider_x], [slider_y - 1, slider_y + 1])
        
        crank_point.set_data([crank_x], [crank_y])
        rod_point.set_data([slider_x], [slider_y])
        slider_point.set_data([slider_x], [slider_y])
        
        if show_path:
            trajectory.append([slider_x, slider_y])
            slider_path.set_data(*zip(*trajectory))
        
        return crank_line, rod_line, slider_line, crank_point, rod_point, slider_point
    
    ani = FuncAnimation(fig, update, frames=NUM_FRAMES, init_func=init, interval=1000//FPS, blit=False)
    
    tmpfile = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp_filename = tmpfile.name
    tmpfile.close()
    ani.save(tmp_filename, writer=PillowWriter(fps=FPS))
    with open(tmp_filename, "rb") as f:
        gif_bytes = f.read()
    os.remove(tmp_filename)
    plt.close(fig)
    
    return io.BytesIO(gif_bytes), trajectory
