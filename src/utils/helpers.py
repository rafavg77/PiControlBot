import telebot

def get_user_name(bot, logger, user_id):
    try:
        user_info = bot.get_chat_member(user_id, user_id)
        return user_info.user.first_name
    except telebot.apihelper.ApiException:
        return logger.warning(f"No se pudo resolver el nombre de (ID: {user_id})")

def user_is_allowed(bot, logger, usuarios_permitidos, BOT_MASTER):
    def decorator(func):
        def wrapper(message):
            user_id = message.from_user.id
            user_name = get_user_name(bot, logger, user_id)
            if user_id in usuarios_permitidos:
                # Registra y muestra el comando o acción ejecutada por el usuario.
                command = message.text
                logger.info(f"Usuario {user_name} (ID: {user_id}) ejecutó el comando: {command}")
                return func(message)
            else:
                logger.warning(f"Intento de ejecución de comando por un usuario no autorizado: Usuario {user_name} (ID: {user_id}), Comando: {message.text}")
                bot.send_message(BOT_MASTER,f"Intento de ejecución de comando por un usuario no autorizado: Usuario {user_name} (ID: {user_id}), Comando: {message.text}")
                bot.send_message(message.chat.id, "Lo siento, no tienes permitido interactuar con este bot.")
        return wrapper
    return decorator

# Anotación de tipo para marcar las funciones que deben estar disponibles en el teclado
def keyboard_function(func):
    func.keyboard = True
    return func