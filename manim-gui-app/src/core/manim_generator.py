class ManimGenerator:
    def __init__(self):
        self.slides = []
        self.animations = []

    def add_slide(self, slide_code):
        self.slides.append(slide_code)

    def set_animations(self, animations):
        self.animations = animations

    def generate_code(self):
        code = ""
        for slide in self.slides:
            code += f"{slide}\n"
            for animation in self.animations:
                code += f"    self.play({animation}())\n"
        return code.strip()