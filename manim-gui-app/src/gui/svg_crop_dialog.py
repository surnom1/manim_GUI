from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QScrollArea, QFrame, QSpinBox)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtSvg import QSvgWidget

class SvgCropArea(QFrame):
    """Widget personnalisé permettant de sélectionner une zone de rognage dans un SVG"""
    def __init__(self, svg_path):
        super().__init__()
        self.svg_path = svg_path
        self.svg_widget = QSvgWidget(svg_path)
        
        # Configuration du layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.svg_widget)
        
        # Variables pour la sélection
        self.start_point = None
        self.end_point = None
        self.is_selecting = False
        
        # Configuration du widget
        self.setMouseTracking(True)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        
        # Obtenir les dimensions du SVG
        self.svg_size = self.svg_widget.sizeHint()
        self.svg_widget.setFixedSize(self.svg_size)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.is_selecting = True
            self.end_point = self.start_point
            self.update()
    
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.end_point = event.pos()
            self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.start_point and self.end_point:
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            
            # Dessiner le rectangle de sélection
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
            
            # Dessiner des lignes diagonales pour indiquer la zone de rognage
            painter.setOpacity(0.3)
            painter.fillRect(rect, QColor(255, 0, 0, 50))
    
    def get_crop_rect(self):
        """Retourne le rectangle de rognage relativement au SVG"""
        if not self.start_point or not self.end_point:
            return None
        
        # Calculer les coordonnées ajustées au widget SVG
        svg_pos = self.svg_widget.pos()
        x1 = min(self.start_point.x(), self.end_point.x()) - svg_pos.x()
        y1 = min(self.start_point.y(), self.end_point.y()) - svg_pos.y()
        x2 = max(self.start_point.x(), self.end_point.x()) - svg_pos.x()
        y2 = max(self.start_point.y(), self.end_point.y()) - svg_pos.y()
        
        # S'assurer que les coordonnées sont dans les limites du SVG
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(self.svg_size.width(), x2)
        y2 = min(self.svg_size.height(), y2)
        
        return QRect(x1, y1, x2 - x1, y2 - y1)


class SvgCropDialog(QDialog):
    """Boîte de dialogue pour rogner un fichier SVG"""
    def __init__(self, svg_path, parent=None):
        super().__init__(parent)
        self.svg_path = svg_path
        self.crop_rect = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Rogner le SVG")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Zone de sélection pour le rognage
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.crop_area = SvgCropArea(self.svg_path)
        self.scroll_area.setWidget(self.crop_area)
        
        layout.addWidget(QLabel("Sélectionnez la zone à conserver:"))
        layout.addWidget(self.scroll_area)
        
        # Dimensions
        dimensions_layout = QHBoxLayout()
        
        dimensions_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        dimensions_layout.addWidget(self.x_spin)
        
        dimensions_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        dimensions_layout.addWidget(self.y_spin)
        
        dimensions_layout.addWidget(QLabel("Largeur:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 9999)
        dimensions_layout.addWidget(self.width_spin)
        
        dimensions_layout.addWidget(QLabel("Hauteur:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 9999)
        dimensions_layout.addWidget(self.height_spin)
        
        layout.addLayout(dimensions_layout)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        self.crop_button = QPushButton("Rogner")
        self.crop_button.clicked.connect(self.accept_crop)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.crop_button)
        
        layout.addLayout(buttons_layout)
        
        # Connecter les événements de sélection
        self.crop_area.mouseReleaseEvent = self.update_spin_values
        
    def update_spin_values(self, event):
        """Met à jour les valeurs des QSpinBox après la sélection"""
        # Appel de la méthode parente
        SvgCropArea.mouseReleaseEvent(self.crop_area, event)
        
        rect = self.crop_area.get_crop_rect()
        if rect:
            self.x_spin.setValue(rect.x())
            self.y_spin.setValue(rect.y())
            self.width_spin.setValue(rect.width())
            self.height_spin.setValue(rect.height())
    
    def accept_crop(self):
        """Accepter le rognage avec les valeurs actuelles"""
        self.crop_rect = QRect(
            self.x_spin.value(),
            self.y_spin.value(),
            self.width_spin.value(),
            self.height_spin.value()
        )
        self.accept()