# default
import logging
import inspect

# external
import yaml

# initialization
with open("config\\controls.yml") as file:
    log_controls = yaml.safe_load(file)["data"]["loggers"]


# functions
def set_logger_level(logger, level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    if level == "INFO":
        logger.setLevel(logging.INFO)
    if level == "WARNING":
        logger.setLevel(logging.WARNING)
    if level == "ERROR":
        logger.setLevel(logging.ERROR)
    if level == "CRITICAL":
        logger.setLevel(logging.CRITICAL)


def add_main_handler(logger):
    handler = logging.FileHandler(
        filename=log_controls["logfile"], encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter(log_controls["format"]))
    logger.addHandler(handler)


def standard_logger(level=log_controls["loglevel"]):
    # this supposedly gets the calling module's name. I will read up on how it works now. haha, just a little joke.
    # https://www.calazan.com/how-to-retrieve-the-name-of-the-calling-module-in-python/
    logger = logging.getLogger(inspect.getmodulename(inspect.stack()[1][1]))
    set_logger_level(logger, level)
    add_main_handler(logger)
    return logger
