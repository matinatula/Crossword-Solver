import matplotlib.pyplot as plt
import matplotlib.animation as animation


def display_crossword(grid, words):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                ax.add_patch(plt.Rectangle((c, rows - 1 - r), 1, 1, facecolor="black"))
            else:
                ax.add_patch(
                    plt.Rectangle(
                        (c, rows - 1 - r), 1, 1, facecolor="white", edgecolor="black"
                    )
                )
                ax.text(
                    c + 0.5,
                    rows - 1 - r + 0.5,
                    grid[r][c],
                    ha="center",
                    va="center",
                    fontsize=12,
                )

    clue_numbers = {}
    clue_counter = 1
    sorted_words = sorted(words, key=lambda x: (x["row"], x["col"]))
    for word_info in sorted_words:
        r, c = word_info["row"], word_info["col"]
        if (r, c) not in clue_numbers:
            clue_numbers[(r, c)] = clue_counter
            ax.text(
                c + 0.1,
                rows - 1 - r + 0.9,
                str(clue_counter),
                ha="left",
                va="top",
                fontsize=8,
            )
            clue_counter += 1

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.show()


def animate_solution(grid, words, solution_stream):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    rows, cols = len(grid), len(grid[0])

    def update(assignment):
        ax.clear()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        solved_grid = [row[:] for row in grid]
        for var, word in assignment.items():
            r, c, direction, length = var
            for i in range(length):
                if direction == "across":
                    solved_grid[r][c + i] = word[i]
                else:
                    solved_grid[r + i][c] = word[i]

        for r in range(rows):
            for c in range(cols):
                if solved_grid[r][c] == "#":
                    ax.add_patch(
                        plt.Rectangle((c, rows - 1 - r), 1, 1, facecolor="black")
                    )
                else:
                    ax.add_patch(
                        plt.Rectangle(
                            (c, rows - 1 - r),
                            1,
                            1,
                            facecolor="white",
                            edgecolor="black",
                        )
                    )
                    ax.text(
                        c + 0.5,
                        rows - 1 - r + 0.5,
                        solved_grid[r][c],
                        ha="center",
                        va="center",
                        fontsize=12,
                    )

        clue_numbers = {}
        clue_counter = 1
        sorted_words = sorted(words, key=lambda x: (x["row"], x["col"]))
        for word_info in sorted_words:
            r, c = word_info["row"], word_info["col"]
            if (r, c) not in clue_numbers:
                clue_numbers[(r, c)] = clue_counter
                ax.text(
                    c + 0.1,
                    rows - 1 - r + 0.9,
                    str(clue_counter),
                    ha="left",
                    va="top",
                    fontsize=8,
                )
                clue_counter += 1

        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=solution_stream,
        repeat=False,
        interval=500,
        cache_frame_data=False,
    )
    plt.show()
