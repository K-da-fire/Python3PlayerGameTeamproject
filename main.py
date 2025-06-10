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
from skills import BlinkSkill, ShockwaveSkill

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

    # P3의 스킬 이름 목록 업데이트 (기존 유지)
    p3_skills_name = ["정사각형 벽", "가로벽", "세로벽", "슬로우장판", "튕겨내기", "반대움직임", "데미지"]

    p1_skills = SkillManager()
    p1_skills.add_skill("총알", 1000, 999)  # 쿨타임 1초
    p1_skills.add_skill("속도증가", 10000, 999) # 쿨타임 10초
    p1_skills.add_skill("무적", 30000, 999)   # 쿨타임 30초
    p1_skills.skills.append(BlinkSkill("순간이동", 5000, 999))

    p2_skills = SkillManager()
    p2_skills.add_skill("총알", 1000, 999)
    p2_skills.add_skill("속도증가", 10000, 999)
    p2_skills.add_skill("무적", 30000, 999)
    p2_skills.skills.append(BlinkSkill("순간이동", 5000, 999))

    p3_skills = SkillManager()
    p3_skills.add_skill("정사각형 벽", 3000, 999)
    p3_skills.add_skill("가로벽", 3000, 999)
    p3_skills.add_skill("세로벽", 3000, 999)
    p3_skills.add_skill("슬로우장판", 5000, 5)
    p3_skills.add_skill("튕겨내기", 5000, 5)
    p3_skills.add_skill("반대움직임", 7000, 3)
    p3_skills.add_skill("데미지", 10000, 2)

    p3_obstacles = [] # P3가 생성하는 장애물 목록

    p3 = Player3(canvas, p3_skills, p3_obstacles, cooldown=500)

    p1.set_skill_manager(p1_skills)
    p2.set_skill_manager(p2_skills)

    keys = []
    goal_area = (canvas_width - TILE_SIZE * 2, UI_HEIGHT + TILE_SIZE,
                 canvas_width - TILE_SIZE, UI_HEIGHT + TILE_SIZE * 2)

    # 맵 및 키 생성
    all_obstacles = draw_box(canvas, canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, [], goal_area)
    
    # 기존 장애물과 키의 위치를 (x, y) 튜플 리스트로 결합
    existing_positions_for_key_generation = [(o.x, o.y) for o in all_obstacles] + [(k.x, k.y) for k in keys]

    for _ in range(3):  # 각 플레이어별 3개의 키 생성
        key_pos = generate_non_overlapping_key_position(
            existing_positions_for_key_generation,
            canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, goal_area
        )
        keys.append(Key(key_pos[0], key_pos[1], "p1"))
        existing_positions_for_key_generation.append(key_pos) # 새로 생성된 키 위치 추가

        key_pos = generate_non_overlapping_key_position(
            existing_positions_for_key_generation,
            canvas_width, canvas_height, TILE_SIZE, UI_HEIGHT, goal_area
        )
        keys.append(Key(key_pos[0], key_pos[1], "p2"))
        existing_positions_for_key_generation.append(key_pos) # 새로 생성된 키 위치 추가


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

        # P3 스킬 사용 키 (예시)
        elif event.keysym == "q":  # P3 스킬 사용 키 (예시)
            obs = p3.spawn_obstacle(p1.x, p1.y + p1.size // 2)  # P1 위치에 스폰 (수정 필요)
            if obs:
                all_obstacles.append(obs)
        elif event.keysym == "e": # P3 스킬 사용 키 (예시)
            obs = p3.spawn_obstacle(p2.x, p2.y + p2.size // 2) # P2 위치에 스폰 (수정 필요)
            if obs:
                all_obstacles.append(obs)


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

        current_time_ms = int(time.time() * 1000)
        elapsed_ms = current_time_ms - last_update_time
        last_update_time = current_time_ms

        # 1. 플레이어 이동
        p1.move(canvas_width, canvas_height, UI_HEIGHT, all_obstacles)
        p2.move(canvas_width, canvas_height, UI_HEIGHT, all_obstacles)

        # 2. 총알 이동 및 충돌 검사
        for player in [p1, p2]:
            for bullet in player.bullets[:]: # 리스트 복사본으로 반복하여 안전하게 제거
                if bullet.active:
                    bullet.move(canvas_width, canvas_height, UI_HEIGHT, [p for p in [p1, p2] if p is not player])
                else:
                    player.bullets.remove(bullet)


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
                    p1_skills, p2_skills, p3_skills) # HP 상태 업데이트
            show_winner("Draw!")
            return

        root.after(GAME_TICK_MS, game_loop)

    game_loop()
    root.mainloop()

if __name__ == "__main__":
    main()
