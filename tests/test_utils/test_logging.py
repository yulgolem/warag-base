from src.utils.logging_utils import get_logger


def test_get_logger():
    logger = get_logger("test")
    logger.info("hi")
    assert logger.name == "test"
