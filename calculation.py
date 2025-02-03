import numpy as np

def build_points():
    #Standartpunkte mal als Beispiel 
    return {
        "p0": np.array([  0.0,   0.0]),
        "p1": np.array([ 10.0,  35.0]),
        "p2": np.array([-25.0,  10.0]),
        "p3": np.array([  5.0, -30.0])
    }

def build_matrix_4bars():
    
    #8x8-Matrix A für vier Stäbe (p0->p1, p1->p2, p2->p3, p3->p0).
    
    A = np.zeros((8, 8))
    # Stab 1: p0 -> p1
    A[0, 0] =  1.0; A[0, 2] = -1.0
    A[1, 1] =  1.0; A[1, 3] = -1.0
    # Stab 2: p1 -> p2
    A[2, 2] =  1.0; A[2, 4] = -1.0
    A[3, 3] =  1.0; A[3, 5] = -1.0
    # Stab 3: p2 -> p3
    A[4, 4] =  1.0; A[4, 6] = -1.0
    A[5, 5] =  1.0; A[5, 7] = -1.0
    # Stab 4: p3 -> p0
    A[6, 6] =  1.0; A[6, 0] = -1.0
    A[7, 7] =  1.0; A[7, 1] = -1.0
    return A

def compute_bar_lengths(A, x):
    
    #A*x -> Differenzvektoren, daraus euklidische Längen der 4 Stäbe.
    diffs = A @ x  # Vektor der Länge 8
    diffs_2d = diffs.reshape(-1, 2)  # (4,2)
    lengths = np.linalg.norm(diffs_2d, axis=1)
    return lengths

def run_4bar_calculation(points):
    #speichert vektorlängen in einem array
    # 1) Punktevektor x
    x = np.array([
        points["p0"][0], points["p0"][1],
        points["p1"][0], points["p1"][1],
        points["p2"][0], points["p2"][1],
        points["p3"][0], points["p3"][1],
    ])
    # 2) Matrix A
    A = build_matrix_4bars()
    # 3) Längen berechnen
    lengths = compute_bar_lengths(A, x)
    return lengths
