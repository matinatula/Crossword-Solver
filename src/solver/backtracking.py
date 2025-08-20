from src.dictionary.word_loader import load_words
from typing import List, Dict, Set


class CrosswordSolver:
    def __init__(self, grid: List[List[str]]):
        self.grid = [["#" if cell == "█" else cell for cell in row]
                     for row in grid]

        self.height = len(self.grid)

        max_width = 0
        for row in self.grid:
            if len(row) > max_width:
                max_width = len(row)
        self.width = max_width
        self.grid = [row + ["#"] * (self.width - len(row))
                     for row in self.grid]

        self.words_by_length = self._get_words_by_length()
        self.variables = self._find_variables()
        self.intersections = self._find_intersections()
        self.variable_intersections = self._get_variable_intersections()

    def _find_intersections(self) -> Dict[tuple, tuple]:
        intersections = {}
        for i in range(len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                var1 = self.variables[i]
                var2 = self.variables[j]

                _, _, dir1, _ = var1
                _, _, dir2, _ = var2

                if dir1 == dir2:
                    continue

                if dir1 == "down":
                    across_var, down_var = var2, var1
                else:
                    across_var, down_var = var1, var2

                r_across, c_across, _, len_across = across_var
                r_down, c_down, _, len_down = down_var

                if (
                    c_across <= c_down < c_across + len_across
                    and r_down <= r_across < r_down + len_down
                ):
                    idx_across = c_down - c_across
                    idx_down = r_across - r_down
                    intersections[(across_var, down_var)] = (
                        idx_across, idx_down)
        return intersections

    def _get_variable_intersections(self) -> Dict[tuple, List[tuple]]:
        variable_intersections = {var: [] for var in self.variables}
        for var1, var2 in self.intersections:
            variable_intersections[var1].append(var2)
            variable_intersections[var2].append(var1)
        return variable_intersections

    def _get_words_by_length(self) -> Dict[int, List[str]]:
        all_words = load_words()
        words_by_length = {}
        for word in all_words:
            length = len(word)
            if length not in words_by_length:
                words_by_length[length] = []
            words_by_length[length].append(word)
        return words_by_length

    def _find_variables(self) -> List[tuple]:
        variables = []
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == "#":
                    continue

                is_horizontal_start = (
                    c == 0 or (c > 0 and self.grid[r][c - 1] == "#")
                ) and (c + 1 < self.width and self.grid[r][c + 1] != "#")
                if is_horizontal_start:
                    length = 0
                    temp_c = c
                    while temp_c < self.width and self.grid[r][temp_c] != "#":
                        length += 1
                        temp_c += 1
                    if length > 1:
                        variables.append((r, c, "across", length))

                is_vertical_start = (
                    r == 0 or (r > 0 and self.grid[r - 1][c] == "#")
                ) and (r + 1 < self.height and self.grid[r + 1][c] != "#")
                if is_vertical_start:
                    length = 0
                    temp_r = r
                    while temp_r < self.height and self.grid[temp_r][c] != "#":
                        length += 1
                        temp_r += 1
                    if length > 1:
                        variables.append((r, c, "down", length))
        return variables

    def solve(self):
        yield from self.backtrack({}, set())

    def backtrack(self, assignment: Dict[tuple, str], used_words: Set[str]):
        yield assignment

        if len(assignment) == len(self.variables):
            return

        var = self.select_unassigned_variable(assignment)
        if var is None:
            return

        for word in self.order_domain_values(var, assignment):
            if self.is_consistent(word, used_words):
                assignment[var] = word
                used_words.add(word)
                yield from self.backtrack(assignment, used_words)
                if len(assignment) == len(self.variables):
                    return
                del assignment[var]
                used_words.remove(word)

    def get_pattern(self, var: tuple, assignment: Dict[tuple, str]) -> List[str]:
        r, c, direction, length = var
        pattern = [""] * length

        for i in range(length):
            current_r, current_c = r, c
            if direction == "across":
                current_c += i
            else:
                current_r += i

            if (
                self.grid[current_r][current_c] != " "
                and self.grid[current_r][current_c] != "#"
            ):
                pattern[i] = self.grid[current_r][current_c]

        for other_var in self.variable_intersections[var]:
            if other_var in assignment:
                intersection = self.intersections.get((var, other_var))
                if not intersection:
                    intersection = self.intersections.get((other_var, var))
                    idx_in_var = intersection[1]
                    idx_in_other_var = intersection[0]
                else:
                    idx_in_var = intersection[0]
                    idx_in_other_var = intersection[1]

                pattern[idx_in_var] = assignment[other_var][idx_in_other_var]
        return pattern

    def select_unassigned_variable(self, assignment: Dict[tuple, str]) -> tuple:
        unassigned_vars = [v for v in self.variables if v not in assignment]

        best_var = None
        min_count = float("inf")

        for var in unassigned_vars:
            pattern = self.get_pattern(var, assignment)
            length = var[3]

            count = 0
            words_to_check = self.words_by_length.get(length, [])
            for word in words_to_check:
                match = True
                for i, char in enumerate(pattern):
                    if char != "" and char != word[i]:
                        match = False
                        break
                if match:
                    count += 1

            if count < min_count:
                min_count = count
                best_var = var

        return best_var

    def order_domain_values(
        self, var: tuple, assignment: Dict[tuple, str]
    ) -> List[str]:
        length = var[3]
        pattern = self.get_pattern(var, assignment)

        candidate_words = []
        words_to_check = self.words_by_length.get(length, [])
        for word in words_to_check:
            match = True
            for i, char in enumerate(pattern):
                if char != "" and char != word[i]:
                    match = False
                    break
            if match:
                candidate_words.append(word)

        return candidate_words

    def is_consistent(self, word: str, used_words: Set[str]) -> bool:
        return word not in used_words

    def get_grid_with_solution(self, assignment: Dict[tuple, str]) -> List[List[str]]:

        grid = [row[:] for row in self.grid]

        for var, word in assignment.items():
            r, c, direction, length = var
            for i in range(length):
                if direction == "across":
                    grid[r][c + i] = word[i]
                else:
                    grid[r + i][c] = word[i]
        return grid
