import requests


def run_model(prompt, config, current_model):
    response = requests.post(
        "http://127.0.0.1:8080/completion",
        json={
            "prompt": prompt,
            "n_predict": 256,
            "temperature": config["parameters"]["temperature"]["default"],
            "top_p": config["parameters"]["top_p"]["default"]
        },
        timeout=300
    )
    response.raise_for_status()
    data = response.json()
    return data["content"].strip()
