# ui.py
import time
from constants import UI_HEIGHT  # UI_HEIGHT 상수 임포트


def draw_ui(canvas, canvas_width, UI_HEIGHT,
    p1_keys, p2_keys,
    p1_hp, p2_hp, p3_hp,
    time_left,
    p1_selected, p2_selected, p3_selected,
    p1_skills, p2_skills, p3_skills):
  # 전체 UI 영역 배경
  canvas.create_rectangle(0, 0, canvas_width, UI_HEIGHT, fill="lightgray",
                          outline="")

  # 각 플레이어 UI 섹션의 시작 X 좌표 및 너비
  section_width = (canvas_width - 20) // 3  # 전체 너비에서 여백을 제외하고 3등분

  p1_section_x = 10
  p2_section_x = p1_section_x + section_width + 10  # P1 섹션 후 10픽셀 간격
  p3_section_x = p2_section_x + section_width + 10  # P2 섹션 후 10픽셀 간격

  # P1 상태 및 스킬 그룹
  canvas.create_rectangle(p1_section_x, 5, p1_section_x + section_width,
                          UI_HEIGHT - 5, fill="white", outline="gray")
  canvas.create_text(p1_section_x + section_width / 2, 20,
                     text=f"P1 ♥:{p1_hp} 🔑:{p1_keys}", font=("Arial", 12),
                     anchor="center")
  # 스킬 바를 중앙에 오도록 x 좌표 조정
  skill_bar_start_x_p1 = p1_section_x + (section_width - (
        60 * len(p1_skills.skills) + 10 * (len(p1_skills.skills) - 1))) / 2
  draw_skill_bar(canvas, skill_bar_start_x_p1, 40, p1_selected,
                 p1_skills.skills)
  canvas.create_text(p1_section_x + section_width / 2, UI_HEIGHT - 15,
                     text="C V B", font=("Arial", 10), fill="darkgray",
                     anchor="center")

  # P2 상태 및 스킬 그룹
  canvas.create_rectangle(p2_section_x, 5, p2_section_x + section_width,
                          UI_HEIGHT - 5, fill="white", outline="gray")
  canvas.create_text(p2_section_x + section_width / 2, 20,
                     text=f"P2 ♥:{p2_hp} 🔑:{p2_keys}", font=("Arial", 12),
                     anchor="center")
  # 스킬 바를 중앙에 오도록 x 좌표 조정
  skill_bar_start_x_p2 = p2_section_x + (section_width - (
        60 * len(p2_skills.skills) + 10 * (len(p2_skills.skills) - 1))) / 2
  draw_skill_bar(canvas, skill_bar_start_x_p2, 40, p2_selected,
                 p2_skills.skills)
  canvas.create_text(p2_section_x + section_width / 2, UI_HEIGHT - 15,
                     text="< > ?", font=("Arial", 10), fill="darkgray",
                     anchor="center")

  # P3 상태 및 스킬 그룹
  canvas.create_rectangle(p3_section_x, 5, p3_section_x + section_width,
                          UI_HEIGHT - 5, fill="white", outline="gray")
  canvas.create_text(p3_section_x + section_width / 2, 20, text=f"P3 ♥:{p3_hp}",
                     font=("Arial", 12), anchor="center")
  # P3 스킬이 더 많으므로 너비 계산을 정확히 해야함
  # 가정: P3는 7개의 스킬을 가지고 있음.
  # 7 * 60 (바 너비) + 6 * 10 (스페이싱) = 420 + 60 = 480
  total_p3_skill_bar_width = 60 * len(p3_skills.skills) + 10 * (
        len(p3_skills.skills) - 1)
  # 섹션 너비를 초과할 경우를 대비하여 최소 너비 확보
  if total_p3_skill_bar_width > section_width:
    # P3 스킬 바가 섹션 너비를 초과할 경우, 왼쪽으로 정렬하거나 스크롤 기능을 추가해야 함.
    # 여기서는 단순히 섹션 너비를 초과하더라도 그릴 수 있도록 함.
    # 실제 게임에서는 UI 디자인에 따라 다르게 처리될 수 있습니다.
    skill_bar_start_x_p3 = p3_section_x + (
          section_width - total_p3_skill_bar_width) / 2  # 가운데 정렬
    if skill_bar_start_x_p3 < p3_section_x + 5:  # 섹션 왼쪽 경계를 넘지 않도록
      skill_bar_start_x_p3 = p3_section_x + 5
  else:
    skill_bar_start_x_p3 = p3_section_x + (
          section_width - total_p3_skill_bar_width) / 2

  draw_skill_bar(canvas, skill_bar_start_x_p3, 40, p3_selected,
                 p3_skills.skills)
  canvas.create_text(p3_section_x + section_width / 2, UI_HEIGHT - 15,
                     text="Q E (click)", font=("Arial", 10), fill="darkgray",
                     anchor="center")

  # 남은 시간 (가장 오른쪽)
  canvas.create_text(canvas_width - 10, 20, text=f"⏱ {int(time_left)}초",
                     font=("Arial", 14), anchor="ne")


def draw_skill_bar(canvas, x, y, selected_index, skills):
  bar_width = 60
  bar_height = 8
  spacing = 10
  text_offset_y = 15

  for i, skill in enumerate(skills):
    cooldown_ratio = skill.cooldown_remaining / skill.cooldown_time if skill.cooldown_time > 0 else 0
    cooldown_ratio = min(max(cooldown_ratio, 0), 1)

    bar_x = x + i * (bar_width + spacing)
    bar_y = y

    # 스킬 바 배경
    canvas.create_rectangle(
        bar_x, bar_y,
        bar_x + bar_width, bar_y + bar_height,
        fill="gray", outline="black"
    )

    # 쿨다운 바
    if cooldown_ratio > 0:
      fill_width = bar_width * (1 - cooldown_ratio)
      canvas.create_rectangle(
          bar_x, bar_y,
          bar_x + fill_width, bar_y + bar_height,
          fill="lightblue", outline=""
      )
      # 쿨타임 텍스트
      remaining_time = int(skill.cooldown_remaining / 1000) + 1
      canvas.create_text(
          bar_x + bar_width / 2, bar_y + bar_height / 2,
          text=f"{remaining_time}s", font=("Arial", 8), fill="black"
      )

    # 선택된 스킬 표시
    if i == selected_index:
      canvas.create_rectangle(
          bar_x, bar_y,
          bar_x + bar_width, bar_y + bar_height,
          outline="yellow", width=2
      )

    # 스킬 이름 표시
    canvas.create_text(
        bar_x + bar_width / 2, bar_y + bar_height + text_offset_y,
        text=skill.name, font=("Arial", 10), fill="black"
    )
