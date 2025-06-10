from constants import POTION_SIZE, POTION_HEAL_AMOUNT
from icons import POTION_SYMBOL

class Potion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = POTION_SIZE
        self.collected = False
        self.id = None

    def draw(self, canvas):
        if self.collected:
            if self.id:
                canvas.delete(self.id)
            return
        self.id = canvas.create_text(
            self.x + self.size//2, self.y + self.size//2,
            text=POTION_SYMBOL, font=("Arial", self.size), fill="green"
        )

    def check(self, player):
        if self.collected:
            return False
        dx = (player.x + player.size // 2) - (self.x + self.size // 2)
        dy = (player.y + player.size // 2) - (self.y + self.size // 2)
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < (player.size + self.size) // 2:
            self.collected = True
            player.add_potion()  # player.py에 add_potion 메서드 구현
            return True
        return False