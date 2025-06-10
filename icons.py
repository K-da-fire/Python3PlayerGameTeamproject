# Module: icons.py
# Purpose: Define emoji or text symbols used in UI display

HEART_SYMBOL = "♥"  # Unicode heart
KEY_SYMBOL = "🔑"  # Unicode key
GOAL_SYMBOL = "🏁"  # Unicode checkered flag for goal
POTION_SYMBOL = "🧪"

# icons.py
def draw_icons(canvas, x, y, count=3, color="red", icon_type="heart"):
    icons = []
    for i in range(count):
        dx = x + i * 25
        dy = y
        if icon_type == "heart":
            icon = canvas.create_text(dx, dy, text="♥", fill=color, font=("Arial", 16))
        elif icon_type == "key":
            icon = canvas.create_text(dx, dy, text="🔑", fill=color, font=("Arial", 16))
        elif icon_type == "square":
            icon = canvas.create_rectangle(dx, dy, dx+20, dy+20, fill=color, outline="black")
        else:
            icon = canvas.create_text(dx, dy, text="?", fill=color, font=("Arial", 16))
        icons.append(icon)
    return icons