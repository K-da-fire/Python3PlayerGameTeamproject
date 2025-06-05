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

root = tk.Tk()

# === MAIN GAME FUNCTION ===
def main():
    root.title("3인 경쟁 게임")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    canvas_width = screen_width
    canvas_height = screen_height
    root.geometry(f"{canvas_width}x{canvas_height}")

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()

    canvas.after(100, canvas.focus_set)

    # === 초기화 ===
    p1 = Player(100, canvas_height - TILE_SIZE * 2, "red", "wasd", canvas)
    p2 = Player(300, canvas_height - TILE_SIZE * 2, "blue", "arrow", canvas)

    p3_skills_name = ["정사각형 벽", "가로벽", "세로벽", "슬로우장판", "튕겨내기", "데미지"]

    p1_skills = SkillManager()
    p1_skills.add_skill("벽", 3000, 3)
    p2_skills = SkillManager()
    p2_skills.add_skill("벽", 3000, 3)
    p3_skills = SkillManager()
    for i in range(6):  # P3는 6개 슬롯
        p3_skills.add_skill(p3_skills_name[i], 500, 10)

    keys_p1 = []
    keys_p2 = []
    existing_key_positions = []
    goal_area = (canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE, TILE_SIZE, TILE_SIZE)
    player_positions = [
        (p1.x, p1.y),
        (p2.x, p2.y)
    ]
    all_positions_to_avoid = existing_key_positions + player_positions
    obstacles = draw_box(canvas, canvas_width, canvas_height,
                         TILE_SIZE, UI_HEIGHT, all_positions_to_avoid, goal_area)
    p3 = Player3(canvas, p3_skills, obstacles)

    for _ in range(3):  # p1 열쇠
        x, y = generate_non_overlapping_key_position(existing_key_positions, canvas_width, canvas_height,
                                                    TILE_SIZE, UI_HEIGHT, goal_area)
        existing_key_positions.append((x, y))
        keys_p1.append(Key(x, y, "p1"))

    for _ in range(3):  # p2 열쇠
        x, y = generate_non_overlapping_key_position(existing_key_positions, canvas_width, canvas_height,
                                                    TILE_SIZE, UI_HEIGHT, goal_area)
        existing_key_positions.append((x, y))
        keys_p2.append(Key(x, y, "p2"))

    # === 이벤트 바인딩 ===
    def on_key(event):
        key = event.keysym.lower()
        p1.pressed.add(event.keysym)
        p2.pressed.add(event.keysym)
        p1.handle_skill_selection(key)
        p2.handle_skill_selection(key)

    def on_key_up(event):
        p1.pressed.discard(event.keysym)
        p2.pressed.discard(event.keysym)

    def on_mouse_click(event):
        obstacle = p3.spawn_obstacle(event.x, event.y)
        if obstacle:
            obstacles.append(obstacle)

    def on_mousewheel(event):
        p3.handle_mousewheel(event.delta)

    canvas.bind_all("<KeyPress>", on_key)
    canvas.bind_all("<KeyRelease>", on_key_up)
    canvas.bind("<Button-1>", on_mouse_click)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # === 게임 루프 ===
    game_over = False
    start_time = time.time()

    def loop():
        nonlocal game_over
        if game_over:
            return

        if p1.is_dead():
            p1.die()
        if p2.is_dead():
            p2.die()

        canvas.delete("all")

        #1. 시간 계산
        now = time.time()
        elapsed = now - start_time
        time_left = max(0, GAME_DURATION - elapsed)

        #2. 맵, UI
        draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT)
        draw_ui(canvas, canvas_width, UI_HEIGHT, p1.keys, p2.keys,
                p1.hp, p2.hp, p3.hp, time_left,
                p1.selected_skill, p2.selected_skill, p3.selected_skill_index,
                p1_skills, p2_skills, p3_skills)
        for obstacle in obstacles:
            obstacle.draw()

        #3. 플레이어 이동 및 그리기
        p1.move(canvas_width, canvas_height, UI_HEIGHT, obstacles)
        p2.move(canvas_width, canvas_height, UI_HEIGHT, obstacles)
        p1.draw(canvas)
        p2.draw(canvas)

        #4. 열쇠 아이템 처리
        for k in keys_p1:
            k.draw(canvas)
            k.check(p1, "p1")
        for k in keys_p2:
            k.draw(canvas)
            k.check(p2, "p2")

        #5. 장애물 처리
        p3.update_obstacles()
        for obs in p3.obstacles[:]:
            if obs.is_expired():
                p3.obstacles.remove(obs)
                obs.remove()
            else:
                canvas.tag_raise(obs.id)
                for player in [p1, p2]:
                    if obs.check_collision(player):
                        obs.apply_effect(player)

        #6. 스킬 쿨타임 업데이트
        p1_skills.update(GAME_TICK_MS)
        p2_skills.update(GAME_TICK_MS)
        p3_skills.update(GAME_TICK_MS)

        # 승리 처리 함수
        def show_winner(winner_text):
            color = winner_text.lower().split()[0]
            canvas.create_text(canvas_width // 2, canvas_height // 2 - 40,
                               text=winner_text, font=("Arial", 48), fill=color)

            def restart():
                retry_button.destroy()
                # canvas.delete("all")
                if canvas:
                    canvas.destroy()
                main()  # 전체 게임 재시작

            retry_button = tk.Button(root, text="다시하기", font=("Arial", 20),
                                     command=restart)
            retry_button.place(x=canvas_width // 2 - 60, y=canvas_height // 2 + 10)

        # 8. 승리 조건 확인
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
            draw_ui(canvas, canvas_width, UI_HEIGHT, p1.keys, p2.keys,
                    p1.hp, p2.hp, p3.hp, time_left,
                    p1.selected_skill, p2.selected_skill, p3.selected_skill_index,
                    p1_skills, p2_skills, p3_skills)
            show_winner("Green Wins!")
            return

        #7. 다음 프레임 예약
        canvas.after(GAME_TICK_MS, loop)

    loop()

if __name__ == '__main__':
    main()
    root.mainloop()