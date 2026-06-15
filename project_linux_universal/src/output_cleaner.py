def clean_output(text):
    text = text.strip()

    if "[Answer]" in text:
        text = text[text.index("[Answer]"):]

    cut_markers = [
        "\nRules:",
        "\n[Answer]\n\nhow",
        "\n[Answer]\n\nHow",
        "\nAnswer the user's question",
    ]

    cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]

    if cut_positions:
        text = text[:min(cut_positions)].strip()

    return text
