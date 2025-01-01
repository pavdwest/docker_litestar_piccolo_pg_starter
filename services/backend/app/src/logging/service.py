import sys

import loguru


# https://betterstack.com/community/guides/logging/loguru/
logger = loguru.logger
logger.remove()
logger.add(sys.stdout, colorize=True, enqueue=True)
