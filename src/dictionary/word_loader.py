from pathlib import Path


def load_words():
    word_file = Path(__file__).parent.parent / "data" / "words.txt"
    with open(word_file, "r") as f:
        words = {line.strip() for line in f if line.strip().isalpha()}
    return words
