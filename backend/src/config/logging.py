import logging
import logging.config

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )