import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Token de ton bot
BOT_TOKEN = '7645422993:AAFkFkkXb3e0RqpZRdL1vuVQn7Incd6ssK8'

# Liste des utilisateurs autorisés
UTILISATEURS_AUTORISES = ["maryam", "fatimazahra", "abderhmane", "adelphe"]

# Étapes de la conversation
ASK_PROJECT_NAME = range(1)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bonjour et bienvenue dans le *Bot SFR* développé par Maryam !\n"
        "Utilise /description pour comprendre le rôle de l'équipe.\n"
        "Utilise /contact pour obtenir les contacts utiles.\n"
        "Utilise /projet pour accéder aux informations projets."
    )

# Commande /description
async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧭 *Objectif du bot :*\n"
        "- Comprendre le rôle de l’équipe SFR\n"
        "- Suivre le processus de traitement des projets\n"
        "- Savoir à qui s’adresser selon les besoins\n"
        "- Intégrer facilement les outils et la méthode de travail"
    )

# Commande /contact
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacts_message = (
        "📞 *Contacts utiles :*\n"
        "• Responsable Conduite d'activité : maxim@maneoreseaux.com\n"
        "• Analyste de projet télécom : Maryam@maneorseaux.com\n"
        "• Chargé d'étude : Abderhmane@maneorseaux.com\n"
        "• Service Ressources Humaines : Fatima@maneorseaux.com\n"
        "• Chef d'entreprise : Anass@maneorseaux.com"
    )
    await update.message.reply_text(contacts_message, parse_mode='Markdown')

# Commande /projet (début)
async def projet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Avant d'accéder aux projets, quel est votre nom ?")
    return ASK_PROJECT_NAME

# Réponse après nom saisi
async def handle_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nom = update.message.text.strip().lower()
    if nom in UTILISATEURS_AUTORISES:
        await update.message.reply_text(
            f"✅ Bonjour {nom.capitalize()}, vous êtes autorisé. Veuillez poser votre question sur le projet."
        )
    else:
        await update.message.reply_text("🚫 Désolé, vous n’êtes pas autorisé(e) à accéder aux projets.")
    return ConversationHandler.END

# Lancement du bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commandes normales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("description", description))
    app.add_handler(CommandHandler("contact", contact))

    # Conversation pour sécuriser les projets
    projet_handler = ConversationHandler(
        entry_points=[CommandHandler("projet", projet_command)],
        states={
            ASK_PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_project_name)],
        },
        fallbacks=[]
    )
    app.add_handler(projet_handler)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot démarré...")
    await asyncio.Event().wait()

# Exécution dans Spyder avec boucle déjà active
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    print("⚙️ Bot démarré dans Spyder avec la boucle asyncio déjà active.")
