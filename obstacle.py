import time
from constants import TILE_SIZE

class BaseObstacle:
    def __init__(self, canvas, x, y, size=None, width=None, height=None, duration=5000):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width if width else size
        self.height = height if height else size
        self.duration = duration
        self.created_time = int(time.time() * 1000)
        self.id = self.canvas.create_rectangle(
            x, y, x + self.width, y + self.height,
            fill="gray"
        )

    def is_expired(self):
        current_time = int(time.time() * 1000)
        return current_time - self.created_time >= self.duration

    def remove(self):
        self.canvas.delete(self.id)

    def check_collision(self, player):
        px, py = player.x, player.y
        pw, ph = player.size, player.size
        return (
            self.x < px + pw and
            px < self.x + self.width and
            self.y < py + ph and
            py < self.y + self.height
        )

    def apply_effect(self, player):
        # Override in subclasses
        pass

    def check_collision_rect(self, x, y, width, height):
        return not (
                x + width < self.x or x > self.x + self.width or
                y + height < self.y or y > self.y + self.height
        )


class WallObstacle(BaseObstacle):
    def __init__(self, canvas, x, y, shape="square", color="black", duration=5000):
        # shape: "square", "wide", "tall"
        if shape == "square":
            width, height = 60, 60
        elif shape == "wide":
            width, height = 100, 40
        elif shape == "tall":
            width, height = 40, 100
        else:
            width, height = 60, 60
        self.color = color
        super().__init__(canvas, x, y, width=width, height=height, duration=duration)
        self.canvas.itemconfig(self.id, fill=self.color)

    def draw(self):
        self.id = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.color
        )

    def apply_effect(self, player):
        pass  # 기본 충돌 처리

    def check_collision(self, player):
        # 플레이어의 위치와 장애물의 사각형 충돌 여부 계산
        px, py = player.x, player.y
        pw, ph = player.size, player.size

        return not (
                px + pw < self.x or px > self.x + self.width or
                py + ph < self.y or py > self.y + self.height
        )

class SlowObstacle(WallObstacle):
    def __init__(self, canvas, x, y, shape="square", duration=5000):
        super().__init__(canvas, x, y, shape=shape, color="blue", duration=duration)

    def apply_effect(self, player):
        player.slow(0.3)

    def check_collision_rect(self, x, y, width, height):
        pass


class PushObstacle(WallObstacle):
    def __init__(self, canvas, x, y, shape="square", duration=5000):
        super().__init__(canvas, x, y, shape=shape, color="purple", duration=duration)

    def apply_effect(self, player):
        player.push_back(self.canvas)

    def check_collision_rect(self, x, y, width, height):
        pass


class DamageObstacle(WallObstacle):
    def __init__(self, canvas, x, y, shape="square", duration=5000):
        super().__init__(canvas, x, y, shape=shape, color="red", duration=duration)
        self.damaged_players = set()  # 이미 피해를 입힌 플레이어를 추적

    def apply_effect(self, player):
        if player not in self.damaged_players:
            player.get_damage(1)
            self.damaged_players.add(player)

    def check_collision_rect(self, x, y, width, height):
        pass