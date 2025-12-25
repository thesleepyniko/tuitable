import platformdirs
from pathlib import Path
import logging
from datetime import datetime

CONFIG_PATH = Path(platformdirs.user_log_dir("tuitable", "niko"))


def init_log() -> None:
    if not Path.is_dir(CONFIG_PATH):
        Path.mkdir(CONFIG_PATH, exist_ok=True, parents=True)

    log_file = CONFIG_PATH / f"tuitable_{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
        ],
    )


def create_log(name: str, message: str, severity: str = "INFO") -> None:
    logger = logging.getLogger(name)
    logger.log(getattr(logging, severity.upper()), message)
