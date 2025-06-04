# game_map.py

def draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT):
    # 맵 전체 영역
    canvas.create_rectangle(0, UI_HEIGHT, canvas_width, canvas_height, fill="white")
    
    # 골인지점 (오른쪽 상단에 위치)
    canvas.create_rectangle(
        canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE,
        canvas_width - TILE_SIZE, UI_HEIGHT + TILE_SIZE * 2,
        fill="green"
    )