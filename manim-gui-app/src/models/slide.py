class Slide:
    def __init__(self, title, content, page_number):
        self.title = title
        self.content = content
        self.page_number = page_number

    def __repr__(self):
        return f"Slide(title={self.title}, page_number={self.page_number})"

    def to_manim_code(self):
        # This method will generate the Manim code for the slide
        return f"Slide(title='{self.title}', content='{self.content}', page_number={self.page_number})"