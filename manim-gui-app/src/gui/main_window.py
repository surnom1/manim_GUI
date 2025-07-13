from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QListWidget, QLabel, QToolBar, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from src.gui.pdf_viewer import PdfViewer
from src.gui.slide_list import SlideList
from src.gui.slide_editor import SlideEditor
from src.gui.toolbar import Toolbar
from src.core.inkscape_interface import InkscapeInterface
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manim GUI Application")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize InkscapeInterface
        self.inkscape_interface = InkscapeInterface()
        
        # Initialize current PDF path
        self.current_pdf_path = None
        self.slide_data = {}

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.toolbar = Toolbar(self)
        self.addToolBar(self.toolbar)

        # Main horizontal splitter (slide list | content area)
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.main_splitter)

        # --- Correction de l'ordre d'initialisation ---

        # 1. Créer la liste des slides et l'ajouter au splitter
        self.slide_list = SlideList(self)
        self.main_splitter.addWidget(self.slide_list)

        # 2. Maintenant que self.slide_list existe, on peut connecter le signal
        self.slide_list.slide_list_widget.currentItemChanged.connect(self.on_slide_changed)

        # 3. Créer la zone de contenu
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_splitter.addWidget(self.content_widget)

        # 4. Créer le splitter vertical pour l'éditeur et les PDFs
        self.vertical_splitter = QSplitter(Qt.Vertical)
        self.content_layout.addWidget(self.vertical_splitter)

        # 5. Créer l'éditeur de slide (en passant la référence à MainWindow)
        self.selected_slide = SlideEditor(self)
        self.vertical_splitter.addWidget(self.selected_slide)

        # 6. Créer le conteneur pour les PDFs
        self.pdf_container = QWidget()
        self.pdf_layout = QHBoxLayout(self.pdf_container)
        self.pdf_layout.setContentsMargins(0, 0, 0, 0)
        
        # Two PDF viewers side by side
        self.pdf_viewer_left = PdfViewer()
        self.pdf_viewer_right = PdfViewer()
        
        self.pdf_layout.addWidget(self.pdf_viewer_left)
        self.pdf_layout.addWidget(self.pdf_viewer_right)
        
        self.vertical_splitter.addWidget(self.pdf_container)

        # Set proportional sizes for the main sections
        self.main_splitter.setSizes([200, 1000])  # Slide list narrower than content
        self.vertical_splitter.setSizes([600, 400])  # Editor larger than PDFs
        
        # Add extra actions to the toolbar for Inkscape operations
        self.add_inkscape_actions()
        self.add_slide()

    def on_slide_changed(self, current, previous):
        """Appelé lorsque l'utilisateur sélectionne une autre slide."""
        if previous:
            # Sauvegarder l'état de la slide précédente
            previous_slide_name = previous.text()
            self.slide_data[previous_slide_name] = self.selected_slide.get_slide_content()

        if current:
            # Charger l'état de la nouvelle slide
            current_slide_name = current.text()
            slide_content = self.slide_data.get(current_slide_name, [])
            self.selected_slide.load_slide_content(slide_content)

    def get_current_slide_name(self):
        """Retourne le nom de la slide actuellement sélectionnée."""
        current_item = self.slide_list.currentItem()
        return current_item.text() if current_item else None

    # Le reste du code reste inchangé...
    def open_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            print(f"Opening PDF: {file_path}")
            self.current_pdf_path = file_path
            self.pdf_viewer_left.load_pdf(file_path)  # Updated from pdf_viewer_top
            self.pdf_viewer_right.load_pdf(file_path)  # Updated from pdf_viewer_bottom
 
    def extract_current_page_as_svg(self):
        """Extract the currently visible page as SVG using Inkscape"""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "No PDF Loaded", "Please open a PDF file first.")
            return
            
        # Get the current page number from the top viewer
        page_num = self.pdf_viewer_top.current_page + 1  # +1 because PDF page numbers are 1-based
        
        # Ask user where to save the SVG
        file_dialog = QFileDialog()
        svg_path, _ = file_dialog.getSaveFileName(self, "Save SVG File", f"page_{page_num}.svg", "SVG Files (*.svg)")
        
        if svg_path:
            # Use InkscapeInterface to convert PDF page to SVG
            if self.inkscape_interface.pdf_to_svg(self.current_pdf_path, page_num, svg_path):
                QMessageBox.information(self, "Success", f"Page {page_num} extracted as SVG successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to extract page as SVG.")
    
    def extract_simplified_svg(self):
        """Extract the current page as a simplified SVG (with objects converted to paths)"""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "No PDF Loaded", "Please open a PDF file first.")
            return
            
        # Get the current page number from the top viewer
        page_num = self.pdf_viewer_top.current_page + 1  # +1 because PDF page numbers are 1-based
        
        # Ask user where to save the SVG
        file_dialog = QFileDialog()
        svg_path, _ = file_dialog.getSaveFileName(self, "Save Simplified SVG File", 
                                              f"simplified_page_{page_num}.svg", "SVG Files (*.svg)")
        
        if svg_path:
            # Create a temporary filename for the intermediate SVG
            temp_svg = os.path.join(os.path.dirname(svg_path), f"temp_{os.path.basename(svg_path)}")
            
            # Use InkscapeInterface to convert PDF page to simplified SVG
            if self.inkscape_interface.pdf_page_to_simplified_svg(
                    self.current_pdf_path, page_num, temp_svg, svg_path):
                QMessageBox.information(self, "Success", 
                                       f"Page {page_num} extracted as simplified SVG successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to extract simplified SVG.")
    
    def insert_svg_into_slide(self):
        """Insert an SVG file into the current slide"""
        # Ask user to select an SVG file
        file_dialog = QFileDialog()
        svg_path, _ = file_dialog.getOpenFileName(self, "Select SVG File", "", "SVG Files (*.svg)")
        
        if svg_path and hasattr(self.selected_slide, 'insert_svg'):
            self.selected_slide.insert_svg(svg_path)
    
    def add_slide(self):
        print("Adding new slide")
        if hasattr(self.slide_list, 'add_slide'):
            self.slide_list.add_slide(f"Slide {self.slide_list.slide_list_widget.count() + 1}")
    
    def generate_manim(self):
        print("Generating Manim code")
        # Logique pour générer le code Manim
    
    def export_slide(self):
        print("Exporting slide")
        # Logique pour exporter une diapositive
    
    def add_animation(self, animation_type):
        print(f"Adding {animation_type} animation to slide")
        # Logique pour ajouter une animation au slide sélectionné
    def add_inkscape_actions(self):
        """Add Inkscape-related actions to the toolbar"""
        # Extract Page as SVG action
        self.extract_svg_action = QAction("Extract Page as SVG", self)
        self.extract_svg_action.triggered.connect(self.extract_current_page_as_svg)
        self.toolbar.addAction(self.extract_svg_action)
        
        # Extract Simplified SVG action
        self.extract_simplified_action = QAction("Simplify SVG", self)
        self.extract_simplified_action.triggered.connect(self.extract_simplified_svg)
        self.toolbar.addAction(self.extract_simplified_action)
        
        # Insert SVG into Slide action
        self.insert_svg_action = QAction("Insert SVG into Slide", self)
        self.insert_svg_action.triggered.connect(self.insert_svg_into_slide)
        self.toolbar.addAction(self.insert_svg_action)