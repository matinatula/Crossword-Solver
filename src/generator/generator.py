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

        for attempt in range(num_words * 15):  # Increased attempts
            if len(self.words) >= num_words:
                break

            # KEY CHANGE: Randomize which existing word to use for intersection
            word_info = random.choice(self.words)
            existing_word = word_info["word"]

            # KEY CHANGE: Randomize the order of letters to try
            letter_positions = list(enumerate(existing_word))
            random.shuffle(letter_positions)

            word_placed = False
            for i, letter in letter_positions:
                if word_placed:
                    break

                # KEY CHANGE: Randomize word length selection
                available_lengths = [
                    length
                    for length in self.words_by_length.keys()
                    if self.words_by_length[length]
                ]
                random.shuffle(available_lengths)

                for word_len in available_lengths:
                    if word_placed:
                        break

                    candidate_words = self.words_by_length[word_len].copy()
                    random.shuffle(candidate_words)

                    for new_word in candidate_words:
                        if letter in new_word and new_word not in placed_words:
                            # KEY CHANGE: Try all possible positions of the letter in new_word
                            letter_indices = [
                                idx
                                for idx, char in enumerate(new_word)
                                if char == letter
                            ]
                            random.shuffle(letter_indices)

                            for j in letter_indices:
                                if word_info["direction"] == "across":
                                    new_row = word_info["row"] - j
                                    new_col = word_info["col"] + i
                                    new_direction = "down"
                                else:
                                    new_row = word_info["row"] + i
                                    new_col = word_info["col"] - j
                                    new_direction = "across"

                                if self.can_place_word(
                                    new_word, new_row, new_col, new_direction
                                ):
                                    self.place_word(
                                        new_word, new_row, new_col, new_direction
                                    )
                                    placed_words.add(new_word)
                                    word_placed = True
                                    break

                        if word_placed:
                            break

            # KEY CHANGE: Add fallback random placement every few attempts
            if not word_placed and attempt % 20 == 19:
                self._try_random_placement(placed_words, num_words)

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == "":
                    self.grid[r][c] = "#"

        return self.grid, self.words

    def _try_random_placement(self, placed_words, target_words):
        """Try to place a word randomly when intersection fails"""
        if len(self.words) >= target_words:
            return

        # Get available words
        available_words = []
        for length in self.words_by_length:
            for word in self.words_by_length[length]:
                if word not in placed_words:
                    available_words.append(word)

        if not available_words:
            return

        random.shuffle(available_words)

        # Try to place first few words randomly
        for word in available_words[:5]:
            for _ in range(10):  # Try 10 random positions per word
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)
                direction = random.choice(["across", "down"])

                if self.can_place_word(word, row, col, direction):
                    self.place_word(word, row, col, direction)
                    placed_words.add(word)
                    return

    def can_place_word(self, word, row, col, direction):
        if row < 0 or col < 0:
            return False

        if direction == "across":
            if col + len(word) > self.size:
                return False
            for i, letter in enumerate(word):
                if self.grid[row][col + i] not in ("", letter):
                    return False
                # KEY CHANGE: More lenient adjacent cell checking
                if self.grid[row][col + i] == "":
                    # Only check direct adjacency conflicts for empty cells
                    if (row > 0 and self.grid[row - 1][col + i] not in ("", "#")) or (
                        row < self.size - 1
                        and self.grid[row + 1][col + i] not in ("", "#")
                    ):
                        return False
            # Check word boundaries
            if (col > 0 and self.grid[row][col - 1] not in ("", "#")) or (
                col + len(word) < self.size
                and self.grid[row][col + len(word)] not in ("", "#")
            ):
                return False
        else:
            if row + len(word) > self.size:
                return False
            for i, letter in enumerate(word):
                if self.grid[row + i][col] not in ("", letter):
                    return False
                # KEY CHANGE: More lenient adjacent cell checking
                if self.grid[row + i][col] == "":
                    if (col > 0 and self.grid[row + i][col - 1] not in ("", "#")) or (
                        col < self.size - 1
                        and self.grid[row + i][col + 1] not in ("", "#")
                    ):
                        return False
            # Check word boundaries
            if (row > 0 and self.grid[row - 1][col] not in ("", "#")) or (
                row + len(word) < self.size
                and self.grid[row + len(word)][col] not in ("", "#")
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
