import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = '7645422993:AAFkFkkXb3e0RqpZRdL1vuVQn7Incd6ssK8'

async def start(update, context):
    await update.message.reply_text('Bonjour !')

async def echo(update, context):
    text_received = update.message.text.lower()  # texte reçu en minuscules
    if "salut" in text_received:
        await update.message.reply_text("Salut! Comment puis-je t'aider ?")
    else:
        await update.message.reply_text("Je ne comprends pas, essaye 'salut'.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))  # gère les messages texte sauf les commandes

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    print("Bot démarré dans Spyder avec la boucle asyncio déjà active.")
