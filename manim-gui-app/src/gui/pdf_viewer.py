from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import fitz  # PyMuPDF

class PdfViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_document = None
        self.current_page = 0
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Navigation controls
        self.controls_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self.go_to_page)
        
        self.page_count_label = QLabel("/ 0")
        
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        
        self.controls_layout.addWidget(self.prev_button)
        self.controls_layout.addWidget(self.page_spin)
        self.controls_layout.addWidget(self.page_count_label)
        self.controls_layout.addWidget(self.next_button)
        
        # PDF display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.pdf_label)
        
        self.layout.addLayout(self.controls_layout)
        self.layout.addWidget(self.scroll_area)

    def load_pdf(self, pdf_path):
        try:
            self.pdf_document = fitz.open(pdf_path)
            self.page_spin.setMaximum(len(self.pdf_document))
            self.page_count_label.setText(f"/ {len(self.pdf_document)}")
            self.current_page = 0
            self.render_page()
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False

    def render_page(self):
        if not self.pdf_document:
            return
            
        if 0 <= self.current_page < len(self.pdf_document):
            page = self.pdf_document.load_page(self.current_page)
            # Render page to an image
            zoom = 1.5  # Zoom factor
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            
            # Display in the label
            self.pdf_label.setPixmap(pixmap)
            self.page_spin.setValue(self.current_page + 1)

    def next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.render_page()

    def previous_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def go_to_page(self, page_number):
        if self.pdf_document:
            # Convert from 1-based to 0-based indexing
            page_number = page_number - 1
            if 0 <= page_number < len(self.pdf_document):
                self.current_page = page_number
                self.render_page()