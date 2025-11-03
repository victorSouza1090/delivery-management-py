import logging
import logging.config
from pathlib import Path
import yaml

def setup_logging(name: str = "app", config_path: str | None = None) -> logging.Logger:
    """Carrega logging de YAML e retorna logger principal."""
    if config_path is None:
        config_path = Path(__file__).resolve().parents[2] / "logging.yaml"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)
    return logging.getLogger(name)