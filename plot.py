import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

import pandas as pd
import os

# Chemin racine des données
base_dir = "data"

# Initialiser une liste pour stocker tous les DataFrames
all_data = []

# Scanner les sous-dossiers (semaine 12, 13, etc.)
for semaine in os.listdir(base_dir):
    semaine_path = os.path.join(base_dir, semaine)
    if os.path.isdir(semaine_path):
        for file in os.listdir(semaine_path):
            if file.endswith(".csv") and "Workout" in file:
                file_path = os.path.join(semaine_path, file)
                df = pd.read_csv(file_path)
                df["semaine"] = semaine  # Ajouter l'info de la semaine
                df["source"] = file      # Ajouter le nom du fichier source
                all_data.append(df)

# Fusionner tous les fichiers
if all_data:
    full_df = pd.concat(all_data, ignore_index=True)
    full_df["date"] = pd.to_datetime(full_df["date"], errors='coerce')

    # Nettoyage du poids
    import re
    def extract_weight(value):
        if pd.isna(value):
            return None
        match = re.search(r'\d+\.?\d*', str(value))
        return float(match.group()) if match else None

    full_df["poids_num"] = full_df["poids"].apply(extract_weight)

    # Sauvegarder si tu veux
    full_df.to_csv("data/Workout_Combined_Clean.csv", index=False)
    print("✅ Fichier combiné généré avec succès.")
else:
    print("❌ Aucun fichier CSV trouvé dans les sous-dossiers.")


# Création de l'app Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Progression des Poids par Exercice"),
    dcc.Dropdown(
        id='exercise-dropdown',
        options=[{'label': ex, 'value': ex} for ex in sorted(df["exercices"].dropna().unique())],
        value=sorted(df["exercices"].dropna().unique())[0],
        clearable=False
    ),
    dcc.Graph(id='weight-progression')
])

@app.callback(
    Output('weight-progression', 'figure'),
    Input('exercise-dropdown', 'value')
)
def update_graph(selected_exercise):
    filtered = df[df["exercices"] == selected_exercise]
    fig = px.line(filtered, x='date', y='poids_num', markers=True,
                  title=f"Progression du poids pour : {selected_exercise}",
                  labels={"poids_num": "Poids (kg)", "date": "Date"})
    fig.update_layout(xaxis_title="Date", yaxis_title="Poids utilisé (kg)")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
