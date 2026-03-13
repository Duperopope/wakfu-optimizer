"""
Systeme de logging unifie pour tout le projet.
Chaque module appelle setup_logger(__name__) pour obtenir un logger configure.
Les logs vont dans la console ET dans logs/wakfu_optimizer.log
"""

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file = os.path.join(config.LOGS_DIR, "wakfu_optimizer.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
