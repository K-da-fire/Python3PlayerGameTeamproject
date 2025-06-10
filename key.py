from constants import TILE_SIZE
import random
import math
from PIL import Image, ImageTk
import os

class Key:
    image_cache = {}  # ✅ 이미지 캐시: owner별 PhotoImage 저장

    def __init__(self, x, y, owner, canvas):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = TILE_SIZE // 2
        self.owner = owner  # 'p1' or 'p2'
        self.collected = False
        self.id = None

        # 캐시된 이미지가 없다면 로드 후 저장
        if owner not in Key.image_cache:
            asset_folder = os.path.join(os.path.dirname(__file__), "asset")
            filename = "dogKey.png" if owner == "p1" else "catKey.png"
            image_path = os.path.join(asset_folder, filename)
            try:
                img = Image.open(image_path).resize((self.size, self.size))
                Key.image_cache[owner] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"❌ 이미지 로딩 실패({owner}): {e}")
                Key.image_cache[owner] = None

        self.tk_image = Key.image_cache[owner]

    def draw(self):
        if self.collected or not self.tk_image:
            if self.id:
                self.canvas.delete(self.id)
            return

        if self.id is None or not self.canvas.find_withtag(self.id):
            self.id = self.canvas.create_image(
                self.x + self.size // 2,
                self.y + self.size // 2,
                image=self.tk_image,
                anchor="center",
                tags="key"
            )
            # ✅ GC 방지용 참조 유지
            if not hasattr(self.canvas, "image_refs"):
                self.canvas.image_refs = []
            if self.tk_image not in self.canvas.image_refs:
                self.canvas.image_refs.append(self.tk_image)
        else:
            self.canvas.coords(self.id, self.x + self.size // 2, self.y + self.size // 2)

    def check(self, player, player_id):
        if self.collected or self.owner != player_id:
            return
        if abs(player.x - self.x) < TILE_SIZE and abs(player.y - self.y) < TILE_SIZE:
            self.collected = True
            player.keys += 1
            if self.id:
                self.canvas.delete(self.id)
                self.id = None


def generate_non_overlapping_key_position(existing_positions, canvas_width, canvas_height,
                                          tile_size, ui_height, goal_area, min_distance=60):
    max_attempts = 100
    for _ in range(max_attempts):
        x = random.randint(0, canvas_width - tile_size)
        y = random.randint(ui_height + 20, canvas_height - tile_size)

        # 골인 영역 제외
        goal_x, goal_y, goal_w, goal_h = goal_area
        if goal_x < x < goal_x + goal_w and goal_y < y < goal_y + goal_h:
            continue

        # 다른 키들과 너무 가까우면 제외
        too_close = any(math.hypot(x - px, y - py) < min_distance for px, py in existing_positions)
        if not too_close:
            return (x, y)

    return (0, ui_height + 20)  # 실패 시 기본 위치 반환