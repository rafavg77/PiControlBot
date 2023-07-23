import logging

BOT_NAME = "PiControlBot"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s] - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()  # Agrega el StreamHandler para mostrar logs en la consola
    ]
)

logger = logging.getLogger(BOT_NAME)