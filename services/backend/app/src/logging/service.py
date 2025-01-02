# import sys

# import loguru


# # https://betterstack.com/community/guides/logging/loguru/
# logger = loguru.logger
# logger.remove()
# logger.add(sys.stdout, colorize=True, enqueue=True)


import logging
import coloredlogs


logger = coloredlogs.logging.getLogger(__name__)


def reset_logger():
    coloredlogs.install(isatty=True)
    logger = coloredlogs.logging.getLogger(__name__)

reset_logger()
logging.warning('Logger initialised')
