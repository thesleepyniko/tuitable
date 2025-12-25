import platformdirs
from pathlib import Path
from typing import Any
import yaml

CONFIG_PATH = Path(platformdirs.user_config_dir("tuitable", "niko"))

def init_config() -> None:
    if not Path.is_dir(CONFIG_PATH):
        Path.mkdir(CONFIG_PATH, exist_ok=True, parents=True)
        Path.touch(CONFIG_PATH / "config.yml", exist_ok=True)
    elif not Path.is_file(CONFIG_PATH / "config.yml"):
        Path.touch(CONFIG_PATH / "config.yml", exist_ok=True)

def get_config() -> dict[str, Any]:
    with open(CONFIG_PATH / "config.yml", "r") as f:
        return yaml.safe_load(f)

def set_value(category: str, name: str, value: Any) -> bool:
    try:
        with open(CONFIG_PATH / "config.yml", "r") as f:
            config = yaml.safe_load(f)
        if config.get(category, None):
            config[category][name] = value
            with open(CONFIG_PATH / "config.yml", "w") as f2:
                yaml.safe_dump(config, f2)
            return True
        elif config.get(category, None) is None:
            config[category] = {}
            config[category][name] = value
            with open(CONFIG_PATH / "config.yml", "w") as f2:
                yaml.safe_dump(config, f2)
            return True
    except Exception as e:
        return False
        