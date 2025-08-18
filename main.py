import time
from src.generator.generator import CrosswordGenerator
from src.solver.backtracking import CrosswordSolver
from src.display import animate_solution, display_crossword


def main():
    # 1. Generate a crossword puzzle
    generator = CrosswordGenerator(size=10)
    grid, words = generator.generate(num_words=5)

    # 2. Create a puzzle with one word revealed
    puzzle_grid = [["#" if cell == "#" else " " for cell in row] for row in grid]
    if words:
        first_word_info = words[0]
        word = first_word_info["word"]
        r, c = first_word_info["row"], first_word_info["col"]
        direction = first_word_info["direction"]

        for i in range(len(word)):
            if direction == "across":
                puzzle_grid[r][c + i] = word[i]
            else:
                puzzle_grid[r + i][c] = word[i]

    # Display the partially solved grid
    display_crossword(puzzle_grid, [words[0]] if words else [])
    time.sleep(5)

    # 3. Solve the puzzle
    solver = CrosswordSolver(puzzle_grid)
    solution_stream = solver.solve()

    # 4. Animate the solution
    word_info = []
    for var in solver.variables:
        r, c, direction, _ = var
        word_info.append({"word": "", "row": r, "col": c, "direction": direction})

    animate_solution(puzzle_grid, word_info, solution_stream)


if __name__ == "__main__":
    main()
