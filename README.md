
## Installation

- Python Version Python 3.12.4
- Requirements installieren 'pip install -r requirements.txt

## Nutzung

- Vemv aktivieren '.\.venv\Skripts\activate' Windows
- Streamlit starten 'python -m streamlit run main.py'

## Projektdokumentation

Die entwickelte Software bietet die Möglichkeit verschiedene ebene Mechanismen zu animieren und die Bahnkurven ihrer Gelenke darzustellen. Die Bahnkurven können gespeichert und wieder zur Darstellung geöffnet werden. Der Benutzer hat verschiedene Wahlmöglichkeiten (z.B. Geschlossenes 4-Gelenk, Schubkurbel,...) mit unterschiedlichen Konfigurationen. Ausserdem kann entschieden werden, ob die Bahnkurve angezeigt werden soll und ob die Darstellung gespeichert werden sollen und unter welchem Dateinamen. Die Koordinaten der Gelenke der Modelle können entweder übernommen werden oder individuell geändert werden. Für nicht mögliche Berechnungen und Darstellungen (z.B. Stäbe sind null) kriegt der Nutzer eine Rückmeldung und eine Aufforderung die Punkte zu bearbeiten.



Die Berechnungen werden auf das Strandbeest angewendet. Einerseits kann so eine vereinfachte zweidimensionale Darstellung und andererseits die reele, dreidimensionale Darstellung erstellt werden. 

Die Längenfehler der Glieder je nach Winkel Theta kann für die Modelle Geschlossenes 4-Gelenk und Kurbel-Kolben-Mechanismus dargestellt werden. Anhand dieser Daten können die Modelle weiter verbessert werden.

Desweiteren können die Animationen als .gif gespeichert werden und wieder geöffnet werden. Der Dateiname kann selbst bestimmt werden. 
