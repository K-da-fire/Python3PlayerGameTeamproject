from constants import TILE_SIZE
import random
import math

# key.py

class Key:
    def __init__(self, x, y, owner):
        self.x = x
        self.y = y
        self.size = TILE_SIZE // 2  # 혹은 따로 상수 선언
        self.owner = owner
        self.collected = False
        self.id = None

    def draw(self, canvas):
        if self.collected:
            if self.id:
                canvas.delete(self.id)
            return
        color = "red" if self.owner == "p1" else "blue"
        self.id = canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill=color, tags="key")

    def check(self, player, player_id):
        if self.collected or self.owner != player_id:
            return
        if abs(player.x - self.x) < TILE_SIZE and abs(player.y - self.y) < TILE_SIZE:
            self.collected = True
            player.keys += 1

def generate_non_overlapping_key_position(existing_positions, canvas_width, canvas_height, 
                                          tile_size, ui_height, goal_area, min_distance=60):
    max_attempts = 100
    for _ in range(max_attempts):
        x = random.randint(0, canvas_width - tile_size)
        y = random.randint(ui_height + 20, canvas_height - tile_size)

        # 골인지점과 거리 검사
        goal_x, goal_y, goal_w, goal_h = goal_area
        if goal_x < x < goal_x + goal_w and goal_y < y < goal_y + goal_h:
            continue

        # 기존 키들과 거리 검사
        too_close = False
        for px, py in existing_positions:
            distance = math.hypot(x - px, y - py)
            if distance < min_distance:
                too_close = True
                break
        if not too_close:
            return (x, y)

    return (0, ui_height + 20)