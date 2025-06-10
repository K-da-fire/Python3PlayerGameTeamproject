import time
from constants import TILE_SIZE

class Player:
    def __init__(self, x, y, color, control_type, canvas):
        self.canvas = canvas
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
        self.reverse_movement_end_time = 0  # 역방향 이동 종료 시간 추가
        self.is_reversed = False # 역방향 이동 상태 추가

        # 새로운 스킬 관련 속성
        self.speed_boost_end_time = 0
        self.is_invincible = False
        self.invincible_end_time = 0
        self.bullets = [] # 발사된 총알들을 저장할 리스트


    def set_skill_manager(self, manager):
        self.skill_manager = manager

    def move(self, canvas_width, canvas_height, ui_height, obstacles):
        if not self.is_active:
            return

        self.update_speed()

        # 역방향 이동 시간 확인
        current_time = int(time.time() * 1000)
        if self.is_reversed and current_time >= self.reverse_movement_end_time:
            self.is_reversed = False # 역방향 이동 종료

        # 무적 상태 해제 확인
        if self.is_invincible and current_time >= self.invincible_end_time:
            self.is_invincible = False
            self.color = "red" if self.control_type == "wasd" else "blue" # 원래 색상으로 복원

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

        # 역방향 이동 상태일 경우 dx, dy 반전
        if self.is_reversed:
            dx *= -1
            dy *= -1

        if dx != 0 or dy != 0:
            self.last_dx = dx
            self.last_dy = dy

        new_x = self.x + dx
        new_y = self.y + dy

        # 충돌 검사 (무적 상태일 때는 장애물 무시)
        if not self.is_invincible:
            for obs in obstacles:
                if obs.check_collision_rect(new_x, new_y, self.size, self.size):
                    return  # 이동하지 않음

        if 0 <= new_x <= self.canvas.winfo_width() - self.size: # canvas_width 대신 self.canvas.winfo_width() 사용
            self.x = new_x
        if ui_height <= new_y <= self.canvas.winfo_height() - self.size: # canvas_height 대신 self.canvas.winfo_height() 사용
            self.y = new_y

    def draw(self, canvas):
        if not self.is_active:
            return
        if self.id is None or not canvas.find_withtag(self.id):
            self.id = canvas.create_rectangle(
                self.x, self.y,
                self.x + self.size, self.y + self.size,
                fill=self.color
            )
        else:
            canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)
            canvas.itemconfig(self.id, fill=self.color if not self.is_invincible else "yellow") # 무적일 때 색상 변경

    def handle_skill_selection(self, key):
        if not self.skill_manager:
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
            if key == "comma": # <
                self.selected_skill = 0
            elif key == "period": # >
                self.selected_skill = 1
            elif key == "slash": # ?
                self.selected_skill = 2

    def use_selected_skill(self, target_player=None):
        if self.skill_manager:
            skill = self.skill_manager.get_selected_skill(self.selected_skill)
            if skill and skill.use(self):
                if self.selected_skill == 0: # 총알 발사 스킬
                    # 총알 생성 및 발사 (가장 최근 이동 방향으로)
                    bullet_dx = 0
                    bullet_dy = 0
                    if self.last_dx == 0 and self.last_dy == 0:
                        # 기본 발사 방향 (예: 오른쪽)
                        bullet_dx = 1
                    else:
                        # 마지막 이동 방향으로 총알 발사
                        norm = (self.last_dx**2 + self.last_dy**2)**0.5
                        if norm > 0:
                            bullet_dx = self.last_dx / norm
                            bullet_dy = self.last_dy / norm

                    # 총알 속도 조절
                    bullet_speed = 15
                    new_bullet = Bullet(self.canvas, self.x + self.size // 2, self.y + self.size // 2,
                                        bullet_dx * bullet_speed, bullet_dy * bullet_speed,
                                        self.color, self)
                    self.bullets.append(new_bullet)
                elif self.selected_skill == 1: # 속도 증가 스킬
                    self.speed_boost(factor=2, duration=3000) # 3초간 2배속
                elif self.selected_skill == 2: # 무적 스킬
                    self.activate_invincibility(duration=2000) # 2초간 무적
                return True
        return False

    def is_in_goal_area(self, goal_area):
        px, py = self.x, self.y
        pw, ph = self.size, self.size
        gx, gy, gw, gh = goal_area

        return not (
                px + pw < gx or px > gx + gw or
                py + ph < gy or py > gy + gh
        )

    def update_speed(self):
        current_time = int(time.time() * 1000)
        # 슬로우 효과 해제
        if self.speed < self.default_speed and current_time >= self.slow_end_time:
            self.speed = self.default_speed
        # 속도 부스트 효과 해제
        if self.speed > self.default_speed and current_time >= self.speed_boost_end_time:
            self.speed = self.default_speed


    def slow(self, factor, duration=3000):
        current_time = int(time.time() * 1000)
        self.speed = self.default_speed * factor
        self.slow_end_time = max(self.slow_end_time, current_time + duration)

    def speed_boost(self, factor, duration=3000):
        current_time = int(time.time() * 1000)
        self.speed = self.default_speed * factor
        self.speed_boost_end_time = max(self.speed_boost_end_time, current_time + duration)


    def push_back(self, canvas, distance=30, steps=10, delay=20):
        # Calculate the push back direction based on the last movement.
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
            if count >= steps:
                return
            self.x += dx
            self.y += dy
            canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)
            canvas.after(delay, lambda: step(count + 1))

        step()  # 애니메이션 시작

    def start_reverse_movement(self, duration=3000): # 3000ms = 3초
        self.is_reversed = True
        self.reverse_movement_end_time = int(time.time() * 1000) + duration

    def activate_invincibility(self, duration=2000):
        self.is_invincible = True
        self.invincible_end_time = int(time.time() * 1000) + duration
        self.canvas.itemconfig(self.id, fill="yellow") # 무적 상태 시 색상 변경

    def get_damage(self, dmg):
        if not self.is_invincible: # 무적 상태가 아닐 때만 데미지 적용
            self.hp -= dmg
            self.flash_black()
            if self.hp <= 0:
                self.die()

    def flash_black(self, flashes=3, interval=200):
        def toggle(count=0):
            if count >= flashes * 2:
                self.canvas.itemconfig(self.id, fill=self.color if not self.is_invincible else "yellow")
                return
            color = 'black' if count % 2 == 0 else (self.color if not self.is_invincible else "yellow")
            self.canvas.itemconfig(self.id, fill=color)
            self.canvas.after(interval, lambda: toggle(count + 1))

        toggle()

    def is_dead(self):
        return self.hp <= 0

    def die(self):
        self.hp = 0
        self.is_active = False
        self.x = -1000
        self.y = -1000
        if self.id:
            self.canvas.delete(self.id)
            self.id = None

# 총알 클래스 추가 (player.py 파일 내부에 정의)
class Bullet:
    def __init__(self, canvas, x, y, dx, dy, color, owner_player):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.size = TILE_SIZE // 4
        self.id = self.canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size, fill=color)
        self.active = True
        self.owner = owner_player # 총알을 발사한 플레이어

    def move(self, canvas_width, canvas_height, ui_height, target_players):
        if not self.active:
            return

        self.x += self.dx
        self.y += self.dy

        # 화면 밖으로 나가면 비활성화
        if not (0 <= self.x < canvas_width and ui_height <= self.y < canvas_height):
            self.deactivate()
            return

        self.canvas.coords(self.id, self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size)

        # 다른 플레이어와의 충돌 검사
        for player in target_players:
            if player is not self.owner and player.is_active and self.check_collision(player):
                player.get_damage(1) # 데미지 적용
                self.deactivate()
                return

    def check_collision(self, player):
        px, py = player.x, player.y
        pw, ph = player.size, player.size
        
        # 총알과 플레이어 충돌 검사
        return (
            self.x - self.size < px + pw and
            px < self.x + self.size and
            self.y - self.size < py + ph and
            py < self.y + self.size
        )

    def deactivate(self):
        if self.id:
            self.canvas.delete(self.id)
            self.id = None
        self.active = False
