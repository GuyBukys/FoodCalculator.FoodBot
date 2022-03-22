from googletrans.models import Translated
from requests import Response
from telegram import Update
from telegram.ext import *
import constants
from googletrans import Translator
import requests
import json

FOOD, GRAMS = range(2)
ingredient = ''
amount = 0


def amount_message(update: Update, context):
    global amount
    amount = update.message.text
    update.message.reply_text("מעולה! מחשב את הנתונים..")

    response = get_nutrition_data()
    if response.status_code != 200:
        update.message.reply_text("קרתה שגיאה, אנא נסה שנית")
        return ConversationHandler.END

    content = json.loads(response.content)['nutrients']
    print(content)
    update.message.reply_text("קלוריות: {0}\n פחמימות: {1}\n חלבונים: {2}\n שומנים: {3}\n סוכרים: {4}\n"
                              .format(content[0]['quantity'],
                                      content[1]['quantity'],
                                      content[2]['quantity'],
                                      content[3]['quantity'],
                                      content[4]['quantity']))
    update.message.reply_text("משהו נוסף? אנא הכנס סוג אוכל שברצונך לבדוק")

    return FOOD

def ingredient_message(update: Update, context):
    global ingredient
    ingredient = update.message.text
    update.message.reply_text("אנא הכנס את הכמות בגרמים.")
    return GRAMS


def start_command(update: Update, context):
    update.message.reply_text("ברוך הבא למחשבון הקלוריות! אנא הקלד את שם האוכל הרצוי. לדוגמה : 'חזה עוף'")
    return FOOD


def error_handler(update, context):
    print(f"Error: {context.error}")


def get_nutrition_data() -> Response:
    trans = Translator()
    food_in_hebrew = str(trans.translate(ingredient, src='he', dest='en').text)
    input = {
        'ingredient': food_in_hebrew,
        'amountInGrams': amount
    }
    response = requests.post(constants.FOOD_API_URL + constants.GET_NUTRITION_DATA_REQUEST_URI,
                             json=input,
                             verify=False)

    return response


def main():
    print("Bot is starting..")
    update = Updater(constants.API_KEY, use_context=True)
    dispatcher = update.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            FOOD: [MessageHandler(Filters.text, ingredient_message)],
            GRAMS: [MessageHandler(Filters.text, amount_message)],
        },
        fallbacks=[CommandHandler('error', error_handler)],
    )

    dispatcher.add_handler(conv_handler)

    update.start_polling()
    update.idle()


main()
