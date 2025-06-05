# ui.py
def draw_ui(canvas, canvas_width, UI_HEIGHT,
            p1_keys, p2_keys,
            p1_hp, p2_hp, p3_hp,
            time_left,
            p1_selected, p2_selected, p3_selected,
            p1_skills, p2_skills, p3_skills):
    
    # 전체 UI 영역
    canvas.create_rectangle(0, 0, canvas_width, UI_HEIGHT, fill="lightgray", tags="ui")

    # P1 상태 및 스킬
    canvas.create_text(100, 20, text=f"P1 ♥:{p1_hp} 🔑:{p1_keys}", font=("Arial", 12), tags="ui")
    draw_skill_bar(canvas, 40, 40, p1_selected, p1_skills.skills)

    # P2 상태 및 스킬
    canvas.create_text(300, 20, text=f"P2 ♥:{p2_hp} 🔑:{p2_keys}", font=("Arial", 12), tags="ui")
    draw_skill_bar(canvas, 240, 40, p2_selected, p2_skills.skills)

    # P3 상태 및 스킬
    canvas.create_text(500, 20, text=f"P3 ♥:{p3_hp}", font=("Arial", 12), tags="ui")
    draw_skill_bar(canvas, 430, 40, p3_selected, p3_skills.skills)

    # 남은 시간
    canvas.create_text(700, 20, text=f"⏱ {int(time_left)}초", font=("Arial", 12), tags="ui")


def draw_skill_bar(canvas, x, y, selected_index, skills):
    bar_width = 40
    bar_height = 8
    spacing = 10

    for i, skill in enumerate(skills):
        cooldown_ratio = skill.cooldown_remaining / skill.cooldown_time if skill.cooldown_time > 0 else 0
        cooldown_ratio = min(max(cooldown_ratio, 0), 1)

        bar_x = x + i * (bar_width + spacing)
        bar_y = y + 30

        # 스킬 슬롯 배경
        fill_color = "yellow" if i == selected_index else "white"
        canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height, fill=fill_color, tags="ui")

        # 쿨타임 오버레이
        cooldown_width = int(bar_width * cooldown_ratio)
        if cooldown_width > 0:
            canvas.create_rectangle(bar_x, bar_y, bar_x + cooldown_width, bar_y + bar_height, fill="gray", tags="ui")

        # 남은 사용 횟수 표시
        canvas.create_text(bar_x + bar_width // 2, bar_y + bar_height + 10,
                           text=f"{skill.remaining_count}", font=("Arial", 10), tags="ui")