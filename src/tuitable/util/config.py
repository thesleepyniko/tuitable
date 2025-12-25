import platformdirs
from pathlib import Path
from typing import Any
import yaml

CONFIG_PATH = Path(platformdirs.user_config_dir("tuitable", "niko"))

def init_config() -> None:
    if not Path.is_dir(CONFIG_PATH):
        Path.mkdir(CONFIG_PATH, exist_ok= True, parents = True)
        Path.touch(CONFIG_PATH / "config.yml", exist_ok = True)

def update_value(category: str, name: str, value: Any) -> bool:
    with open(CONFIG_PATH / "config.yml", 'r') as f:
        result = yaml.safe_load(f)
        temp_category = result.get(category, None)
        if temp_category.get(name):
            temp_category[name] = value
            return True
        else:
            return False
