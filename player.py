from constants import TILE_SIZE, POTION_COUNT_PER_PLAYER, POTION_HEAL_AMOUNT, \
    PLAYER_INVINCIBILITY, PLAYER_SPEED_INV
from PIL import Image, ImageTk
import time
import os

class Player:
    image_cache = {}  # 캐시: control_type별 이미지 저장

    def __init__(self, x, y, color, control_type, canvas):
        self.canvas = canvas
        self.id = None
        self.x = x
        self.y = y
        self.size = TILE_SIZE
        self.original_color = color
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
        self.reverse_movement_end_time = 0
        self.is_reversed = False
        self.speed_boost_end_time = 0
        self.is_invincible = False
        self.invincible_end_time = 0
        self.bullets = []
        self.potions = POTION_COUNT_PER_PLAYER  # 시작 포션 개수

        # 이미지 캐싱 처리
        if control_type not in Player.image_cache:
            asset_path = os.path.join(os.path.dirname(__file__), "asset")
            image_path = os.path.join(asset_path, "dog.png" if control_type == "wasd" else "cat.png")
            img = Image.open(image_path).resize((self.size, self.size))
            Player.image_cache[control_type] = ImageTk.PhotoImage(img)

        self.tk_image = Player.image_cache[control_type]

    def set_skill_manager(self, manager):
        self.skill_manager = manager

    def move(self, canvas_width, canvas_height, ui_height, obstacles):
        if not self.is_active:
            return
        self.update_speed()

        current_time = int(time.time() * 1000)
        if self.is_reversed and current_time >= self.reverse_movement_end_time:
            self.is_reversed = False
        if self.is_invincible and current_time >= self.invincible_end_time:
            self.is_invincible = False

            # 무적 상태 해제 확인
        if self.is_invincible and current_time >= self.invincible_end_time:
            self.is_invincible = False
            self.color = "red" if self.control_type == "wasd" else "blue"  # 원래 색상으로 복원

        dx = dy = 0
        if self.control_type == "wasd":
            if "w" in self.pressed: dy -= self.speed
            if "s" in self.pressed: dy += self.speed
            if "a" in self.pressed: dx -= self.speed
            if "d" in self.pressed: dx += self.speed
        elif self.control_type == "arrow":
            if "Up" in self.pressed: dy -= self.speed
            if "Down" in self.pressed: dy += self.speed
            if "Left" in self.pressed: dx -= self.speed
            if "Right" in self.pressed: dx += self.speed

        if self.is_reversed:
            dx *= -1
            dy *= -1

        if dx or dy:
            self.last_dx = dx
            self.last_dy = dy

        new_x, new_y = self.x + dx, self.y + dy

        # 충돌 검사 (무적 상태일 때는 장애물 무시)
        if not self.is_invincible:
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

        if self.id is None or not canvas.find_withtag(self.id):
            self.id = canvas.create_image(
                self.x + self.size // 2,
                self.y + self.size // 2,
                image=self.tk_image,
                anchor="center",
                tags="players"
            )
            if not hasattr(canvas, "image_refs"):
                canvas.image_refs = []
            if self.tk_image not in canvas.image_refs:
                canvas.image_refs.append(self.tk_image)
        else:
            canvas.coords(self.id, self.x + self.size // 2, self.y + self.size // 2)

    def handle_skill_selection(self, key):
        if not self.skill_manager:
            print("no skill manager")
            return

        # P1 스킬 선택 (C, V, B)
        if self.control_type == "wasd":
          if key == "c":
            self.selected_skill = 0
          elif key == "v":
            self.selected_skill = 1
          elif key == "b":
            self.selected_skill = 2
        # P2 스킬 선택 (<, >, ?)
        elif self.control_type == "arrow":
          if key == "comma":  # <
            self.selected_skill = 0
          elif key == "period":  # >
            self.selected_skill = 1
          elif key == "slash":  # ?
            self.selected_skill = 2

    def use_selected_skill(self, target_player=None):
        if self.skill_manager:
            skill = self.skill_manager.get_selected_skill(self.selected_skill)
            if skill and skill.use():
                if self.selected_skill == 0:  # 포션 사용 스킬
                    print("use position")
                    self.use_potion()
                elif self.selected_skill == 1:  # 속도 증가 스킬
                    self.speed_boost(factor=2, duration=PLAYER_SPEED_INV)  # 10초간 2배속
                elif self.selected_skill == 2:  # 무적 스킬
                    self.activate_invincibility(duration=PLAYER_INVINCIBILITY)  # 5초간 무적
                return True
        return False

    def update_speed(self):
        current_time = int(time.time() * 1000)
        if self.speed < self.default_speed and current_time >= self.slow_end_time:
            self.speed = self.default_speed
        if self.speed > self.default_speed and current_time >= self.speed_boost_end_time:
            self.speed = self.default_speed

    def slow(self, factor, duration=PLAYER_SPEED_INV):
        current_time = int(time.time() * 1000)
        self.speed = self.default_speed * factor
        self.slow_end_time = max(self.slow_end_time, current_time + duration)

    def speed_boost(self, factor, duration=3000):
        current_time = int(time.time() * 1000)
        self.speed = self.default_speed * factor
        self.speed_boost_end_time = max(self.speed_boost_end_time, current_time + duration)


    def push_back(self, canvas, distance=30, steps=10, delay=20):
        # Calculate the pushback direction based on the last movement.
        # If last_dx or last_dy is 0, set a default push direction (e.g., away from center or a fixed direction).
        if self.last_dx == 0 and self.last_dy == 0:
            # Default push if no recent movement (e.g., push left)
            dx = -distance / steps
            dy = 0
        else:
            # Reverse the last movement direction
            norm = (self.last_dx**2 + self.last_dy**2)**0.5
            if norm > 0:
                dx = -self.last_dx * (distance / steps) / norm
                dy = -self.last_dy * (distance / steps) / norm
            else:
                dx = 0
                dy = 0


        def step(count=0):
            if count >= steps: return
            self.x += dx
            self.y += dy
            canvas.coords(self.id, self.x + self.size // 2, self.y + self.size // 2)
            canvas.after(delay, lambda: step(count + 1))
        step()

    def start_reverse_movement(self, duration=3000):
        self.is_reversed = True
        self.reverse_movement_end_time = int(time.time() * 1000) + duration

    def activate_invincibility(self, duration=2000):
        self.is_invincible = True
        self.invincible_end_time = int(time.time() * 1000) + duration

    def get_damage(self, dmg):
        if not self.is_invincible:  # 무적 상태가 아닐 때만 데미지 적용
            self.hp -= dmg
            # self.flash_black()
            if self.hp <= 0:
                self.die()

    # def flash_black(self, flashes=3, interval=400):
    #     def toggle(count=0):
    #         if count >= flashes * 2:
    #             return
    #         color = "black" if count % 2 == 0 else self.original_color
    #         self.canvas.itemconfig(self.id, fill=color)
    #         self.canvas.after(interval, lambda: toggle(count + 1))
    #     toggle()

    def is_dead(self):
        return self.hp <= 0

    def is_in_goal_area(player, goal_area):
        px, py = player.x, player.y
        pw, ph = player.size, player.size
        gx, gy, gw, gh = goal_area

        return not (
            px + pw < gx or px > gx + gw or
            py + ph < gy or py > gy + gh
        )

    def die(self):
        self.hp = 0
        self.is_active = False
        self.x = -1000
        self.y = -1000
        if self.id:
            self.canvas.coords(self.id, self.x + self.size // 2, self.y + self.size // 2)

    def heal(self, amount):
        self.hp = min(self.hp + amount, 3)  # 최대 HP 초과 불가

    def use_potion(self):
        if self.potions > 0 and self.hp < 3:
            self.potions -= 1
            self.heal(POTION_HEAL_AMOUNT)
            # self.flash_green()  # 회복 효과 시각화

    # def flash_green(self, flashes=3, interval=200):
    #     def toggle(count=0):
    #         if count >= flashes * 2:
    #             self.canvas.itemconfig(self.id, fill=self.color)
    #             return
    #         color = 'green' if count % 2 == 0 else self.color
    #         self.canvas.itemconfig(self.id, fill=color)
    #         self.canvas.after(interval, lambda: toggle(count + 1))

    def add_potion(self, amount=1):
        self.potions += amount
            # 포션 숫자 강조 효과를 쓸 경우:
        # if hasattr(self, "potion_scale_timer"):
        #     self.potion_scale_timer = 8