from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QHBoxLayout, QFileDialog, QSizePolicy, QFrame, 
                            QSpinBox, QDialog, QMessageBox, QCheckBox)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QPalette, QColor
import os
import subprocess
import xml.etree.ElementTree as ET
from src.gui.svg_crop_dialog import SvgCropDialog
from src.gui.interactive_svg_widget import InteractiveSvgWidget

class SlideAreaFrame(QFrame):
    """
    Un QFrame personnalisé pour la zone de la slide, optimisé pour 
    réduire le scintillement et gérer la désélection.
    """
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor # Référence à SlideEditor
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: white;")

    def mousePressEvent(self, event):
        """Gère le clic sur la zone de la slide."""
        # Vérifier si on clique sur le fond (pas sur un widget enfant)
        child = self.childAt(event.pos())
        if child is None:
            print("[SlideArea] Clic sur le fond. Désélection.")
            self.editor.setActiveWidget(None) # Désélectionner le widget actif
        
        # Important: passer l'événement au parent pour qu'il soit traité normalement
        # Cela permet aux widgets enfants de recevoir leurs propres événements de clic.
        super().mousePressEvent(event)


class SlideEditor(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.svg_widgets = []  # Liste pour stocker les widgets SVG
        self.active_widget = None
        self.init_ui()

    def setActiveWidget(self, widget):
        """Définit un widget comme étant l'actif et désactive les autres."""
        if self.active_widget == widget:
            return # Ne rien faire si c'est déjà l'actif

        # Désactiver l'ancien widget actif
        if self.active_widget:
            self.active_widget.set_active(False)

        # Activer le nouveau widget
        self.active_widget = widget
        if self.active_widget:
            self.active_widget.set_active(True)
            self.active_widget.raise_() # Le mettre au premier plan

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # Utiliser notre QFrame optimisé, en lui passant une référence de l'éditeur
        self.slide_area = SlideAreaFrame(self)
        self.slide_area.setFrameShape(QFrame.StyledPanel)
        self.slide_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.layout.addWidget(self.slide_area, 1)
        
        # Boutons d'action
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_svg_button = QPushButton("Add SVG")
        self.add_svg_button.clicked.connect(self.add_svg)
        
        self.mode_checkbox = QCheckBox("Mode rognage")
        self.mode_checkbox.toggled.connect(self.toggle_crop_mode)
        
        self.buttons_layout.addWidget(self.add_svg_button)
        self.buttons_layout.addWidget(self.mode_checkbox)
        self.buttons_layout.addStretch()
        
        self.layout.addLayout(self.buttons_layout)

    def maintain_aspect_ratio(self, event=None):
        """Maintenir un ratio 16:9 pour le slide_frame tout en s'assurant qu'il est visible en entier"""
        # Calculer l'espace disponible
        available_width = self.width() - 40  # Marge de 20px de chaque côté
        # Correction: retrait de la référence à self.slide_label qui n'existe plus
        available_height = self.height() - self.buttons_layout.sizeHint().height() - 60
        
        # Calculer les dimensions maximales possibles tout en maintenant le ratio 16:9
        if available_width / 16 * 9 <= available_height:
            # Limitée par la largeur
            width = available_width
            height = width * 9 / 16
        else:
            # Limitée par la hauteur
            height = available_height
            width = height * 16 / 9
        
        # Appliquer les dimensions calculées
        self.slide_frame.setFixedWidth(int(width))
        self.slide_frame.setFixedHeight(int(height))

    def add_svg(self):
        """Ajouter un SVG manuellement via boîte de dialogue"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select SVG File", "", "SVG Files (*.svg)")
        if file_path:
            self.insert_svg(file_path)

    def insert_svg(self, svg_path):
        """Insérer un SVG dans l'éditeur"""
        self.add_svg_widget(svg_path)
        print(f"Inserted SVG: {svg_path}")
        
    def add_svg_widget(self, svg_path, geometry=None):
        """Ajouter un widget SVG interactif, potentiellement avec une géométrie prédéfinie."""
        try:
            interactive_svg = InteractiveSvgWidget(svg_path, parent=self.slide_area)
            
            if geometry:
                interactive_svg.setGeometry(geometry)
            else:
                # Centrer le nouveau SVG s'il n'a pas de géométrie
                center_point = self.slide_area.rect().center()
                new_pos = QPoint(center_point.x() - interactive_svg.width() // 2,
                                 center_point.y() - interactive_svg.height() // 2)
                interactive_svg.move(new_pos)
            
            interactive_svg.show()
            self.svg_widgets.append(interactive_svg)
            
        except Exception as e:
            print(f"Erreur lors du chargement du SVG {svg_path}: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le SVG: {e}")

    def toggle_crop_mode(self, checked):
        """Basculer entre le mode redimensionnement et rognage pour tous les widgets SVG"""
        for svg_widget in self.svg_widgets:
            svg_widget.set_crop_mode(checked)
    
    def clear_svg_widgets(self):
        """Supprimer tous les widgets SVG"""
        for widget in self.svg_widgets:
            widget.deleteLater()
        self.svg_widgets.clear()
    
    def remove_svg_widget(self, svg_widget_to_remove):
        """Supprimer un widget SVG spécifique"""
        if svg_widget_to_remove in self.svg_widgets:
            self.svg_widgets.remove(svg_widget_to_remove)
            svg_widget_to_remove.deleteLater()
    def get_slide_content(self):
        """Retourne une liste de dictionnaires décrivant l'état de chaque SVG."""
        content = []
        for widget in self.svg_widgets:
            content.append({
                'path': widget.svg_path,
                'geometry': widget.geometry()
            })
        return content

    def load_slide_content(self, content):
        """Efface la slide actuelle et charge un nouveau contenu."""
        self.clear_svg_widgets()
        
        for svg_data in content:
            self.add_svg_widget(svg_data['path'], svg_data['geometry'])

    def clear_svg_widgets(self):
        """Supprimer tous les widgets SVG de la slide."""
        # Réinitialiser le widget actif avant de supprimer les objets
        self.active_widget = None
        for widget in self.svg_widgets:
            widget.deleteLater()
        self.svg_widgets.clear()
