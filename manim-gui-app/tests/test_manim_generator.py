import unittest
from src.core.manim_generator import ManimGenerator

class TestManimGenerator(unittest.TestCase):

    def setUp(self):
        self.manim_generator = ManimGenerator()

    def test_generate_code(self):
        slide_content = "This is a test slide."
        animations = ["fade_in", "zoom"]
        expected_code = (
            "from manim import *\n\n"
            "class TestSlide(Scene):\n"
            "    def construct(self):\n"
            "        text = Text('This is a test slide.')\n"
            "        self.play(FadeIn(text))\n"
            "        self.play(ZoomIn(text))\n"
            "        self.wait(2)\n"
        )
        generated_code = self.manim_generator.generate_code(slide_content, animations)
        self.assertEqual(generated_code.strip(), expected_code.strip())

    def test_invalid_animations(self):
        slide_content = "Another test slide."
        animations = ["invalid_animation"]
        with self.assertRaises(ValueError):
            self.manim_generator.generate_code(slide_content, animations)

    def test_empty_slide(self):
        slide_content = ""
        animations = []
        expected_code = (
            "from manim import *\n\n"
            "class TestSlide(Scene):\n"
            "    def construct(self):\n"
            "        self.wait(2)\n"
        )
        generated_code = self.manim_generator.generate_code(slide_content, animations)
        self.assertEqual(generated_code.strip(), expected_code.strip())

if __name__ == '__main__':
    unittest.main()