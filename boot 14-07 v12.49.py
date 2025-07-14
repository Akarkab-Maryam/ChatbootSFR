import asyncio
import json
import pandas as pd
import gdown
import torch
import re
from transformers import pipeline
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)

# === CONFIGURATION ===
BOT_TOKEN = '7645422993:AAFkFkkXb3e0RqpZRdL1vuVQn7Incd6ssK8'
UTILISATEURS_AUTORISES = ["maryam", "fatimazahra", "abderhmane", "adelphe"]
ASK_PROJECT_NAME, ASK_QUESTION = range(2)

# === TÉLÉCHARGEMENT DES FICHIERS ===
FILE_IDS = {
    "faq": "1XtZesLx35tN-Y0BiOyKfYgmlAIbNkQz5",
    "procedure": "1tQHxKRmejdD7SciBTrA5V_jBA4n_2Sdl",
    "excel": "1Gngwa3SlEbCDKu7e60d1L0qt4f01jIir",
}
gdown.download(id=FILE_IDS["faq"], output="faq.json", quiet=True)
gdown.download(id=FILE_IDS["procedure"], output="procedure.json", quiet=True)
gdown.download(id=FILE_IDS["excel"], output="suivie_sfr.xlsx", quiet=True)

# === LECTURE DES FICHIERS ===
with open("faq_sfr_complet.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

with open("procedure_sfr.json", "r", encoding="utf-8") as f:
    procedure_data = json.load(f)

# === CHARGEMENT EXCEL ===
colonnes_utiles = ["UO", "NB.Lien", "Date de réception", "Odeon", "type de dossier", "Date de depot", "ETAT"]
sfr_df = pd.read_excel("suivie_sfr.xlsx", sheet_name="Avancemment-2025", usecols=colonnes_utiles)

# === NLP ===
classifier = pipeline("text-classification", model="D:/Soutenance MOIS 9/env/intent_classifier_model", tokenizer="D:/Soutenance MOIS 9/env/intent_classifier_model")

labels = [
    "faq", "procédure", "procedure", "processus", "instructions", "marche",
    "étapes de traitement", "traitement projet", "projets_2025"
]

# === NETTOYAGE ===
def clean_value(val):
    return "-" if pd.isna(val) else str(val)

# === COMMANDES DE BASE ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bonjour et bienvenue dans le *Bot SFR* développé par Maryam !\n"
        "Utilise /description pour comprendre le rôle de l'équipe.\n"
        "Utilise /contact pour obtenir les contacts utiles.\n"
        "Utilise /projet pour accéder aux informations projets.",
        parse_mode='Markdown'
    )

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧭 *Objectif du bot :*\n"
        "- Comprendre le rôle de l’équipe SFR\n"
        "- Suivre le processus de traitement des projets\n"
        "- Savoir à qui s’adresser selon les besoins\n"
        "- Intégrer facilement les outils et la méthode de travail",
        parse_mode='Markdown'
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacts_message = (
        "📞 *Contacts utiles :*\n"
        "• Responsable Conduite d'activité : maxim@maneoreseaux.com\n"
        "• Analyste de projet télécom : Maryam@maneoreseaux.com\n"
        "• Chargé d'étude : Abderhmane@maneoreseaux.com\n"
        "• Service RH : Fatima@maneoreseaux.com\n"
        "• Chef d'entreprise : Anass@maneoreseaux.com"
    )
    await update.message.reply_text(contacts_message, parse_mode='Markdown')

# === FLUX DE CONVERSATION POUR /projet ===
async def projet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Avant d'accéder aux projets, quel est votre nom ?")
    return ASK_PROJECT_NAME

async def handle_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nom = update.message.text.strip().lower()
    if nom in UTILISATEURS_AUTORISES:
        await update.message.reply_text(f"✅ Bonjour {nom.capitalize()}, posez votre question sur le projet.")
        return ASK_QUESTION
    else:
        await update.message.reply_text("🚫 Désolé, vous n’êtes pas autorisé(e) à accéder aux projets.")
        return ConversationHandler.END

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    # 🔎 Recherche code projet (ex : P24403)
    match = re.search(r'\bP\d+\b', question.upper())
    if match:
        projet_code = match.group(0)
        df_projet = sfr_df[sfr_df["UO"].astype(str).str.upper() == projet_code]

        if not df_projet.empty:
            projet_info = df_projet.iloc[0]
            texte = (
                f"📊 *Informations du projet {projet_code}* :\n\n"
                f"- 📌 **UO** : {clean_value(projet_info['UO'])}\n"
                f"- 🔗 **NB.Lien** : {clean_value(projet_info['NB.Lien'])}\n"
                f"- 🗓️ **Date de réception** : {clean_value(projet_info['Date de réception'])}\n"
                f"- 🧾 **Odeon** : {clean_value(projet_info['Odeon'])}\n"
                f"- 📂 **Type de dossier** : {clean_value(projet_info['type de dossier'])}\n"
                f"- 📥 **Date de dépôt** : {clean_value(projet_info['Date de depot'])}\n"
                f"- ✅ **État** : {clean_value(projet_info['ETAT'])}"
            )
            await update.message.reply_text(texte, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❓ Projet {projet_code} non trouvé.")
        return ConversationHandler.END

    # 🔍 Sinon NLP
    prediction = classifier(question, candidate_labels=labels)
    top_label = prediction["labels"][0].lower()
    score = prediction["scores"][0]
    print(f"🔍 Intention détectée : {top_label} avec un score de {score:.2f}")

    if "faq" in top_label:
        for item in faq_data["faq"]:
            if item["question"].lower() in question.lower():
                await update.message.reply_text(f"📌 Réponse : {item['réponse']}")
                return ConversationHandler.END
        await update.message.reply_text("❓ Je n'ai pas trouvé de réponse exacte dans la FAQ.")
        
     
    
        
        

       # 📋 Procédure
    elif any(keyword in top_label for keyword in ["procédure", "procedure", "processus", "instructions", "marche", "étapes", "traitement"]):
        proc = procedure_data.get("procedure_SFR")
        if proc:
            description = proc.get("description", "")
            etapes = proc.get("etapes", [])
            texte_procedure = f"*📋 {description}*\n\n"
            for idx, etape in enumerate(etapes, 1):
                titre = etape.get("titre", "-")
                desc = etape.get("description", "-")  # ✅ c'est 'description' et non 'details'
                texte_procedure += f"*Étape {idx}* : {titre}\n_{desc}_\n\n"
        else:
            texte_procedure = "⚠️ Procédure non trouvée dans les données."
        await update.message.reply_text(texte_procedure, parse_mode='Markdown')
    elif "projets_2025" in top_label:
        await update.message.reply_text("📊 Les projets 2025 sont disponibles. Veuillez entrer un code projet (ex : P29700) pour plus de détails.")

    else:
        await update.message.reply_text("❗Je ne comprends pas bien la question. Reformulez-la.")

    return ConversationHandler.END

# === MAIN ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("description", description))
    app.add_handler(CommandHandler("contact", contact))

    projet_handler = ConversationHandler(
        entry_points=[CommandHandler("projet", projet_command)],
        states={
            ASK_PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_project_name)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)],
        },
        fallbacks=[]
    )
    app.add_handler(projet_handler)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot démarré avec succès.")
    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    print("⚙️ Bot lancé avec NLP et sécurité activée.")
