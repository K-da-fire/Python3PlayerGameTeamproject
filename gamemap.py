# game_map.py
from obstacle import WallObstacle
import random
import math


def draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT):
    # 맵 전체 영역
    canvas.create_rectangle(0, UI_HEIGHT, canvas_width, canvas_height, fill="white")
    
    # 골인지점 (오른쪽 상단에 위치)
    canvas.create_rectangle(
        canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE,
        canvas_width - TILE_SIZE, UI_HEIGHT + TILE_SIZE * 2,
        fill="green"
    )

def draw_box(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, key_positions, goal_area):
    obstacles = []
    existing_positions = key_positions.copy()

    shape_options = ["square", "wide", "tall"]

    for _ in range(10):  # 10개의 장애물 생성
        x, y = generate_non_overlapping_obstacle_position(
            existing_positions,
            canvas_width, canvas_height,
            TILE_SIZE, UI_HEIGHT,
            goal_area,
            min_distance=60
        )
        existing_positions.append((x, y))

        shape = random.choice(shape_options)  # 무작위 모양 선택
        obs = WallObstacle(canvas, x, y, shape=shape, duration=99999999)
        obstacles.append(obs)

    return obstacles

def generate_non_overlapping_obstacle_position(existing_positions, canvas_width, canvas_height,
                                               tile_size, ui_height, goal_area, min_distance=60):
    max_attempts = 100
    for _ in range(max_attempts):
        x = random.randint(0, canvas_width - tile_size)
        y = random.randint(ui_height + 20, canvas_height - tile_size)

        # 골인지점 피하기
        goal_x, goal_y, goal_w, goal_h = goal_area
        if goal_x < x < goal_x + goal_w and goal_y < y < goal_y + goal_h:
            continue

        # 기존 장애물/키들과의 거리 확인
        too_close = False
        for px, py in existing_positions:
            distance = math.hypot(x - px, y - py)
            if distance < min_distance:
                too_close = True
                break
        if not too_close:
            return (x, y)

    return (0, ui_height + 20)