class Skill:
    def __init__(self, name, cooldown_time, max_count):
        self.name = name
        self.cooldown_time = cooldown_time  # milliseconds
        self.max_count = max_count
        self.remaining_count = max_count
        self.cooldown_remaining = 0

    def use(self):
        if self.is_available():
            self.remaining_count -= 1
            self.cooldown_remaining = self.cooldown_time
            return True
        return False

    def is_available(self):
        return self.remaining_count > 0 and self.cooldown_remaining <= 0

    def update(self, elapsed_ms):
        if self.cooldown_remaining > 0:
            self.cooldown_remaining = max(0, self.cooldown_remaining - elapsed_ms)

class SkillManager:
    def __init__(self):
        self.skills = []

    def add_skill(self, name, cooldown_time, count):
        self.skills.append(Skill(name, cooldown_time, count))

    def get_selected_skill(self, index):
        if 0 <= index < len(self.skills):
            return self.skills[index]
        return None

    def use_skill(self, index):
        skill = self.get_selected_skill(index)
        if skill:
            return skill.use()
        return False

    def update(self, elapsed_ms):
        for skill in self.skills:
            skill.update(elapsed_ms)

    def get_status(self):
        return self.skills