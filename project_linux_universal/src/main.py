from config_loader import load_config
from prompt_manager import build_full_prompt
from model_client import run_model
from output_cleaner import clean_output


def main():
    config = load_config()
    current_prompt = config["prompt"]["active_profile"]
    current_model = config["models"]["default"]

    while True:
        user_input = input(">> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if user_input.lower() == "/status":
            print("Current status:")
            print(f"- prompt: {current_prompt}")
            print(f"- model: {current_model}")
            print(f"- server: manually started model in terminal 1")
            continue

        if user_input.lower() == "/prompts":
            print("Available prompts:")
            for name in config["prompt"]["profiles"]:
                marker = " (active)" if name == current_prompt else ""
                print(f"- {name}{marker}")
            continue

        if user_input.startswith("/prompt "):
            requested_prompt = user_input.split(" ", 1)[1].strip()

            if requested_prompt in config["prompt"]["profiles"]:
                current_prompt = requested_prompt
                print(f"Switched prompt to: {current_prompt}")
            else:
                print(f"Unknown prompt: {requested_prompt}")
            continue

        if user_input.lower() == "/models":
            print("Available models:")
            for name, info in config["models"]["available"].items():
                marker = " (active)" if name == current_model else ""
                print(f"- {name}{marker} -> {info['name']}")
            continue

        if user_input.startswith("/model "):
            requested_model = user_input.split(" ", 1)[1].strip()

            if requested_model in config["models"]["available"]:
                current_model = requested_model
                print(f"Switched model to: {current_model}")
            else:
                print(f"Unknown model: {requested_model}")
            continue

        full_prompt = build_full_prompt(config, user_input, current_prompt)
        output = run_model(full_prompt, config, current_model)
        output = clean_output(output)
        print(output)


if __name__ == "__main__":
    main()
