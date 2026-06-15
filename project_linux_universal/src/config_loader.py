import os
import yaml

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "config",
    "local_llm_spec.yaml"
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
