from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon

class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        
        # Créer les actions pour la barre d'outils
        self.open_pdf_action = QAction("Open PDF", self)
        self.open_pdf_action.triggered.connect(self.parent().open_pdf if parent else lambda: None)
        
        self.add_slide_action = QAction("Add Slide", self)
        self.add_slide_action.triggered.connect(self.parent().add_slide if parent else lambda: None)
        
        self.generate_manim_action = QAction("Generate Manim Code", self)
        self.generate_manim_action.triggered.connect(self.parent().generate_manim if parent else lambda: None)
        
        self.export_slide_action = QAction("Export Slide", self)
        self.export_slide_action.triggered.connect(self.parent().export_slide if parent else lambda: None)
        
        # Ajouter les actions à la barre d'outils
        self.addAction(self.open_pdf_action)
        self.addAction(self.add_slide_action)
        self.addAction(self.generate_manim_action)
        self.addAction(self.export_slide_action)
        
        # Ajouter un séparateur
        self.addSeparator()
        
        # Actions pour les animations
        self.add_fade_in_action = QAction("Fade In", self)
        self.add_fade_in_action.triggered.connect(lambda: self.parent().add_animation("FadeIn") if parent else None)
        
        self.add_transform_action = QAction("Transform", self)
        self.add_transform_action.triggered.connect(lambda: self.parent().add_animation("Transform") if parent else None)
        
        self.add_write_action = QAction("Write", self)
        self.add_write_action.triggered.connect(lambda: self.parent().add_animation("Write") if parent else None)
        
        # Ajouter les animations à la barre d'outils
        self.addAction(self.add_fade_in_action)
        self.addAction(self.add_transform_action)
        self.addAction(self.add_write_action)


    def open_pdf(self):
        # Logique pour ouvrir un PDF
        pass
    
    def add_slide(self):
        # Logique pour ajouter une diapositive
        pass
    
    def generate_manim(self):
        # Logique pour générer le code Manim
        pass
    
    def export_slide(self):
        # Logique pour exporter une diapositive
        pass
    
    def add_animation(self, animation_type):
        # Logique pour ajouter une animation au slide sélectionné
        print(f"Adding {animation_type} animation to slide")
    def init_ui(self):
        layout = QVBoxLayout()

        # Create the toolbar
        self.toolbar = QToolBar("Animation Toolbar", self)

        # Add actions for animations
        self.add_animation_action("Fade In")
        self.add_animation_action("Slide In")
        self.add_animation_action("Zoom In")

        # Add a dropdown for selecting animations
        self.animation_selector = QComboBox(self)
        self.animation_selector.addItems(["Select Animation", "Fade In", "Slide In", "Zoom In"])
        self.toolbar.addWidget(self.animation_selector)

        # Add a label to show selected animation
        self.selected_animation_label = QLabel("Selected Animation: None", self)
        self.toolbar.addWidget(self.selected_animation_label)

        # Connect the animation selector to update the label
        self.animation_selector.currentTextChanged.connect(self.update_selected_animation)

        layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def add_animation_action(self, animation_name):
        action = QAction(animation_name, self)
        action.triggered.connect(lambda: self.select_animation(animation_name))
        self.toolbar.addAction(action)

    def select_animation(self, animation_name):
        self.animation_selector.setCurrentText(animation_name)
        self.update_selected_animation(animation_name)

    def update_selected_animation(self, animation_name):
        self.selected_animation_label.setText(f"Selected Animation: {animation_name}")