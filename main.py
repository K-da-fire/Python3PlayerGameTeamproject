import tkinter as tk
import time
from gamemap import draw_map, draw_box
from player import Player, Bullet # Bullet 클래스 임포트
from key import Key, generate_non_overlapping_key_position
from ui import draw_ui
from constants import *
from player3 import Player3
from obstacle import *
from skillmanager import SkillManager
from skills import BaseSkill, BlinkSkill

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
    p1_skills.add_skill("총알", 1000, 999)  # 쿨타임 1초
    p1_skills.add_skill("속도증가", 10000, 999)  # 쿨타임 10초
    p1_skills.add_skill("무적", 30000, 999)  # 쿨타임 30초

    p2_skills = SkillManager()
    p2_skills.add_skill("총알", 1000, 999)
    p2_skills.add_skill("속도증가", 10000, 999)
    p2_skills.add_skill("무적", 30000, 999)

    p3_skills = SkillManager()
    p3_skills.add_skill("정사각형 벽", 3000, 999)
    p3_skills.add_skill("가로벽", 3000, 999)
    p3_skills.add_skill("세로벽", 3000, 999)
    p3_skills.add_skill("슬로우장판", 5000, 5)
    p3_skills.add_skill("튕겨내기", 5000, 5)
    p3_skills.add_skill("반대움직임", 7000, 3)
    p3_skills.add_skill("데미지", 10000, 2)

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
        x, y = generate_non_overlapping_key_position(existing_key_positions,
                                                     canvas_width,
                                                     canvas_height,
                                                     TILE_SIZE, UI_HEIGHT,
                                                     goal_area)
        existing_key_positions.append((x, y))
        keys_p1.append(Key(x, y, "p1", canvas))  # ✅ canvas 추가

    for _ in range(3):  # p2 열쇠
        x, y = generate_non_overlapping_key_position(existing_key_positions,
                                                     canvas_width,
                                                     canvas_height,
                                                     TILE_SIZE, UI_HEIGHT,
                                                     goal_area)
        existing_key_positions.append((x, y))
        keys_p2.append(Key(x, y, "p2", canvas))  # ✅ canvas 추가

    game_over = False
    start_time = time.time()
    last_update_time = int(time.time() * 1000)

    # === 이벤트 핸들러 ===
    def on_key_press(event):
        if event.keysym in ["w", "a", "s", "d"]:
            p1.pressed.add(event.keysym)
        elif event.keysym in ["Up", "Down", "Left", "Right"]:
            p2.pressed.add(event.keysym)
        # P1 스킬 사용 키 바인딩
        elif event.keysym == "c":
            p1.use_selected_skill()
        elif event.keysym == "v":
            p1.selected_skill = 1
            p1.use_selected_skill()
        elif event.keysym == "b":
            p1.selected_skill = 2
            p1.use_selected_skill()
        elif event.keysym == "n":
            p1.selected_skill = 3
            p1.use_selected_skill()


        # P2 스킬 사용 키 바인딩
        elif event.keysym == "comma": # <
            p2.use_selected_skill()
        elif event.keysym == "period": # >
            p2.selected_skill = 1
            p2.use_selected_skill()
        elif event.keysym == "slash": # ?
            p2.selected_skill = 2
            p2.use_selected_skill()
        elif event.keysym == "semicolon":
            p2.selected_skill = 3
            p2.use_selected_skill()


        # P1 스킬 선택 키 바인딩
        elif event.keysym == "C": # C
            p1.handle_skill_selection("c")
        elif event.keysym == "V": # V
            p1.handle_skill_selection("v")
        elif event.keysym == "B": # B
            p1.handle_skill_selection("b")
        # P2 스킬 선택 키 바인딩
        elif event.keysym == "less": # <
            p2.handle_skill_selection("comma")
        elif event.keysym == "greater": # >
            p2.handle_skill_selection("period")
        elif event.keysym == "question": # ?
            p2.handle_skill_selection("slash")

    def on_key_release(event):
        if event.keysym in ["w", "a", "s", "d"]:
            p1.pressed.discard(event.keysym)
        elif event.keysym in ["Up", "Down", "Left", "Right"]:
            p2.pressed.discard(event.keysym)

    def on_mousewheel(event):
        p3.handle_mousewheel(event.delta)

    def on_mouse_click(event):
        if event.num == 1: # 좌클릭
            obs = p3.spawn_obstacle(event.x, event.y)
            if obs:
                all_obstacles.append(obs)


    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)
    root.bind("<MouseWheel>", on_mousewheel) # 마우스 휠 이벤트 바인딩
    root.bind("<Button-1>", on_mouse_click) # 마우스 클릭 이벤트 바인딩

    # === 게임 루프 ===
    def game_loop():
        nonlocal game_over, last_update_time

        if game_over:
            return

        if p1.is_dead():
            p1.die()
        if p2.is_dead():
            p2.die()

        # 3. P3 장애물 업데이트 (만료된 장애물 제거)
        p3.update_obstacles()
        all_obstacles[:] = [obs for obs in all_obstacles if not obs.is_expired()]

        # 4. 충돌 검사 및 효과 적용
        for player in [p1, p2]:
            if player.is_active:
                for key in keys:
                    key.check(player, "p1" if player is p1 else "p2")
                p3.check_collisions(player) # P3 장애물과 충돌 검사 및 효과 적용

                # 플레이어가 무적 상태가 아닐 때만 장애물과 충돌 처리
                if not player.is_invincible:
                    for obs in all_obstacles:
                        if obs.check_collision(player):
                            obs.apply_effect(player)

        # 5. 스킬 쿨다운 업데이트
        p1_skills.update(elapsed_ms)
        p2_skills.update(elapsed_ms)
        p3_skills.update(elapsed_ms)
        # 총알 그리기 (각 플레이어 총알들을 이동 후 그리기)
        for player in [p1, p2]:
            for bullet in player.bullets:
                if bullet.active:
                    bullet.draw(canvas)

        # 6. UI 그리기
        canvas.delete("all")
        draw_map(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT)
        for obs in all_obstacles:
            obs.draw() # 장애물 그리기 (WallObstacle에 draw 메서드 추가 필요)

        for key in keys:
            key.draw(canvas)

        p1.draw(canvas)
        p2.draw(canvas)

        # 총알 그리기
        for player in [p1,p2]:
            for bullet in player.bullets:
                if bullet.active:
                    bullet.draw(canvas)


        time_left = GAME_DURATION - (time.time() - start_time)
        if time_left <= 0:
            game_over = True
            show_winner("Time Over!")
            return

        draw_ui(canvas, canvas_width, UI_HEIGHT,
                p1.keys, p2.keys,
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
            k.draw()
            k.check(p1, "p1")
        for k in keys_p2:
            k.draw()
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

        def show_winner(winner_text):
            color = winner_text.lower().split()[0]
            canvas.create_text(canvas_width // 2, canvas_height // 2 - 40,
                               text=winner_text, font=("Arial", 48), fill=color)

            def restart():
                retry_button.destroy()
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

        root.after(GAME_TICK_MS, game_loop)

    game_loop()

if __name__ == "__main__":
    main()
    root.mainloop()