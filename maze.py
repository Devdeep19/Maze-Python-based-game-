import tkinter as tk
from tkinter import ttk
import random

CELL_SIZE = 30

DIFFICULTIES = {
    "Easy": (10, 10, 180),
    "Medium": (15, 15, 120),
    "Hard": (20, 20, 90)
}

class MazeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Game")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack()

        # Left side: Controls
        self.left_panel = tk.Frame(self.main_frame)
        self.left_panel.pack(side="left", padx=10, pady=10)

        self.button_frame = tk.Frame(self.left_panel)
        self.button_frame.pack()

        for name in DIFFICULTIES:
            btn = tk.Button(self.button_frame, text=name, font=("Arial", 12),
                            command=lambda n=name: self.set_difficulty(n))
            btn.pack(side="left", padx=5)

        self.restart_btn = tk.Button(self.left_panel, text="Restart", font=("Arial", 12),
                                     command=self.restart_game, state="disabled")
        self.restart_btn.pack(pady=10)

        # Right side: Info
        self.right_panel = tk.Frame(self.main_frame)
        self.right_panel.pack(side="right", padx=10, pady=10)

        self.score_label = tk.Label(self.right_panel, text="Score: 0", font=("Arial", 14))
        self.score_label.pack(pady=5)

        self.timer_label = tk.Label(self.right_panel, text="Time: 0", font=("Arial", 14))
        self.timer_label.pack(pady=5)

        self.timer_bar = ttk.Progressbar(self.right_panel, orient="horizontal", length=200, mode="determinate")
        self.timer_bar.pack(pady=5)

        self.canvas = tk.Canvas(self.main_frame, bg='white')
        self.canvas.pack(padx=10, pady=10)

        self.after_id = None
        self.game_started = False
        self.player = None
        self.trail = []

    def set_difficulty(self, level):
        self.difficulty = level
        self.rows, self.cols, self.time_limit = DIFFICULTIES[level]
        self.canvas.config(width=self.cols * CELL_SIZE, height=self.rows * CELL_SIZE)
        self.start_game()

    def start_game(self):
        self.game_started = True
        self.restart_btn.config(state="normal")
        self.score = 0
        self.time_left = self.time_limit
        self.total_time = self.time_limit
        self.player_pos = [0, 0]
        self.player = None
        self.trail = []

        self.maze = [[{'visited': False, 'walls': {'top': True, 'bottom': True, 'left': True, 'right': True}} for _ in range(self.cols)] for _ in range(self.rows)]
        self.generate_maze(0, 0)

        self.canvas.delete("all")
        self.draw_maze()
        self.draw_special_cells()
        self.draw_player()

        self.root.bind('<Key>', self.move_player)
        self.update_score()
        self.update_timer()

    def restart_game(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.start_game()

    def generate_maze(self, r, c):
        stack = [(r, c)]
        self.maze[r][c]['visited'] = True
        while stack:
            r, c = stack[-1]
            directions = []
            if r > 0 and not self.maze[r - 1][c]['visited']:
                directions.append(('top', r - 1, c))
            if r < self.rows - 1 and not self.maze[r + 1][c]['visited']:
                directions.append(('bottom', r + 1, c))
            if c > 0 and not self.maze[r][c - 1]['visited']:
                directions.append(('left', r, c - 1))
            if c < self.cols - 1 and not self.maze[r][c + 1]['visited']:
                directions.append(('right', r, c + 1))

            if directions:
                direction, nr, nc = random.choice(directions)
                if direction == 'top':
                    self.maze[r][c]['walls']['top'] = False
                    self.maze[nr][nc]['walls']['bottom'] = False
                elif direction == 'bottom':
                    self.maze[r][c]['walls']['bottom'] = False
                    self.maze[nr][nc]['walls']['top'] = False
                elif direction == 'left':
                    self.maze[r][c]['walls']['left'] = False
                    self.maze[nr][nc]['walls']['right'] = False
                elif direction == 'right':
                    self.maze[r][c]['walls']['right'] = False
                    self.maze[nr][nc]['walls']['left'] = False
                self.maze[nr][nc]['visited'] = True
                stack.append((nr, nc))
            else:
                stack.pop()

    def draw_maze(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c * CELL_SIZE, r * CELL_SIZE
                cell = self.maze[r][c]
                if cell['walls']['top']:
                    self.canvas.create_line(x, y, x + CELL_SIZE, y)
                if cell['walls']['right']:
                    self.canvas.create_line(x + CELL_SIZE, y, x + CELL_SIZE, y + CELL_SIZE)
                if cell['walls']['bottom']:
                    self.canvas.create_line(x, y + CELL_SIZE, x + CELL_SIZE, y + CELL_SIZE)
                if cell['walls']['left']:
                    self.canvas.create_line(x, y, x, y + CELL_SIZE)

    def draw_special_cells(self):
        self.canvas.create_rectangle(5, 5, CELL_SIZE - 5, CELL_SIZE - 5, fill="lightgreen", outline="")
        end_x, end_y = (self.cols - 1) * CELL_SIZE + 5, (self.rows - 1) * CELL_SIZE + 5
        self.canvas.create_rectangle(end_x, end_y, end_x + CELL_SIZE - 10, end_y + CELL_SIZE - 10, fill="red", outline="")

    def draw_player(self):
        x, y = self.player_pos[1] * CELL_SIZE + 5, self.player_pos[0] * CELL_SIZE + 5
        if self.player:
            self.canvas.delete(self.player)
        self.trail.append((x, y))  # Add to trail
        for tx, ty in self.trail:
            self.canvas.create_oval(tx + 6, ty + 6, tx + CELL_SIZE - 16, ty + CELL_SIZE - 16, fill="#add8e6", outline="")

        self.player = self.canvas.create_oval(x, y, x + CELL_SIZE - 10, y + CELL_SIZE - 10, fill="blue")

    def move_player(self, event):
        if not self.game_started:
            return

        r, c = self.player_pos
        cell = self.maze[r][c]

        if event.keysym == 'Up' and not cell['walls']['top']:
            self.player_pos[0] -= 1
        elif event.keysym == 'Down' and not cell['walls']['bottom']:
            self.player_pos[0] += 1
        elif event.keysym == 'Left' and not cell['walls']['left']:
            self.player_pos[1] -= 1
        elif event.keysym == 'Right' and not cell['walls']['right']:
            self.player_pos[1] += 1
        else:
            return

        self.score += 1
        self.update_score()
        self.draw_player()

        if self.player_pos == [self.rows - 1, self.cols - 1]:
            self.canvas.create_text(self.cols * CELL_SIZE // 2, self.rows * CELL_SIZE // 2, text="You Win!", font=("Arial", 24), fill="green")
            self.root.unbind('<Key>')
            self.game_started = False
            if self.after_id:
                self.root.after_cancel(self.after_id)

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def update_timer(self):
        if self.game_started and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}")
            self.timer_bar['value'] = ((self.total_time - self.time_left) / self.total_time) * 100
            self.after_id = self.root.after(1000, self.update_timer)
        elif self.game_started:
            self.canvas.create_text(self.cols * CELL_SIZE // 2, self.rows * CELL_SIZE // 2, text="Time's Up!", font=("Arial", 24), fill="red")
            self.root.unbind('<Key>')
            self.game_started = False

# Run it
root = tk.Tk()
game = MazeGame(root)
root.mainloop()
