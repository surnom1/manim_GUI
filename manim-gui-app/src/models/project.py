class Project:
    def __init__(self):
        self.slides = []
        self.current_slide_index = 0

    def add_slide(self, slide):
        self.slides.append(slide)

    def remove_slide(self, index):
        if 0 <= index < len(self.slides):
            del self.slides[index]

    def get_current_slide(self):
        if self.slides:
            return self.slides[self.current_slide_index]
        return None

    def set_current_slide_index(self, index):
        if 0 <= index < len(self.slides):
            self.current_slide_index = index

    def get_slide_count(self):
        return len(self.slides)

    def clear_slides(self):
        self.slides.clear()
        self.current_slide_index = 0

    def get_slide(self, index):
        if 0 <= index < len(self.slides):
            return self.slides[index]
        return None