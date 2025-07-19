# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 13:20:03 2025

@author: Destock-afric
"""

import asyncio
import json
import os
from datetime import datetime
from collections import Counter



def log_user_question(user, question):
    """
    Sauvegarde chaque question posée par un utilisateur dans un fichier JSON.
    """
    log_file = "questions_log.json"
    
    # Si le fichier existe, on le charge, sinon on crée une liste vide
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    
    # On ajoute une nouvelle entrée
    logs.append({
        "user": user,
        "question": question,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # On sauvegarde la liste mise à jour
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

import pandas as pd
import gdown
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)

# Import du module avec les modèles NLP entraînés
import faq_sfr_complet

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
gdown.download(id=FILE_IDS["faq"], output="faq_sfr_complet.json", quiet=True)
gdown.download(id=FILE_IDS["procedure"], output="procedure_sfr.json", quiet=True)
gdown.download(id=FILE_IDS["excel"], output="avancemment_memoir_modif.xlsx", quiet=True)

# === LECTURE DES FICHIERS ===
with open("faq_sfr_complet.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

with open("procedure_sfr.json", "r", encoding="utf-8") as f:
    procedure_data = json.load(f)

# === CHARGEMENT EXCEL ===
colonnes_utiles = ["UO", "NB.Lien", "Date de réception", "Odeon", "type de dossier", "Date de depot", "ETAT"]
sfr_df = pd.read_excel("avancemment_memoir_modif.xlsx", sheet_name="Avancemment-2025", usecols=colonnes_utiles)

# === NETTOYAGE ===
def clean_value(val):
    return "-" if pd.isna(val) else str(val)

# === COMMANDES DE BASE ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bonjour et bienvenue dans le *Bot SFR* développé par Maryam !\n"
        "Utilise /description pour comprendre le rôle de l'équipe.\n"
        "Utilise /contact pour obtenir les contacts utiles.\n"
        "Utilise /projet pour accéder aux informations projets.\n\n"
        "Utilise /faq pour voir les questions les plus posées.\n\n"
        "Pose ta question directement ici ou tape /projet pour accéder aux projets.",
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
    
# ✅ Nouvelle commande FAQ
async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Affiche les questions les plus posées récemment par les utilisateurs.
    """
    log_file = "questions_log.json"
    
    if not os.path.exists(log_file):
        await update.message.reply_text("❌ Aucun historique de questions pour le moment.")
        return
    
    with open(log_file, "r", encoding="utf-8") as f:
        logs = json.load(f)
    
    all_questions = [entry["question"] for entry in logs]
    
    counter = Counter(all_questions)
    most_common = counter.most_common(5)
    
    message = "📊 *Questions les plus posées récemment :*\n\n"
    for i, (q, count) in enumerate(most_common, 1):
        message += f"{i}. {q} _(posée {count} fois)_\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")


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
    
    # Récupérer le nom ou pseudo Telegram de l'utilisateur
    user = update.message.from_user.username or update.message.from_user.first_name
    # Enregistrer la question
    log_user_question(user, question)
    

    # Recherche code projet (ex : P24403)
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

    # Sinon NLP via faq_sfr_complet
    result = faq_sfr_complet.classifier(question)
    best_label = result[0]['label']
    score = result[0]['score']
    print(f"🔍 Intention détectée : {best_label} (confiance {score:.2f})")

    answer = faq_sfr_complet.get_answer(best_label, question)
    if answer:
        await update.message.reply_text(f"🤖 Réponse : {answer}")
    else:
        await update.message.reply_text("❌ Désolé, je n'ai pas trouvé de réponse pour cette question.")

    return ConversationHandler.END

# === GESTION DES QUESTIONS DIRECTES (hors /projet) ===
async def handle_direct_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text


    # Récupérer le nom ou pseudo Telegram de l'utilisateur
    user = update.message.from_user.username or update.message.from_user.first_name
    # Enregistrer la question
    log_user_question(user, question)

    # On ignore les commandes
    if question.startswith('/'):
        return

    # Recherche code projet (ex : P24403)
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
        return

    # Sinon NLP via faq_sfr_complet
    result = faq_sfr_complet.classifier(question)
    best_label = result[0]['label']
    score = result[0]['score']
    print(f"🔍 Intention détectée (direct) : {best_label} (confiance {score:.2f})")

    answer = faq_sfr_complet.get_answer(best_label, question)
    if answer:
        await update.message.reply_text(f"🤖 Réponse : {answer}")
    else:
        await update.message.reply_text("❌ Désolé, je n'ai pas trouvé de réponse pour cette question.")

# === MAIN ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commandes de base
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("description", description))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("faq", faq_command))   # ✅ on enregistre la commande

    # Conversation sécurisée /projet
    projet_handler = ConversationHandler(
        entry_points=[CommandHandler("projet", projet_command)],
        states={
            ASK_PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_project_name)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)],
        },
        fallbacks=[]
    )
    app.add_handler(projet_handler)

    # Questions directes hors /projet
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_direct_question))

    # Démarrage
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot démarré avec succès.")
    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    print("⚙️ Bot lancé avec NLP et sécurité activée.")
