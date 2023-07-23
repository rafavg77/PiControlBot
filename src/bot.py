import telebot
from telebot.types import ReplyKeyboardRemove
from config.loggin_config import logging, logger, BOT_NAME
from config.loader_config import load_config
from utils.helpers import user_is_allowed
from utils.ngrok_util import NgrokExecutor
from APiHole import PiHole

logger = logging.getLogger(BOT_NAME)
config = load_config()

ngrok_executor = NgrokExecutor()
ngrok_executor.set_logger(logger)

#Configuración de paramtros
BOT_TOKEN = config.get('BOT_TOKEN', '')
BOT_MASTER = config.get('BOT_MASTER', '')
BOOT_MESSAGE = config.get('BOOT_MESSAGE', '')
USUARIOS_PERMITIROS = config.get('USUARIOS_PERMITIROS', [])
PIHOLE_ADDRESS = config.get('PIHOLE_ADDRESS', '')
PIHOLE_AUTH = config.get('PIHOLE_AUTH', '')


#Configuración de constntes
buttons = {
    "VPN_STATUS" : "💳 Consultar estatus de VPN 💳",
    "VPN_UP" : "💡 Levantar VPN 💡",
    "VPN_DOWN" : "🚿 Bajar VPN 🚿",
    "PING" : "🏓 Hacer un ping al bot 🏓",
    "NGROK_CHANGE" : "Revisar cambio de tunnel",
    "PIHOLE_STATUS" : "🔥 Status de bloqueo PiHole 🔥",
    "PIHOLE_CHANGE" : "🎮 Cambiar Status de bloqueo PiHole 🎮"
}

#Se configura API del Bot
bot = telebot.TeleBot(BOT_TOKEN)
PiHoleAPI= PIHOLE_AUTH
PiIP=PIHOLE_ADDRESS

#Se instancia el decorador de validación de usuarios.
user_is_allowed_decorator = user_is_allowed(bot, logger, USUARIOS_PERMITIROS, BOT_MASTER)

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

# Funcion para enviar parametros al servicio del tunel ngrok
def handle_change_ngrok(message):
    command_to_execute = message.text
    result = ngrok_executor.tunnel_detect_change_addres(message,bot)
    bot.send_message(message.chat.id, f"Salida del comando:\n{result}", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['blockStatus'])
@user_is_allowed_decorator
def send_block_status(message):
    status = PiHole.GetStatus(PiIP,PiHoleAPI)
    status_value = status.split(" ")[1]
    
    bot.send_message(message.chat.id, "Blocking Status is: " + status_value)

@bot.message_handler(commands=['changeBlockStatus'])
@user_is_allowed_decorator
def send_change_block_status(message):
    status = PiHole.GetStatus(PiIP,PiHoleAPI)
    status_value = status.split(" ")[1]
    
    
    if status_value == "disabled":
        PiHole.Enable(PiIP,PiHoleAPI)
        bot.send_message(message.chat.id, "Blocking Status is: Enabled")
    elif status_value == "enabled":
        PiHole.Disable(PiIP,PiHoleAPI,0)
        bot.send_message(message.chat.id, "Blocking Status is: Disabled")

#Comando que recibe ping y reponde pong
@bot.message_handler(commands=['makePing'])
@user_is_allowed_decorator
def makePing(message):
    bot.send_message(message.chat.id, "Pong 🏓")

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
    elif message.text == buttons['NGROK_CHANGE']:
        handle_change_ngrok(message)
    elif message.text == buttons['PING']:
        makePing(message)
    elif message.text == buttons['PIHOLE_STATUS']:
        send_block_status(message)
    elif message.text == buttons['PIHOLE_CHANGE']:
        send_change_block_status(message)
        
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