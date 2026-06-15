import os
from config_loader import PROJECT_ROOT


def load_prompt_profile(config, profile_name):
    relative_path = config["prompt"]["profiles"][profile_name]
    prompt_path = os.path.join(PROJECT_ROOT, relative_path)

    with open(prompt_path, "r") as f:
        return f.read().strip()


def build_full_prompt(config, user_input, profile_name):
    system_prompt = load_prompt_profile(config, profile_name)
    return system_prompt + "\n" + user_input
