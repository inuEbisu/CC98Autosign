#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from loguru import logger

logger.remove()
logger.level("DEBUG", color="<white>", icon="-")
logger.level("INFO", color="<light-blue>", icon="*")
logger.level("SUCCESS", color="<light-green>", icon="+")
logger.level("WARNING", color="<light-yellow>", icon="!")
logger.level("ERROR", color="<light-red>", icon="E")
logger.level("CRITICAL", color="<RED>", icon="C")

logger.add(
    sys.stderr, format="[{time:HH:mm:ss}][<level>{level.icon}</level>] {message}"
)

if __name__ == "__main__":
    msg = "This is a test msg"
    logger.trace(msg)
    logger.debug(msg)
    logger.info(msg)
    logger.success(msg)
    logger.warning(msg)
    logger.error(msg)
    logger.critical(msg)
