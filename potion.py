import os
from PIL import Image, ImageTk
from constants import POTION_SIZE, POTION_HEAL_AMOUNT
from icons import POTION_SYMBOL

class Potion:
    image_cache = {}  # ✅ 이미지 캐시: owner별 PhotoImage 저장

    def __init__(self, x, y, owner):
      self.x = x
      self.y = y
      self.size = POTION_SIZE
      self.collected = False
      self.id = None

      # 캐시된 이미지가 없다면 로드 후 저장
      if owner not in Potion.image_cache:
          asset_folder = os.path.join(os.path.dirname(__file__), "asset")
          filename = "redPotion.png" if owner == "p1" else "bluePotion.png"
          image_path = os.path.join(asset_folder, filename)
          try:
              img = Image.open(image_path).resize((self.size, self.size))
              Potion.image_cache[owner] = ImageTk.PhotoImage(img)
          except Exception as e:
              print(f"❌ 이미지 로딩 실패({owner}): {e}")
              Potion.image_cache[owner] = None

      self.tk_image = Potion.image_cache[owner]


    def draw(self, canvas):
        if self.collected:
            if self.id:
                canvas.delete(self.id)
            return

        if self.id is None or not canvas.find_withtag(self.id):
            self.id = canvas.create_image(
                self.x + self.size // 2,
                self.y + self.size // 2,
                image=self.tk_image,
                anchor="center",
                tags="key"
            )
            # ✅ GC 방지용 참조 유지
            if not hasattr(canvas, "image_refs"):
                canvas.image_refs = []
            if self.tk_image not in canvas.image_refs:
                canvas.image_refs.append(self.tk_image)
        else:
            canvas.coords(self.id, self.x + self.size // 2, self.y + self.size // 2)

        # self.id = canvas.create_text(
        #     self.x + self.size//2, self.y + self.size//2,
        #     text=POTION_SYMBOL, font=("Arial", self.size), fill="green"
        # )


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