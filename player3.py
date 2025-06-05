from obstacle import WallObstacle, SlowObstacle, PushObstacle, DamageObstacle
import time

class Player3:
    def __init__(self, canvas, skill_manager, shared_obstacle_list, cooldown=3000):
        self.canvas = canvas
        self.hp = 3
        self.selected_skill_index = 0
        self.skill_manager = skill_manager
        self.obstacles = shared_obstacle_list
        self.cooldown = cooldown  # milliseconds
        self.last_placed_time = 0

    def handle_mousewheel(self, delta):
        if abs(delta) < 10:  # macOS delta 보정
            delta *= 120
        direction = 1 if delta < 0 else -1
        self.selected_skill_index = (self.selected_skill_index + direction) % len(self.skill_manager.skills)

    def can_place_obstacle(self):
        current_time = int(time.time() * 1000)
        return current_time - self.last_placed_time >= self.cooldown

    def spawn_obstacle(self, x, y):
        skill = self.skill_manager.get_selected_skill(self.selected_skill_index)
        if not skill or not skill.is_available():
            return None

        if self.can_place_obstacle():
            success = skill.use()
            if not success:
                return None

            preview_radius = 20
            delay = 1000  # 총 애니메이션 시간(ms)
            steps = 20
            step_delay = delay // steps

            # 1. 테두리 원
            outline_id = self.canvas.create_oval(
                x - preview_radius, y - preview_radius,
                x + preview_radius, y + preview_radius,
                outline="gray", width=2
            )

            # 2. 채워지는 arc (start=90은 위쪽부터)
            fill_id = self.canvas.create_arc(
                x - preview_radius, y - preview_radius,
                x + preview_radius, y + preview_radius,
                start=90, extent=0,
                fill="gray", outline="",
                style="pieslice"  # ← 이거 꼭 필요함!
            )

            # 3. 애니메이션
            def animate_fill(progress=0):
                if progress > steps:
                    self.canvas.delete(outline_id)
                    self.canvas.delete(fill_id)

                    if self.selected_skill_index == 0:
                        obstacle = WallObstacle(self.canvas, x, y, shape="square")
                    elif self.selected_skill_index == 1:
                        obstacle = WallObstacle(self.canvas, x, y, shape="wide")
                    elif self.selected_skill_index == 2:
                        obstacle = WallObstacle(self.canvas, x, y, shape="tall")
                    elif self.selected_skill_index == 3:
                        obstacle = SlowObstacle(self.canvas, x, y, shape="square")
                    elif self.selected_skill_index == 4:
                        obstacle = PushObstacle(self.canvas, x, y, shape="square")
                    elif self.selected_skill_index == 5:
                        obstacle = DamageObstacle(self.canvas, x, y, shape="square")
                    else:
                        return

                    self.obstacles.append(obstacle)
                    self.last_placed_time = int(time.time() * 1000)
                    return

                    # 1. extent 증가
                angle = 360 * (progress / steps)
                self.canvas.itemconfig(fill_id, extent=angle)

                # 2. 점점 진해지는 회색 계산 (0~255)
                intensity = int(255 * (progress / steps))
                gray_hex = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                self.canvas.itemconfig(fill_id, fill=gray_hex)

                # 3. 다음 단계 예약
                self.canvas.after(step_delay, lambda: animate_fill(progress + 1))

            # 🔥 반드시 즉시 시작해야 함!
            self.canvas.after(10, animate_fill)

            return None
        return None

    def update_obstacles(self):
        for obs in self.obstacles[:]:
            if obs.is_expired():
                obs.remove()
                self.obstacles.remove(obs)

    def check_collisions(self, player):
        for obs in self.obstacles:
            if obs.check_collision(player):
                obs.apply_effect(player)