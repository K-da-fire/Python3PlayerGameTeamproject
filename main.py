import tkinter as tk
import time
from gamemap import draw_map, draw_box
from player import Player
from key import Key, generate_non_overlapping_key_position
from ui import draw_ui
from constants import *
from player3 import Player3
from obstacle import *
from skillmanager import SkillManager
from potion import Potion

root = tk.Tk()

def main():
    root.title("3인 경쟁 게임")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    canvas_width, canvas_height = screen_width, screen_height
    root.geometry(f"{canvas_width}x{canvas_height}")

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()
    canvas.after(100, canvas.focus_set)

    # 초기화
    p1 = Player(100, canvas_height - TILE_SIZE * 2, "red", "wasd", canvas)
    p2 = Player(300, canvas_height - TILE_SIZE * 2, "blue", "arrow", canvas)

    p1_skills = SkillManager()
    p1_skills.add_skill("물약", 1000, 999)  # 쿨타임 1초
    p1_skills.add_skill("속도증가", 10000, 999)  # 쿨타임 10초
    p1_skills.add_skill("무적", 30000, 999)  # 쿨타임 30초

    p2_skills = SkillManager()
    p2_skills.add_skill("물약", 1000, 999)
    p2_skills.add_skill("속도증가", 10000, 999)
    p2_skills.add_skill("무적", 30000, 999)

    p3_skills = SkillManager()

    p1.set_skill_manager(p1_skills)
    p2.set_skill_manager(p2_skills)

    for name, cooldown, count in [("정사각형 벽", 3000, 999), ("가로벽", 3000, 999), ("세로벽", 3000, 999),
                                  ("슬로우장판", 5000, 5), ("튕겨내기", 5000, 5), ("반대움직임", 7000, 3), ("데미지", 10000, 2)]:
        p3_skills.add_skill(name, cooldown, count)

    keys_p1, keys_p2 = [], []
    existing_key_positions = []
    goal_area = (canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE, TILE_SIZE, TILE_SIZE)
    player_positions = [(p1.x, p1.y), (p2.x, p2.y)]
    all_positions_to_avoid = existing_key_positions + player_positions

    potions_p1 = []
    potions_p2 = []
    existing_potion_positions = []
    for _ in range(POTION_COUNT_PER_PLAYER):
        x, y = generate_non_overlapping_key_position(existing_potion_positions,
                                                     canvas_width,
                                                     canvas_height,
                                                     TILE_SIZE, UI_HEIGHT,
                                                     goal_area)
        existing_potion_positions.append((x, y))
        potions_p1.append(Potion(x, y, "p1"))
    for _ in range(POTION_COUNT_PER_PLAYER):
        x, y = generate_non_overlapping_key_position(existing_potion_positions,
                                                     canvas_width,
                                                     canvas_height,
                                                     TILE_SIZE, UI_HEIGHT,
                                                     goal_area)
        existing_potion_positions.append((x, y))
        potions_p2.append(Potion(x, y, "p2"))

    all_obstacles = draw_box(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, all_positions_to_avoid, goal_area)
    p3 = Player3(canvas, p3_skills, all_obstacles)

    for _ in range(3):
        x, y = generate_non_overlapping_key_position(existing_key_positions, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, goal_area)
        existing_key_positions.append((x, y))
        keys_p1.append(Key(x, y, "p1", canvas))

    for _ in range(3):
        x, y = generate_non_overlapping_key_position(existing_key_positions, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, goal_area)
        existing_key_positions.append((x, y))
        keys_p2.append(Key(x, y, "p2", canvas))

    # === 이벤트 핸들러 ===
    def on_key_press(event):
        if event.keysym in ["w", "a", "s", "d"]:
            p1.pressed.add(event.keysym)
        elif event.keysym in ["Up", "Down", "Left", "Right"]:
            p2.pressed.add(event.keysym)
        # P1 스킬 사용 키 바인딩
        elif event.keysym == "c":
            p1.selected_skill = 0
            p1.use_selected_skill()
        elif event.keysym == "v":
            p1.selected_skill = 1
            p1.use_selected_skill()
        elif event.keysym == "b":
            p1.selected_skill = 2
            p1.use_selected_skill()
        # P2 스킬 사용 키 바인딩
        elif event.keysym == "comma":  # <
            p2.selected_skill = 0
            p2.use_selected_skill()
        elif event.keysym == "period":  # >
            p2.selected_skill = 1
            p2.use_selected_skill()
        elif event.keysym == "slash":  # ?
            p2.selected_skill = 2
            p2.use_selected_skill()

        # P1 스킬 선택 키 바인딩
        elif event.keysym == "C":  # C
            print("c")
            p1.handle_skill_selection("c")
        elif event.keysym == "V":  # V
            p1.handle_skill_selection("v")
        elif event.keysym == "B":  # B
            p1.handle_skill_selection("b")
        # P2 스킬 선택 키 바인딩
        elif event.keysym == "less":  # <
            p2.handle_skill_selection("comma")
        elif event.keysym == "greater":  # >
            p2.handle_skill_selection("period")
        elif event.keysym == "question":  # ?
            p2.handle_skill_selection("slash")

    def on_key_release(event):
        key = event.keysym
        p1.pressed.discard(key)
        p2.pressed.discard(key)

    def on_mousewheel(event):
        p3.handle_mousewheel(event.delta)

    def on_mouse_click(event):
        obs = p3.spawn_obstacle(event.x, event.y)
        if obs: all_obstacles.append(obs)

    canvas.bind_all("<KeyPress>", on_key_press)
    canvas.bind_all("<KeyRelease>", on_key_release)
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind("<Button-1>", on_mouse_click)

    game_over = False
    potion_message = ""
    potion_message_timer = 0
    start_time = time.time()

    def show_winner(winner_text, color = "Red"):
        canvas.create_text(canvas_width // 2, canvas_height // 2 - 40, text=winner_text, font=("Arial", 48), fill=color)
        def restart():
            retry_button.destroy()
            canvas.destroy()
            main()
        retry_button = tk.Button(root, text="다시하기", font=("Arial", 20), command=restart)
        retry_button.place(x=canvas_width // 2 - 60, y=canvas_height // 2 + 10)

    def game_loop():
        nonlocal game_over,potion_message, potion_message_timer
        if game_over:
            return

        if p1.is_dead(): p1.die()
        if p2.is_dead(): p2.die()

        canvas.delete("all")

        if potion_message_timer > 0:
            potion_message_timer -= 1
            if potion_message_timer == 0:
                potion_message = ""

        now = time.time()
        elapsed = now - start_time
        time_left = max(0, GAME_DURATION - elapsed)

        draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT)
        draw_ui(canvas, canvas_width, UI_HEIGHT, p1.keys, p2.keys,
                p1.hp, p2.hp, p3.hp, time_left,
                p1.selected_skill, p2.selected_skill, p3.selected_skill_index,
                p1_skills, p2_skills, p3_skills, p1.potions, p2.potions,
                potion_message)

        for k in keys_p1:
            k.draw()
            k.check(p1, "p1")
        for k in keys_p2:
            k.draw()
            k.check(p2, "p2")

        for potion in potions_p1:
            potion.draw(canvas)
            if not potion.collected and potion.check(p1):
                potion_message = "포션을 획득했습니다!"
                potion_message_timer = 30
            if potion.collected:
                potions_p1.remove(potion)
        for potion in potions_p2:
            potion.draw(canvas)
            if not potion.collected and potion.check(p2):
                potion_message = "포션을 획득했습니다!"
                potion_message_timer = 30
            if potion.collected:
                potions_p2.remove(potion)

        p3.update_obstacles()
        all_obstacles[:] = [obs for obs in all_obstacles if not obs.is_expired()]
        for obs in all_obstacles:
            obs.draw()
            for player in [p1, p2]:
                if obs.check_collision(player):
                    obs.apply_effect(player)

        p1_skills.update(GAME_TICK_MS)
        p2_skills.update(GAME_TICK_MS)
        p3_skills.update(GAME_TICK_MS)

        if potion_message_timer > 0:
            potion_message_timer -= 1
            if potion_message_timer == 0:
                potion_message = ""

        p1.move(canvas_width, canvas_height, UI_HEIGHT, all_obstacles)
        p2.move(canvas_width, canvas_height, UI_HEIGHT, all_obstacles)
        p1.draw(canvas)
        p2.draw(canvas)

        if p1.keys >= 3 and p1.is_in_goal_area(goal_area):
            game_over = True
            show_winner("Dog Wins!", "Red")
            return
        if p2.keys >= 3 and p2.is_in_goal_area(goal_area):
            game_over = True
            show_winner("Cat Wins!", "Blue")
            return
        if p1.is_dead() and p2.is_dead() or time_left <= 0:
            game_over = True
            show_winner("Human Wins!", "Green")
            return

        root.after(GAME_TICK_MS, game_loop)

    game_loop()

if __name__ == "__main__":
    main()
    root.mainloop()