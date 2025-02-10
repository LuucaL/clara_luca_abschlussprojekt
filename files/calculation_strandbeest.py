import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ---------------------- Parameter (Längen und Winkel) ---------------------- #
# Längen (entsprechend MATLAB)
L1 = 6;   L2 = 1;   L3 = 8;   L33 = 8;   L4 = 5;   L44 = 5
L5 = 5;   L6 = 5;   L66 = 9;  L7 = 5;    L8 = 0.5

A1 = 0.0  # Fixwinkel (für den Boden)

# A2: von pi/2 bis 6*pi+pi/2 in Schritten von 0.3
A2 = np.arange(np.pi/2, 6*np.pi + np.pi/2 + 0.3, 0.3)
# A22 = pi + A2, danach Vorzeichenwechsel
A22 = np.pi + A2
A2 = -A2
A22 = -A22

# ---------------------- Hilfsfunktion: Mechanism ---------------------- #
def Mechanism(L1, L2, L3, L4, A1, A2, mode='cross'):
    """
    Berechnet für einen Viergelenk-Mechanismus (feste Grundseite von Länge L1,
    Eingangsgelenk L2, Verbindungsstab L3 und Ausgangsstab L4) die Winkel A3 und A4.
    
    Wir nehmen an, dass der feste Punkt A bei (0,0) liegt und D bei (L1,0) – also A1=0.
    Es gilt:
        B = (L2*cos(A2), L2*sin(A2))
        C = B + L3*(cos(A3), sin(A3))
        und C liegt auf einem Kreis um D mit Radius L4.
        
    Zur Lösung wird zuerst eine Gleichung der Form
        A*sin(A3) + B*cos(A3) = M
    aufgestellt, die sich mittels Phasoraddition lösen lässt.
    """
    # Wir definieren:
    A_val = L2 * np.sin(A2)
    B_val = - (L1 - L2 * np.cos(A2))
    R = np.sqrt(A_val**2 + B_val**2)
    # M aus der Schleifenschließung:
    M = (L4**2 - L1**2 - L2**2 - L3**2 + 2*L1*L2*np.cos(A2)) / (2*L3)
    # Damit erhalten wir: A*sin(A3) + B*cos(A3) = M  =>  R*cos(A3 - delta) = M
    # delta so gewählt, dass:
    delta = np.arctan2(A_val, B_val)
    # Damit gilt: A3 = delta ± arccos(M/R)
    # Für den 'cross'-Fall wählen wir die Plus-Lösung:
    # (Anpassungen sind hier je nach gewünschter Zweigwahl möglich.)
    # Achten Sie darauf, M/R in den erlaubten Bereich zu clippen.
    cos_arg = np.clip(M/R, -1, 1)
    if mode == 'cross':
        A3 = delta + np.arccos(cos_arg)
    else:
        A3 = delta - np.arccos(cos_arg)
    # Anschließend bestimmt sich A4 aus der Vektoraddition:
    A4 = np.arctan2(L2*np.sin(A2) + L3*np.sin(A3),
                    L2*np.cos(A2) + L3*np.cos(A3))
    return A3, A4

# ---------------------- Berechnungen der Gelenkwinkel und Punkte ---------------------- #
# Erster Schleifenzweig
A3, A4 = Mechanism(L1, L2, L3, L4, A1, A2, mode='cross')
A5 = (np.pi - A4) + (np.pi/2)

A32, A42 = Mechanism(L1, L2, L3, L4, A1, A22, mode='cross')
A52 = (np.pi - A42) + (np.pi/2)

# Punkte B
Bx = L2 * np.cos(A2)
By = L2 * np.sin(A2)
B2x = L2 * np.cos(A22)
B2y = L2 * np.sin(A22)

# Punkt C (Hinweis: Im MATLAB-Code wird für Cy direkt L4*sin(A4) genommen)
Cx = Bx + L3 * np.cos(A3)
Cy = L4 * np.sin(A4)
C2x = B2x + L3 * np.cos(A32)
C2y = L4 * np.sin(A42)

# Punkt E (fest)
Ex = L1;  Ey = -L8

# Zweiter Schleifenzweig (Berechnungen analog zum MATLAB-Code)
j   = 2 * L4 * ((L1 * np.cos(A1)) - (L2 * np.cos(A2)))
k   = 2 * L4 * ((L1 * np.sin(A1)) - (L2 * np.sin(A2)))
m_val = (L1**2) + (L2**2) - (L33**2) + (L44**2) - 2*L1*L2*np.cos(A1-A2)
A44 = 2 * np.arctan(( -k + np.sqrt(j**2 + k**2 - m_val**2) ) / (m_val - j))

n   = 2 * L3 * ((L2 * np.cos(A2)) - (L1 * np.cos(A1)))
p_val = 2 * L3 * ((L2 * np.sin(A2)) - (L1 * np.sin(A1)))
q   = (L1**2) + (L2**2) + (L33**2) - (L44**2) - 2*L1*L2*np.cos(A2-A1)
A33 = 2 * np.arctan(( -p_val - np.sqrt(n**2 + p_val**2 - q**2) ) / (q - n))

j2   = 2 * L4 * ((L1 * np.cos(A1)) - (L2 * np.cos(A22)))
k2   = 2 * L4 * ((L1 * np.sin(A1)) - (L2 * np.sin(A22)))
m2   = (L1**2) + (L2**2) - (L33**2) + (L44**2) - 2*L1*L2*np.cos(A1-A22)
A442 = 2 * np.arctan(( -k2 + np.sqrt(j2**2 + k2**2 - m2**2) ) / (m2 - j2))

n2   = 2 * L3 * ((L2 * np.cos(A22)) - (L1 * np.cos(A1)))
p2   = 2 * L3 * ((L2 * np.sin(A22)) - (L1 * np.sin(A1)))
q2   = (L1**2) + (L2**2) + (L33**2) - (L44**2) - 2*L1*L2*np.cos(A22-A1)
A332 = 2 * np.arctan(( -p2 - np.sqrt(n2**2 + p2**2 - q2**2) ) / (q2 - n2))

# Punkt D
Dx = Ex + L5 * np.cos(np.pi - A5)
Dy = Ey + L5 * np.sin(np.pi - A5)
D2x = Ex + L5 * np.cos(np.pi - A52)
D2y = Ey + L5 * np.sin(np.pi - A52)

# Dritter Schleifenzweig
A5 = -A5;  A4 = -A4
A6, A7 = Mechanism(L5, L4, L6, L7, A5, A4, mode='cross')
A52 = -A52;  A42 = -A42
A62, A72 = Mechanism(L5, L4, L6, L7, A52, A42, mode='cross')

# Punkt F
Fx = Bx + L33 * np.cos(A33)
Fy = By + L33 * np.sin(A33)
F2x = B2x + L33 * np.cos(A332)
F2y = B2y + L33 * np.sin(A332)

# Punkt G
Gx = Fx - L6 * np.cos(A6)
Gy = Fy - L6 * np.sin(A6)
G2x = F2x - L6 * np.cos(A62)
G2y = F2y - L6 * np.sin(A62)

# Punkt H
Hx = Fx + L66 * np.cos(A6 + np.pi/2)
Hy = Fy + L66 * np.sin(A6 + np.pi/2)
H2x = F2x + L66 * np.cos(A62 + np.pi/2)
H2y = F2y + L66 * np.sin(A62 + np.pi/2)

# Spiegelungssystem (system mirror)
BBx = -L2 * np.cos(A2)
BBy = L2 * np.sin(A2)
BB2x = -L2 * np.cos(A22)
BB2y = L2 * np.sin(A22)

CCx = BBx - L3 * np.cos(A3)
CCy = -L4 * np.sin(A4)
CC2x = B2x - L3 * np.cos(A32)
CC2y = -L4 * np.sin(A42)

EEx = -L1;  EEy = -L8

DDx = EEx - L5 * np.cos(np.pi - A5)
DDy = EEy - L5 * np.sin(np.pi - A5)
DD2x = EEx - L5 * np.cos(np.pi - A52)
DD2y = EEy - L5 * np.sin(np.pi - A52)

FFx = BBx - L33 * np.cos(A33)
FFy = BBy + L33 * np.sin(A33)
FF2x = BB2x - L33 * np.cos(A332)
FF2y = BB2y + L33 * np.sin(A332)

GGx = FFx + L6 * np.cos(A6)
GGy = FFy - L6 * np.sin(A6)
GG2x = FF2x + L6 * np.cos(A62)
GG2y = FF2y - L6 * np.sin(A62)

HHx = FFx - L66 * np.cos(A6 + np.pi/2)
HHy = FFy + L66 * np.sin(A6 + np.pi/2)
HH2x = FF2x - L66 * np.cos(A62 + np.pi/2)
HH2y = FF2y + L66 * np.sin(A62 + np.pi/2)

# ---------------------- Animation (entsprechend MATLAB-Loop) ---------------------- #
fig, ax = plt.subplots(figsize=(8,6))
ax.set_xlim(-13, 14)
ax.set_ylim(-14, 6)
ax.set_aspect('equal')
ax.set_facecolor('yellow')
# Damit auch Achsen, Hintergrund etc. gelb sind:
for spine in ax.spines.values():
    spine.set_color('yellow')
ax.tick_params(colors='yellow')

# Vorab definieren: Wir verwenden den Index i als Frame-Index, der von 0 bis len(A2)-1 läuft.
num_frames = len(A2)

def update(frame):
    ax.clear()
    ax.set_xlim(-13, 14)
    ax.set_ylim(-14, 6)
    ax.set_aspect('equal')
    ax.set_facecolor('yellow')
    for spine in ax.spines.values():
        spine.set_color('yellow')
    # Für Übersicht: Verwenden Sie den aktuellen Index i (frame) und einen Offset sh für das Spiegelungssystem
    i = frame
    sh = 5
    k = (i + sh) % num_frames

    # --- System 1 ---
    # Dots
    ax.plot(0, 0, 'or')
    ax.plot(Bx[i], By[i], 'or')
    ax.plot(Cx[i], Cy[i], 'ok')
    ax.plot(Ex, Ey, 'or')
    ax.plot(Dx[i], Dy[i], 'ok')
    ax.plot(Fx[i], Fy[i], 'ok')
    ax.plot(Gx[i], Gy[i], 'ok')
    ax.plot(Hx[i], Hy[i], 'ok')
    # System 1 Linien
    ax.plot([EEx, Ex], [-0.5, -0.5], '-k', linewidth=2)
    ax.plot([0, 0], [0, -0.5], '-k', linewidth=2)
    ax.plot([0, Bx[i]], [0, By[i]], '-k', linewidth=1)
    ax.plot([Bx[i], Cx[i]], [By[i], Cy[i]], '-m', linewidth=1)
    ax.plot([Ex, Cx[i]], [Ey, Cy[i]], '-m', linewidth=1)
    ax.plot([Ex, Dx[i]], [Ey, Dy[i]], '-m', linewidth=1)
    ax.plot([Cx[i], Dx[i]], [Cy[i], Dy[i]], '-m', linewidth=1)
    ax.plot([Bx[i], Fx[i]], [By[i], Fy[i]], '-m', linewidth=1)
    ax.plot([Ex, Fx[i]], [Ey, Fy[i]], '-m', linewidth=1)
    ax.plot([Dx[i], Gx[i]], [Dy[i], Gy[i]], '-m', linewidth=1)
    ax.plot([Fx[i], Gx[i]], [Fy[i], Gy[i]], '-m', linewidth=1)
    # System 1 Interior
    ax.add_patch(plt.Polygon([[Ex, Ey], [Cx[i], Cy[i]], [Dx[i], Dy[i]]],
                             color='g', alpha=0.5))
    ax.add_patch(plt.Polygon([[Fx[i], Fy[i]], [Hx[i], Hy[i]], [Gx[i], Gy[i]]],
                             color='c', alpha=0.5))
    # --- System 2 ---
    ax.plot([0, B2x[i]], [0, B2y[i]], '-k', linewidth=1)
    ax.plot([B2x[i], C2x[i]], [B2y[i], C2y[i]], '-b', linewidth=1)
    ax.plot([Ex, C2x[i]], [Ey, C2y[i]], '-b', linewidth=1)
    ax.plot([Ex, D2x[i]], [Ey, D2y[i]], '-b', linewidth=1)
    ax.plot([C2x[i], D2x[i]], [C2y[i], D2y[i]], '-b', linewidth=1)
    ax.plot([B2x[i], F2x[i]], [B2y[i], F2y[i]], '-b', linewidth=1)
    ax.plot([Ex, F2x[i]], [Ey, F2y[i]], '-b', linewidth=1)
    ax.plot([D2x[i], G2x[i]], [D2y[i], G2y[i]], '-b', linewidth=1)
    ax.plot([F2x[i], G2x[i]], [F2y[i], G2y[i]], '-b', linewidth=1)
    # System 2 Interior
    ax.add_patch(plt.Polygon([[Ex, Ey], [C2x[i], C2y[i]], [D2x[i], D2y[i]]],
                             color='c', alpha=0.5))
    ax.add_patch(plt.Polygon([[F2x[i], F2y[i]], [H2x[i], H2y[i]], [G2x[i], G2y[i]]],
                             color='g', alpha=0.5))
    # Kurven (bis zum aktuellen Frame)
    ax.plot(Hx[:i+1], Hy[:i+1], '-b')
    ax.plot(H2x[:i+1], H2y[:i+1], '-b')
    
    # --- Spiegelungssystem (System Mirror) ---
    ax.plot(BBx[k], BBy[k], 'or')
    ax.plot(CCx[k], CCy[k], 'ok')
    ax.plot(EEx, EEy, 'or')
    ax.plot(DDx[k], DDy[k], 'ok')
    ax.plot(FFx[k], FFy[k], 'ok')
    ax.plot(GGx[k], GGy[k], 'ok')
    ax.plot(HHx[k], HHy[k], 'ok')
    
    ax.plot(BB2x[k], BB2y[k], 'or')
    ax.plot(CC2x[k], CC2y[k], 'ok')
    ax.plot(EEx, EEy, 'or')
    ax.plot(DD2x[k], DD2y[k], 'ok')
    ax.plot(FF2x[k], FF2y[k], 'ok')
    ax.plot(GG2x[k], GG2y[k], 'ok')
    ax.plot(HH2x[k], HH2y[k], 'ok')
    
    ax.plot([0, BBx[k]], [0, BBy[k]], '-k', linewidth=1)
    ax.plot([BBx[k], CCx[k]], [BBy[k], CCy[k]], '-m', linewidth=1)
    ax.plot([EEx, CCx[k]], [EEy, CCy[k]], '-m', linewidth=1)
    ax.plot([EEx, DDx[k]], [EEy, DDy[k]], '-m', linewidth=1)
    ax.plot([CCx[k], DDx[k]], [CCy[k], DDy[k]], '-m', linewidth=1)
    ax.plot([BBx[k], FFx[k]], [BBy[k], FFy[k]], '-m', linewidth=1)
    ax.plot([EEx, FFx[k]], [EEy, FFy[k]], '-m', linewidth=1)
    ax.plot([DDx[k], GGx[k]], [DDy[k], GGy[k]], '-m', linewidth=1)
    ax.plot([FFx[k], GGx[k]], [FFy[k], GGy[k]], '-m', linewidth=1)
    ax.add_patch(plt.Polygon([[EEx, EEy], [CCx[k], CCy[k]], [DDx[k], DDy[k]]],
                             color='g', alpha=0.5))
    ax.add_patch(plt.Polygon([[FFx[k], FFy[k]], [HHx[k], HHy[k]], [GGx[k], GGy[k]]],
                             color='c', alpha=0.5))
    ax.plot([0, BB2x[k]], [0, BB2y[k]], '-k', linewidth=1)
    ax.plot([BB2x[k], CC2x[k]], [BB2y[k], CC2y[k]], '-b', linewidth=1)
    ax.plot([EEx, CC2x[k]], [EEy, CC2y[k]], '-b', linewidth=1)
    ax.plot([EEx, DD2x[k]], [EEy, DD2y[k]], '-b', linewidth=1)
    ax.plot([CC2x[k], DD2x[k]], [CC2y[k], DD2y[k]], '-b', linewidth=1)
    ax.plot([BB2x[k], FF2x[k]], [BB2y[k], FF2y[k]], '-b', linewidth=1)
    ax.plot([EEx, FF2x[k]], [EEy, FF2y[k]], '-b', linewidth=1)
    ax.plot([DD2x[k], GG2x[k]], [DD2y[k], GG2y[k]], '-b', linewidth=1)
    ax.plot([FF2x[k], GG2x[k]], [FF2y[k], GG2y[k]], '-b', linewidth=1)
    ax.add_patch(plt.Polygon([[EEx, EEy], [CC2x[k], CC2y[k]], [DD2x[k], DD2y[k]]],
                             color='c', alpha=0.5))
    ax.add_patch(plt.Polygon([[FF2x[k], FF2y[k]], [HH2x[k], HH2y[k]], [GG2x[k], GG2y[k]]],
                             color='g', alpha=0.5))
    
    # Beschriftungen
    ax.text(-1, -0.8, 'A')
    ax.text(Bx[i] + 0.1 * L2, By[i] + 0.1 * L2, 'B')
    ax.text(Cx[i] + 0.1 * (L3/2), Cy[i] + 0.1 * (L3/2), 'C')
    ax.text(5.8, -0.8, 'E')
    ax.text(Dx[i] + 0.1 * L5, Dy[i] + 0.1 * L5, 'D')
    ax.text(Fx[i] + 0.1 * (L3/2), Fy[i] + 0.1 * (L3/2), 'F')
    ax.text(Gx[i] + 0.1 * (L3/2), Gy[i] + 0.1 * (L3/2), 'G')
    ax.text(B2x[i] + 0.1 * L2, B2y[i] + 0.1 * L2, 'B2')
    ax.text(C2x[i] + 0.1 * (L3/2), C2y[i] + 0.1 * (L3/2), 'C2')
    ax.text(D2x[i] + 0.1 * L5, D2y[i] + 0.1 * L5, 'D2')
    ax.text(F2x[i] + 0.1 * (L3/2), F2y[i] + 0.1 * (L3/2), 'F2')
    ax.text(G2x[i] + 0.1 * (L3/2), G2y[i] + 0.1 * (L3/2), 'G2')
    
    return

ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=50, repeat=True)
plt.show()
