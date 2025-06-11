from obstacle import WallObstacle
from PIL import Image, ImageTk
import random
import math
import os

def draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT):
    # === 배경 이미지 불러오기 ===
    asset_folder = os.path.join(os.path.dirname(__file__), "asset")
    bg_path = os.path.join(asset_folder, "background.png")

    try:
        bg_image = Image.open(bg_path).resize((canvas_width, canvas_height - UI_HEIGHT))
        tk_bg_image = ImageTk.PhotoImage(bg_image)

        # 이미지 참조 유지 (GC 방지)
        canvas.bg_refs = getattr(canvas, "bg_refs", [])
        canvas.bg_refs.append(tk_bg_image)

        canvas.create_image(
            0, UI_HEIGHT,
            image=tk_bg_image,
            anchor="nw",
            tags="background"
        )
        canvas.lower("background")  # 가장 뒤로 보냄

    except Exception as e:
        print(f"❌ 배경 이미지 로딩 실패: {e}")
        # fallback: 흰 배경
        canvas.create_rectangle(0, UI_HEIGHT, canvas_width, canvas_height, fill="white", tags="background")

    # === 골인지점 (오른쪽 상단) ===
    canvas.create_rectangle(
        canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE,
        canvas_width - TILE_SIZE, UI_HEIGHT + TILE_SIZE * 2,
        fill="green", tags="map"
    )

def draw_box(canvas, canvas_width, canvas_height, tile_size, ui_height,
             positions_to_avoid, goal_area, box_count=10, min_distance=60):
    obstacles = []
    shape_options = ["square", "wide", "tall"]

    for _ in range(box_count):
        x, y = generate_non_overlapping_obstacle_position(
            positions_to_avoid,
            canvas_width,
            canvas_height,
            tile_size,
            ui_height,
            goal_area,
            min_distance
        )
        shape = random.choice(shape_options)  # 무작위 모양 선택
        obs = WallObstacle(canvas, x, y, shape=shape, color="gray",
                           duration=99999999)
        obstacles.append(obs)

        # 새로 생성한 장애물 위치도 제외 리스트에 추가
        positions_to_avoid.append((x, y))

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
