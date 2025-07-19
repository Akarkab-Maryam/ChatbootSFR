import pandas as pd
import json
import gdown
import random

# === Téléchargement des fichiers Google Drive ===
file_ids = {
    "procedure": "1tQHxKRmejdD7SciBTrA5V_jBA4n_2Sdl",  # procédure SFR (json)
    "faq": "1XtZesLx35tN-Y0BiOyKfYgmlAIbNkQz5",        # FAQ (json)
    "projets": "1-qnd98mvhi3V4v4Jr46leyeIaCH45Mmn"    # ton nouveau fichier Excel partagé
}

# Télécharger les fichiers
gdown.download(id=file_ids["procedure"], output="procedure_sfr.json", quiet=False)
gdown.download(id=file_ids["faq"], output="faq_sfr_complet.json", quiet=False)
gdown.download(f"https://drive.google.com/uc?id={file_ids['projets']}", output="avancemment_memoir_modif.xlsx", quiet=False)

# === Génération des exemples à partir des fichiers ===
examples = []

# Procédures (label = procédure)
with open("procedure_sfr.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    etapes = data.get("procedure_SFR", {}).get("etapes", [])
    for etape in etapes:
        titre = etape.get('titre', '')
        question1 = f"Quelle est l'étape : {titre} ?"
        question2 = f"Peux-tu m'expliquer la procédure pour {titre.lower()} ?"
        examples.append((question1, "procédure"))
        examples.append((question2, "procédure"))

# FAQ (label = faq)
with open("faq_sfr_complet.json", "r", encoding="utf-8") as f:
    faq = json.load(f)["faq"]
    for item in faq:
        question = item.get("question", "").strip()
        if question:
            examples.append((question, "faq"))
            examples.append((f"J'ai une question : {question.lower()}", "faq"))

# Projets (label = projet)

# Lire le fichier Excel (avec le nom correct de la feuille)
df_temp = pd.read_excel("avancemment_memoir_modif.xlsx", sheet_name="Avancemment-2025")
print("Colonnes trouvées dans Excel :", df_temp.columns.tolist())

# Liste des colonnes utiles à utiliser
colonnes = ["UO", "NB.Lien", "Date de réception", "Odeon", "Type de dossier", "Date de depot", "ETAT"]

# Normalisation pour détecter colonnes existantes (pour éviter erreur)
def normalize_col(name):
    return name.strip().lower().replace(" ", "").replace("_", "")

colonnes_trouvees_norm = {normalize_col(c): c for c in df_temp.columns}
colonnes_finales = []

for c in colonnes:
    c_norm = normalize_col(c)
    if c_norm in colonnes_trouvees_norm:
        colonnes_finales.append(colonnes_trouvees_norm[c_norm])
    else:
        print(f"⚠️ La colonne '{c}' n'a pas été trouvée dans le fichier Excel et sera ignorée.")

# Lire le fichier avec les colonnes existantes seulement
df = pd.read_excel("avancemment_memoir_modif.xlsx", sheet_name="Avancemment-2025", usecols=colonnes_finales)

# Génération de questions autour des codes projets dans la colonne "UO"
for i in range(min(100, len(df))):
    code = str(df.iloc[i]["UO"])
    if pd.notna(code):
        questions = [
            f"Où en est le projet {code} ?",
            f"Donne-moi les détails du projet {code}",
            f"Quel est l'état du projet {code} ?",
            f"Quelle est la date de réception pour {code} ?"
        ]
        for q in questions:
            examples.append((q, "projet"))

# Mélanger et sauvegarder les exemples dans un fichier CSV
random.shuffle(examples)
df_final = pd.DataFrame(examples, columns=["text", "label"])
df_final.to_csv("intent_dataset.csv", index=False, encoding="utf-8")
print("✅ Fichier intent_dataset.csv généré avec succès.")
