import logging
import os


def logging_setup():
    # Remove old log file
    try:
        os.remove("bot.log")
    except FileNotFoundError:
        pass

    logger = logging.getLogger("fake_life_bot")
    discord_logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    discord_logger.setLevel(logging.WARN)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler("bot.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    discord_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARN)
    logger.addHandler(console_handler)
    discord_logger.addHandler(console_handler)
