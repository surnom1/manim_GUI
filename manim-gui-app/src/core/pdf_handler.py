class PdfHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.document = None

    def load_pdf(self):
        """Load the PDF document from the specified file path."""
        from PyPDF2 import PdfReader
        self.document = PdfReader(self.file_path)

    def get_page_count(self):
        """Return the number of pages in the PDF document."""
        if self.document is None:
            raise ValueError("PDF document not loaded.")
        return len(self.document.pages)

    def get_page(self, page_number):
        """Return the specified page from the PDF document."""
        if self.document is None:
            raise ValueError("PDF document not loaded.")
        if page_number < 0 or page_number >= self.get_page_count():
            raise IndexError("Page number out of range.")
        return self.document.pages[page_number]

    def extract_text(self, page_number):
        """Extract text from the specified page."""
        page = self.get_page(page_number)
        return page.extract_text()

    def save_page_as_image(self, page_number, output_path):
        """Save the specified page as an image."""
        import fitz  # PyMuPDF
        pdf_document = fitz.open(self.file_path)
        page = pdf_document.load_page(page_number)
        pix = page.get_pixmap()
        pix.save(output_path)