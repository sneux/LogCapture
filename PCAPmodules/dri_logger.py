import os
import json
import logging
import logging.config

LOGGER_DIR = "log"
LOGGER_FILE = "sys.log"
LOGGER_LEVEL = logging.DEBUG

LoggerConfig = 1
logging.getLogger("requests").setLevel(logging.WARNING)

if LoggerConfig is None:
    try:
        with open("loggerConfig.json") as f:
            LoggerConfig = json.load(f)
    except FileNotFoundError:
        print("Failed to load logger configuration.\nExiting now...")
        exit(-1)
    LOGGER_DIR = LoggerConfig["loggerDir"]
    LOGGER_FILE = LoggerConfig["loggerFile"]
    lvl = LoggerConfig["loggerLevel"]
    if lvl == "INFO":
        LOGGER_LEVEL = logging.INFO
    elif lvl == "WARNING":
        LOGGER_LEVEL = logging.WARNING
    elif lvl == "ERROR":
        LOGGER_LEVEL = logging.ERROR
    elif lvl == "CRITICAL":
        LOGGER_LEVEL = logging.CRITICAL


class DRIFormatter(logging.Formatter):
    datefmt = "%a %b %d %H:%M:%S %Y"
    fmtInfo = "<%(asctime)s> %(levelname)-6s - [%(module)s] %(message)s"
    fmtDebug = "<%(asctime)s> %(levelname)-6s - [%(module)s:%(funcName)s:%(lineno)d] %(message)s"

    def __init__(self):
        super().__init__(fmt=DRIFormatter.fmtDebug, datefmt=DRIFormatter.datefmt)

    def format(self, record):
        self._style._fmt = DRIFormatter.fmtDebug
        if record.levelno == logging.INFO:
            self._style._fmt = DRIFormatter.fmtInfo
        result = logging.Formatter.format(self, record)
        return result


def getLogger(name, loggerFile=None):
    # if os.path.exists(LOGGER_DIR) is False:
    #     os.mkdir(LOGGER_DIR)
    logger = logging.getLogger(name)
    logger.setLevel(LOGGER_LEVEL)
    loggerFormatter = DRIFormatter()

    # if loggerFile is None:
    #     loggerFile = os.path.join(LOGGER_DIR, LOGGER_FILE)
    loggerHandler = logging.handlers.RotatingFileHandler(filename=loggerFile,
                                                         maxBytes=20_000_000,
                                                         backupCount=2)
    loggerHandler.setFormatter(loggerFormatter)
    logger.addHandler(loggerHandler)
    logger.propagate = False
    return logger

