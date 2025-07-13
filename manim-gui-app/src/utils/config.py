class Config:
    def __init__(self):
        self.pdf_path = ""
        self.slide_duration = 5  # Default duration for each slide
        self.animations = []  # List to hold selected animations
        self.output_directory = "./output"  # Default output directory for generated files

    def set_pdf_path(self, path):
        self.pdf_path = path

    def set_slide_duration(self, duration):
        self.slide_duration = duration

    def add_animation(self, animation):
        if animation not in self.animations:
            self.animations.append(animation)

    def remove_animation(self, animation):
        if animation in self.animations:
            self.animations.remove(animation)

    def set_output_directory(self, directory):
        self.output_directory = directory

    def get_config(self):
        return {
            "pdf_path": self.pdf_path,
            "slide_duration": self.slide_duration,
            "animations": self.animations,
            "output_directory": self.output_directory,
        }