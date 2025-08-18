import random
from src.dictionary.word_loader import load_words


class CrosswordGenerator:
    def __init__(self, size=15):
        self.size = size
        self.grid = [["" for _ in range(size)] for _ in range(size)]
        self.words = []
        self.words_by_length = self._get_words_by_length()

    def _get_words_by_length(self):
        all_words = load_words()
        words_by_length = {}
        for word in all_words:
            length = len(word)
            if length not in words_by_length:
                words_by_length[length] = []
            words_by_length[length].append(word)
        return words_by_length

    def generate(self, num_words=30):
        start_word = random.choice(
            self.words_by_length.get(
                self.size, self.words_by_length.get(self.size - 1, [])
            )
        )
        row = self.size // 2
        col = (self.size - len(start_word)) // 2
        self.place_word(start_word, row, col, "across")

        placed_words = {start_word}

        for _ in range(num_words * 10):
            if len(self.words) >= num_words:
                break

            word_info = random.choice(self.words)
            existing_word = word_info["word"]

            for i, letter in enumerate(existing_word):
                for word_len in self.words_by_length:
                    candidate_words = self.words_by_length[word_len]
                    random.shuffle(candidate_words)
                    for new_word in candidate_words:
                        if letter in new_word and new_word not in placed_words:
                            j = new_word.find(letter)
                            if word_info["direction"] == "across":
                                new_row = word_info["row"] - j
                                new_col = word_info["col"] + i
                                if self.can_place_word(
                                    new_word, new_row, new_col, "down"
                                ):
                                    self.place_word(new_word, new_row, new_col, "down")
                                    placed_words.add(new_word)
                                    break
                            else:
                                new_row = word_info["row"] + i
                                new_col = word_info["col"] - j
                                if self.can_place_word(
                                    new_word, new_row, new_col, "across"
                                ):
                                    self.place_word(
                                        new_word, new_row, new_col, "across"
                                    )
                                    placed_words.add(new_word)
                                    break
                    else:
                        continue
                    break

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == "":
                    self.grid[r][c] = "#"

        return self.grid, self.words

    def can_place_word(self, word, row, col, direction):
        if row < 0 or col < 0:
            return False

        if direction == "across":
            if col + len(word) > self.size:
                return False
            for i, letter in enumerate(word):
                if self.grid[row][col + i] not in ("", letter):
                    return False
                if self.grid[row][col + i] == "":
                    if (row > 0 and self.grid[row - 1][col + i] != "") or (
                        row < self.size - 1 and self.grid[row + 1][col + i] != ""
                    ):
                        return False
            if (col > 0 and self.grid[row][col - 1] != "") or (
                col + len(word) < self.size and self.grid[row][col + len(word)] != ""
            ):
                return False
        else:
            if row + len(word) > self.size:
                return False
            for i, letter in enumerate(word):
                if self.grid[row + i][col] not in ("", letter):
                    return False
                if self.grid[row + i][col] == "":
                    if (col > 0 and self.grid[row + i][col - 1] != "") or (
                        col < self.size - 1 and self.grid[row + i][col + 1] != ""
                    ):
                        return False
            if (row > 0 and self.grid[row - 1][col] != "") or (
                row + len(word) < self.size and self.grid[row + len(word)][col] != ""
            ):
                return False

        return True

    def place_word(self, word, row, col, direction):
        self.words.append(
            {"word": word, "row": row, "col": col, "direction": direction}
        )
        for i, letter in enumerate(word):
            if direction == "across":
                self.grid[row][col + i] = letter
            else:
                self.grid[row + i][col] = letter

    def print_grid(self):
        for row in self.grid:
            print("  ".join(row if row else "#"))
