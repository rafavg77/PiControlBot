import telebot
from telebot.types import ReplyKeyboardRemove
from config.loggin_config import logging, logger, BOT_NAME
from config.loader_config import load_config
from utils.helpers import user_is_allowed
from utils.ngrok_util import NgrokExecutor

logger = logging.getLogger(BOT_NAME)
config = load_config()

ngrok_executor = NgrokExecutor()
ngrok_executor.set_logger(logger)

#Configuración de paramtros
BOT_TOKEN = config.get('BOT_TOKEN', '')
BOT_MASTER = config.get('BOT_MASTER', '')
BOOT_MESSAGE = config.get('BOOT_MESSAGE', '')
USUARIOS_PERMITIROS = config.get('USUARIOS_PERMITIROS', [])

#Configuración de constntes
buttons = {
    "VPN_STATUS" : "💳 Consultar estatus de VPN 💳",
    "VPN_UP" : "💡 Levantar VPN 💡",
    "VPN_DOWN" : "🚿 Bajar VPN 🚿",
    "GET_PUBLIC_IP" :  "🔥 Consultar IP pública de la caseta 🔥",
    "PING" : "🏓 Hacer un ping al bot 🏓"
}

#Se configura API del Bot
bot = telebot.TeleBot(BOT_TOKEN)

#Se instancia el decorador de validación de usuarios.
user_is_allowed_decorator = user_is_allowed(bot, logger, USUARIOS_PERMITIROS)

# Función para crear el teclado personalizado con 3 filas de botones.
def create_custom_keyboard():
    keyboard = []
    for button in buttons:
        keyboard.append([telebot.types.KeyboardButton(buttons[button])])

    reply_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in keyboard:
        reply_markup.row(*row)

    return reply_markup
    
# Manejador para el comando /start y /help.
@bot.message_handler(commands=['start', 'help'])
@user_is_allowed_decorator
def handle_start_help(message):
    bot.send_message(message.chat.id, "Hola mundo", reply_markup=create_custom_keyboard())

# Funcion para enviar parametros al servicio del tunel ngrok
def handle_execute_command(message):
    
    command_to_execute = message.text
    result = ngrok_executor.tunnel_command(command_to_execute,buttons)
    bot.send_message(message.chat.id, f"Salida del comando:\n{result}", reply_markup=ReplyKeyboardRemove())


# Manejador para cualquier otro mensaje que no corresponda a un comando.
@bot.message_handler(func=lambda message: True)
@user_is_allowed_decorator
def handle_other_messages(message):
    if message.text == buttons['VPN_STATUS']:
        handle_execute_command(message)
    elif message.text ==  buttons['VPN_UP']:
        handle_execute_command(message)
    elif message.text == buttons['VPN_DOWN']:
        handle_execute_command(message)
    else:
        bot.send_message(message.chat.id, "Lo siento, no entiendo ese comando.")

    #elif message.text == GET_PUBLIC_IP:
    #        getPublicIPInfo(message)
    #elif message.text == PING:
    #        makePing(message)

# Ejecución Inicial del Bot
logger.info(BOOT_MESSAGE)
bot.send_message(BOT_MASTER, BOOT_MESSAGE)
bot.polling()