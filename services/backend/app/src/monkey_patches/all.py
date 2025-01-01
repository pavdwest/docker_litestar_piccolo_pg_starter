from src.logging.service import logger
from src.monkey_patches import piccolo_orm


def apply_all_monkey_patches():
    logger.info("Applying all monkey patches.")
    piccolo_orm.patch()
