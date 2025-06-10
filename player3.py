from obstacle import WallObstacle, SlowObstacle, PushObstacle, DamageObstacle, ReverseObstacle # ReverseObstacle import
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

            if success:
                if self.selected_skill_index == 0:
                    obstacle = WallObstacle(self.canvas, x, y, shape="square")
                elif self.selected_skill_index == 1:
                    obstacle = WallObstacle(self.canvas, x, y, shape="wide")
                elif self.selected_skill_index == 2:
                    obstacle = WallObstacle(self.canvas, x, y, shape="tall")
                    # 슬롯 3~6: 효과 벽 (각각 다른 클래스로)
                elif self.selected_skill_index == 3:
                    obstacle = SlowObstacle(self.canvas, x, y, shape="square")
                elif self.selected_skill_index == 4:
                    obstacle = PushObstacle(self.canvas, x, y, shape="square")
                elif self.selected_skill_index == 5: # 새로운 스킬 슬롯
                    obstacle = ReverseObstacle(self.canvas, x, y, shape="square")
                elif self.selected_skill_index == 6: # 기존 데미지 스킬은 다음 슬롯으로
                    obstacle = DamageObstacle(self.canvas, x, y, shape="square")
                else:
                    return None
            self.obstacles.append(obstacle)
            self.canvas.after(1000, lambda: self.activate_obstacle(obstacle))

            self.last_placed_time = int(time.time() * 1000)
            return obstacle
        return None

    def activate_obstacle(self, obstacle):
        obstacle.pending = False
        obstacle.color = obstacle.original_color
        self.canvas.itemconfig(obstacle.id, fill=obstacle.color)

    def update_obstacles(self):
        for obs in self.obstacles[:]:
            if obs.is_expired():
                obs.remove()
                self.obstacles.remove(obs)

    def check_collisions(self, player):
        for obs in self.obstacles:
            if obs.check_collision(player):
                obs.apply_effect(player)
