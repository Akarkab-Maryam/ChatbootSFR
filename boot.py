# -*- coding: utf-8 -*-
"""
Created on Sat May 17 16:36:51 2025
@author: Destock-afric
"""

import asyncio
import nest_asyncio  # Nécessaire dans Spyder
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Ton token (à garder secret !)
BOT_TOKEN = '7645422993:AAFkFkkXb3e0RqpZRdL1vuVQn7Incd6ssK8'

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bonjour ! Je suis ton bot. Écris 'bonjour' pour commencer.")

# Réponse personnalisée selon le message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()

    salutations = [
        "salut", "salut !", "coucou", "bonjour", "bonjour !", "bonsoir", "bonsoir !",
        "hello", "hé", "hey", "hey !", "yo", "wesh", "allo", "allô", "salutations",
        "ça va ?", "ça va", "comment ça va ?", "comment vas-tu ?", "comment allez-vous ?",
        "ça roule ?", "quoi de neuf ?", "quoi de neuf", "bienvenue", "bienvenue !",
        "démarrer", "commencer", "start", "hello chatbot", "bonjour chatbot",
        "salut chatbot", "coucou chatbot", "j’ai une question", "je veux discuter",
        "je veux parler", "est-ce que tu es là ?", "tu es là ?", "on peut parler ?",
        "peux-tu m’aider ?", "aide-moi", "besoin d’aide", "help"
    ]

    if any(greeting in user_message for greeting in salutations):
        await update.message.reply_text(
            "(1) - Nom de l’équipe : Équipe SFR\n"
            "(2) - Les responsables\n"
            "(3) - Objectif de ce chatbot\n"
            "(4) - Livrables à réaliser : PROJET SFR\n"
            "(5) - Livrables à réaliser : PROJET UE\n"
            "(6) - Comment réaliser le projet SFR"
        )

    elif user_message == "1":
        await update.message.reply_text(
            "- Akarkab Maryam\n"
            "- Abderhmane Darouiche\n"
            "- Adelphe\n"
            "- Fatimzhra"
        )
    elif user_message == "2":
        await update.message.reply_text(
            "Responsable d’activité : Maxim (Fait le lien entre le bureau d’étude et les techniciens)\n"
            "Responsable bureau d'étude : Anass (gère le bureau d'étude)"
        )
    elif user_message == "3":
        await update.message.reply_text(
            "Comprendre le rôle de chaque membre\n"
            "Connaître les règles d’ingénierie\n"
            "Être guidé en cas d’erreur ou blocage\n"
            "Recevoir des documents ou images explicatives\n"
            "Répondre automatiquement aux questions fréquentes"
        )
    elif user_message == "4":
        await update.message.reply_text("Livrables :\n- PV\n- REC")
    elif user_message == "5":
        await update.message.reply_text("Livrable : PV UE uniquement")
    elif user_message == "6":
        await update.message.reply_text(
            "Pour réaliser un projet SFR, voici les deux éléments clés à prendre en compte :\n\n"
            "a-1) Retour terrain :\n"
            "Définition : Le retour terrain consiste à collecter des photos des équipements installés sur le terrain. "
            "Ces photos doivent illustrer :\n"
            "- Les baies optiques\n"
            "- Les connecteurs\n"
            "- Les Rocades\n"
            "- Les câblages (y compris les câbles optiques)\n"
            "Ces photos sont cruciales pour vérifier la conformité du travail effectué sur le terrain.\n\n"
            "b-1) Attribution Axis :\n"
            "À récupérer dans le site AXISS SFR."
        )
    else:
        await update.message.reply_text("Je n’ai pas compris. Tapez 'bonjour' pour voir les options.")

# Fonction principale du bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Le bot est en ligne...")
    await app.run_polling()

# Exécution
if __name__ == '__main__':
    try:
        # Si la boucle existe (Spyder, Jupyter...), on l'adapte
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        print("Le bot a démarré dans un environnement avec boucle existante (comme Spyder).")
    except Exception as e:
        # Sinon, on lance la boucle normalement (ex: terminal)
        print("Environnement standard. Lancement normal.")
        asyncio.run(main())
