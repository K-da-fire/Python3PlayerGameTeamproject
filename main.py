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
from skills import BaseSkill, BlinkSkill

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
    p2_skills = SkillManager()
    p3_skills = SkillManager()

    for name, cooldown in [("총알", 1000), ("속도증가", 10000), ("무적", 30000)]:
        p1_skills.add_skill(name, cooldown, 999)
        p2_skills.add_skill(name, cooldown, 999)

    for name, cooldown, count in [("정사각형 벽", 3000, 999), ("가로벽", 3000, 999), ("세로벽", 3000, 999),
                                  ("슬로우장판", 5000, 5), ("튕겨내기", 5000, 5), ("반대움직임", 7000, 3), ("데미지", 10000, 2)]:
        p3_skills.add_skill(name, cooldown, count)

    keys_p1, keys_p2 = [], []
    existing_key_positions = []
    goal_area = (canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE, TILE_SIZE, TILE_SIZE)
    player_positions = [(p1.x, p1.y), (p2.x, p2.y)]
    all_positions_to_avoid = existing_key_positions + player_positions

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

    # 이벤트 핸들러
    def on_key_press(event):
        key = event.keysym
        key_l = key.lower()
        p1.pressed.add(key)
        p2.pressed.add(key)
        p1.handle_skill_selection(key_l)
        p2.handle_skill_selection(key_l)
        if key_l in ["c", "v", "b"]: p1.use_selected_skill()
        if key_l in ["comma", "period", "slash"]: p2.use_selected_skill()

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
    start_time = time.time()

    def show_winner(winner_text):
        color = winner_text.lower().split()[0]
        canvas.create_text(canvas_width // 2, canvas_height // 2 - 40, text=winner_text, font=("Arial", 48), fill=color)
        def restart():
            retry_button.destroy()
            canvas.destroy()
            main()
        retry_button = tk.Button(root, text="다시하기", font=("Arial", 20), command=restart)
        retry_button.place(x=canvas_width // 2 - 60, y=canvas_height // 2 + 10)

    def game_loop():
        nonlocal game_over
        if game_over:
            return

        if p1.is_dead(): p1.die()
        if p2.is_dead(): p2.die()

        canvas.delete("all")

        now = time.time()
        elapsed = now - start_time
        time_left = max(0, GAME_DURATION - elapsed)

        draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT)
        draw_ui(canvas, canvas_width, UI_HEIGHT, p1.keys, p2.keys, p3.hp, p1.hp, p2.hp, time_left,
                p1.selected_skill, p2.selected_skill, p3.selected_skill_index, p1_skills, p2_skills, p3_skills)

        for k in keys_p1:
            k.draw()
            k.check(p1, "p1")
        for k in keys_p2:
            k.draw()
            k.check(p2, "p2")

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

        p1.move(canvas_width, canvas_height, UI_HEIGHT, all_obstacles)
        p2.move(canvas_width, canvas_height, UI_HEIGHT, all_obstacles)
        p1.draw(canvas)
        p2.draw(canvas)

        if p1.keys >= 3 and p1.is_in_goal_area(goal_area):
            game_over = True
            show_winner("Red Wins!")
            return
        if p2.keys >= 3 and p2.is_in_goal_area(goal_area):
            game_over = True
            show_winner("Blue Wins!")
            return
        if p1.is_dead() and p2.is_dead():
            game_over = True
            show_winner("Green Wins!")
            return

        root.after(GAME_TICK_MS, game_loop)

    game_loop()

if __name__ == "__main__":
    main()
    root.mainloop()