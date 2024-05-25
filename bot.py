from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from config import API_TOKEN, TREFLE_API_KEY, TREFLE_API_URL
from database import UserQuery

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для помощи в уходе за домашними растениями. Используйте /help для получения информации о командах.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/plant <название> - поиск информации о растении.\n/history - получение истории ваших запросов.')

def search_plant(update: Update, context: CallbackContext) -> None:
    plant_name = ' '.join(context.args)
    if not plant_name:
        update.message.reply_text('Пожалуйста, укажите название растения после команды /plant.')
        return

    headers = {
        'Authorization': f'Bearer {TREFLE_API_KEY}'
    }
    response = requests.get(f'{TREFLE_API_URL}/plants/search', headers=headers, params={'q': plant_name})
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            plant = data['data'][0]
            plant_info = f"Название: {plant['common_name']}\nНаучное название: {plant['scientific_name']}\nСемейство: {plant['family']}"
            update.message.reply_text(plant_info)

            # Сохранение запроса в базу данных
            UserQuery.create(username=update.message.from_user.username, query=plant_name, response=plant_info)
        else:
            update.message.reply_text('Растение не найдено.')
    else:
        update.message.reply_text('Не удалось получить данные о растении.')

def history(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    queries = UserQuery.select().where(UserQuery.username == username)
    if queries:
        history_text = "\n".join([f"{q.timestamp}: {q.query} - {q.response}" for q in queries])
        update.message.reply_text(history_text)
    else:
        update.message.reply_text('История запросов пуста.')

def main() -> None:
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("plant", search_plant))
    dispatcher.add_handler(CommandHandler("history", history))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
