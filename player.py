from constants import TILE_SIZE

class Player:
    def __init__(self, x, y, color, control_type):
        self.id = None
        self.x = x
        self.y = y
        self.size = TILE_SIZE
        self.color = color
        self.hp = 3
        self.keys = 0
        self.default_speed = 10
        self.speed = self.default_speed
        self.pressed = set()
        self.selected_skill = 0
        self.control_type = control_type
        self.skill_manager = None
        self.slow_end_time = 0
        self.last_dx = 0
        self.last_dy = 0
        self.is_active = True

    def set_skill_manager(self, manager):
        self.skill_manager = manager

    def move(self, canvas_width, canvas_height, ui_height, obstacles):
        if not self.is_active:
            return
        self.update_speed()
        dx = dy = 0
        if self.control_type == "wasd":
            if "w" in self.pressed:
                dy -= self.speed
            if "s" in self.pressed:
                dy += self.speed
            if "a" in self.pressed:
                dx -= self.speed
            if "d" in self.pressed:
                dx += self.speed
        elif self.control_type == "arrow":
            if "Up" in self.pressed:
                dy -= self.speed
            if "Down" in self.pressed:
                dy += self.speed
            if "Left" in self.pressed:
                dx -= self.speed
            if "Right" in self.pressed:
                dx += self.speed

        if dx != 0 or dy != 0:
            self.last_dx = dx
            self.last_dy = dy

        new_x = self.x + dx
        new_y = self.y + dy

        # 충돌 검사
        for obs in obstacles:
            if obs.check_collision_rect(new_x, new_y, self.size, self.size):
                return  # 이동하지 않음

        if 0 <= new_x <= canvas_width - self.size:
            self.x = new_x
        if ui_height <= new_y <= canvas_height - self.size:
            self.y = new_y

    def draw(self, canvas):
        if not self.is_active:
            return
        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.size, self.y + self.size,
            fill=self.color
        )

    def handle_skill_selection(self, key):
        if not self.skill_manager:
            return
        if self.control_type == "wasd" and key in ["g", "h", "k"]:
            self.selected_skill = int(key) - 1
        elif self.control_type == "arrow" and key in ["KP_1", "KP_2", "KP_3"]:
            key_map = {"comma": 0, "period": 1, "slash": 2}
            self.selected_skill = key_map[key]

    def use_selected_skill(self, *args):
        if self.skill_manager:
            return self.skill_manager.use_skill(self.selected_skill)
        return False

    def is_in_goal_area(player, goal_area):
        px, py = player.x, player.y
        pw, ph = player.size, player.size
        gx, gy, gw, gh = goal_area

        return not (
                px + pw < gx or px > gx + gw or
                py + ph < gy or py > gy + gh
        )

    def update_speed(self):
        import time
        current_time = int(time.time() * 1000)
        if self.speed < self.default_speed and current_time >= self.slow_end_time:
            self.speed = self.default_speed

    def slow(self, factor, duration=3000):
        import time
        current_time = int(time.time() * 1000)
        self.speed = self.default_speed * factor

        # 슬로우가 이미 적용되어 있다면 시간만 연장
        self.slow_end_time = max(self.slow_end_time, current_time + duration)

    def push_back(self, canvas, distance=30, steps=10, delay=20):
        dx = -self.last_dx * (distance / steps)
        dy = -self.last_dy * (distance / steps)

        def step(count=0):
            if count >= steps:
                return
            self.x += dx
            self.y += dy
            canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)
            canvas.after(delay, lambda: step(count + 1))

        step()  # 애니메이션 시작

    def is_dead(self):
        return self.hp <= 0

    # TODO : 추후 사망 로직 생성 우선 방법 1로 생성
    #  방법 1. 사망시 삭제 -> 탈락 -> P1, P2 모두 탈락시 P3 승리 추가
    #  방법 2. 사망시 시작 장소로 이동 이 이 플레이어 만 다시 출발 -> 먹은 열쇠를 뱉어야 할지
    def die(self):
        self.hp = 0
        self.is_active = False  # 더 이상 move, draw 등 수행하지 않음
        self.x = -1000  # 화면 밖으로 보내기 (또는 리스트에서 제거)
        self.y = -1000