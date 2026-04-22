import logging
import sys
from app.core.config import settings

def setup_logging(
    logger_name: str = "shp_api"
) -> logging.Logger:
    """
    Настраивает систему логирования для приложения.

    Конфигурирует вывод логов в файл и в стандартный поток вывода (stdout).
    Использует уровень INFO по умолчанию.

    Args:
        logger_name: Имя создаваемого логгера.

    Returns:
        logging.Logger: Сконфигурированный объект логгера.
    """
    logger = logging.getLogger(logger_name)

    if logger.hasHandlers():
        return logger
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    stream_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(settings.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


logger = setup_logging()