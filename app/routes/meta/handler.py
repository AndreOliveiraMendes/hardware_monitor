import json
from pathlib import Path

from flask import current_app

DEFAULT_CONFIG = {
    "metric_pagination": 100,
    "minmax_pagination": 100,
    "time_window": 1
}

base = Path(current_app.root_path).parent
config_path = base / "data" / "config.json"

def load_config():
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # tenta carregar
    try:
        if not config_path.exists():
            raise FileNotFoundError

        with open(config_path) as f:
            config = json.load(f)

        # valida estrutura mínima
        if not isinstance(config, dict):
            raise ValueError("Config não é dict")

    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        config = DEFAULT_CONFIG.copy()
        save_config(config)
        return config

    # 🔧 merge com defaults (garante chaves novas)
    changed = False
    for k, v in DEFAULT_CONFIG.items():
        if k not in config:
            config[k] = v
            changed = True

    if changed:
        save_config(config)

    return config

def save_config(cfg):
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)