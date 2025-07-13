import unittest
from src.core.pdf_handler import PdfHandler

class TestPdfHandler(unittest.TestCase):

    def setUp(self):
        self.pdf_handler = PdfHandler()

    def test_load_pdf(self):
        result = self.pdf_handler.load_pdf("test.pdf")
        self.assertTrue(result)

    def test_get_page_count(self):
        self.pdf_handler.load_pdf("test.pdf")
        page_count = self.pdf_handler.get_page_count()
        self.assertGreater(page_count, 0)

    def test_get_page(self):
        self.pdf_handler.load_pdf("test.pdf")
        page = self.pdf_handler.get_page(0)
        self.assertIsNotNone(page)

    def test_invalid_pdf(self):
        result = self.pdf_handler.load_pdf("invalid.pdf")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()