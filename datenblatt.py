import json
import numpy as np
import streamlit as st

def compute_mechanism_properties(points):
    """
    Berechnet die Längen der Glieder und speichert die Anzahl der Gelenke und Glieder.
    
    """
    p0, p1, p2, p3 = points["p0"], points["p1"], points["p2"], points["p3"]

    L0 = np.linalg.norm(p1 - p0)  
    L1 = np.linalg.norm(p2 - p1)  
    L2 = np.linalg.norm(p2 - p3)  
    L3 = np.linalg.norm(p3 - p0)  

    mechanism_data = {
        "Benoetigte Materialien"
        "Anzahl der Gelenke": len(points),
        "Laengen der Stangen": {
            "Stange 1 (p0 -> p1)": L0,
            "Stange 2 (p1 -> p2)": L1,
            "Stange 3 (p2 -> p3)": L2,
            "Stange 4 (p3 -> p0)": L3
        }
    }
    
    return mechanism_data

def save_mechanism_data(points, filename="mechanism_data.json"):
    
    data = compute_mechanism_properties(points)

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    st.write(f"Mechanismus-Daten wurden in {filename} gespeichert.")