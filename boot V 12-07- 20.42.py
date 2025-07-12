import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = '7645422993:AAFkFkkXb3e0RqpZRdL1vuVQn7Incd6ssK8'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bonjour et bienvenue dans le *Bot SFR* développé par Maryam !\n"
        "Utilise /description pour comprendre le rôle de l'équipe.\n"
        "Utilise /date pour obtenir l'heure actuelle."
    )

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧭 *Objectif du bot :*\n"
        "- Comprendre le rôle de l’équipe SFR\n"
        "- Suivre le processus de traitement des projets\n"
        "- Savoir à qui s’adresser selon les besoins\n"
        "- Intégrer facilement les outils et la méthode de travail"
    )

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    formatted = now.strftime("🕒 Date et heure actuelles : %d/%m/%Y à %H:%M:%S")
    await update.message.reply_text(formatted)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("description", description))
    app.add_handler(CommandHandler("date", date))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Bot démarré...")
    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    print("Bot démarré dans Spyder avec la boucle asyncio déjà active.")
