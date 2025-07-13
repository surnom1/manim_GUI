from PyQt5.QtWidgets import QWidget, QFrame
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QCursor, QPainterPath
import os
import xml.etree.ElementTree as ET

class InteractiveSvgWidget(QFrame):
    """Widget SVG interactif avec poignées de redimensionnement et rognage"""
    
    HANDLE_SIZE = 10  # Taille des poignées en pixels
    
    # Constantes pour identifier les différentes poignées
    (HANDLE_TOP_LEFT, HANDLE_TOP, HANDLE_TOP_RIGHT, 
     HANDLE_LEFT, HANDLE_RIGHT,
     HANDLE_BOTTOM_LEFT, HANDLE_BOTTOM, HANDLE_BOTTOM_RIGHT) = range(8)
    
    def __init__(self, svg_path=None, parent=None):
        super().__init__(parent)
        
        # --- Optimisation pour la transparence et le scintillement ---
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        
        self.svg_path = svg_path
        
        # --- REFACTOR: Utiliser un QSvgRenderer au lieu d'un QSvgWidget enfant ---
        self.renderer = QSvgRenderer(self)
        if svg_path:
            self.renderer.load(svg_path)

        # Configuration du widget principal (le cadre)
        self.setFrameShape(QFrame.NoFrame) # Pas de cadre visible par défaut
        self.setMouseTracking(True)
        
        # Variables de suivi
        self.active_handle = None
        self.is_active = False # Nouveau: pour savoir si le widget est sélectionné
        self.drag_start_pos = None
        self.original_rect = None
        self.crop_mode = False
        self.crop_selection_rect = None
        
        # Définir la taille initiale du widget pour correspondre au SVG
        if self.renderer.isValid():
            initial_size = self.renderer.defaultSize()
        else:
            initial_size = QSize(200, 150) # Taille par défaut
        self.resize(initial_size)

        # Correction: Initialiser svg_rect ici
        self.svg_rect = self.rect()

        self.handles = {}
        self.update_handles()

    def set_active(self, active):
        """Définit le widget comme actif ou inactif et met à jour son apparence."""
        self.is_active = active
        self.update()

    def set_crop_mode(self, checked):
        """Activer ou désactiver le mode rognage."""
        self.crop_mode = checked
        self.update() # Redessiner pour changer la couleur des poignées


    def update_handles(self):
        """Mettre à jour la position des poignées en fonction de la taille du widget"""
        rect = self.rect() # Utiliser le rectangle du widget lui-même
        handle_size = self.HANDLE_SIZE
        
        # Définir la position de chaque poignée
        self.handles[self.HANDLE_TOP_LEFT] = QRect(0, 0, handle_size, handle_size)
        self.handles[self.HANDLE_TOP] = QRect(rect.width() // 2 - handle_size // 2, 0, handle_size, handle_size)
        self.handles[self.HANDLE_TOP_RIGHT] = QRect(rect.width() - handle_size, 0, handle_size, handle_size)
        self.handles[self.HANDLE_LEFT] = QRect(0, rect.height() // 2 - handle_size // 2, handle_size, handle_size)
        self.handles[self.HANDLE_RIGHT] = QRect(rect.width() - handle_size, rect.height() // 2 - handle_size // 2, handle_size, handle_size)
        self.handles[self.HANDLE_BOTTOM_LEFT] = QRect(0, rect.height() - handle_size, handle_size, handle_size)
        self.handles[self.HANDLE_BOTTOM] = QRect(rect.width() // 2 - handle_size // 2, rect.height() - handle_size, handle_size, handle_size)
        self.handles[self.HANDLE_BOTTOM_RIGHT] = QRect(rect.width() - handle_size, rect.height() - handle_size, handle_size, handle_size)
    
    def load_svg(self, svg_path):
        """Charger un nouveau fichier SVG"""
        self.svg_path = svg_path
        self.renderer.load(svg_path)
        
        # Réinitialiser les dimensions et les poignées
        new_size = self.renderer.defaultSize()
        self.resize(new_size)
        self.update_handles()
        self.update()
    
    def paintEvent(self, event):
        """Dessiner le SVG, les poignées et la zone de rognage"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Dessiner le SVG en premier
        if self.renderer.isValid():
            # Correction: Convertir le QRect en QRectF
            self.renderer.render(painter, QRectF(self.rect()))
        
        # 2. Dessiner le rectangle de rognage par-dessus
        if self.crop_mode and self.is_active and self.crop_selection_rect:
            painter.setPen(QPen(QColor(255, 0, 0, 200), 2, Qt.DashLine))
            painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
            painter.drawRect(self.crop_selection_rect)

        # 3. Dessiner les poignées de redimensionnement par-dessus tout
        if self.is_active and not self.crop_mode:
            painter.setPen(QPen(Qt.red, 1))
            painter.setBrush(QBrush(QColor(255, 0, 0, 128)))
            for handle_id, handle_rect in self.handles.items():
                painter.drawRect(handle_rect)
    
    
    
    def mousePressEvent(self, event):
        """Gérer le clic de souris pour commencer une action."""
        print(f"\n--- mousePressEvent sur {self.svg_path.split('/')[-1]} ---")
        
        # Notifier le parent (SlideEditor) que ce widget a été cliqué
        # Cela va mettre self.is_active à True
        if self.parent() and hasattr(self.parent(), 'editor'):
            self.parent().editor.setActiveWidget(self)
        
        print(f"Widget actif: {self.is_active}, Mode rognage: {self.crop_mode}")

        # --- CORRECTION : La logique d'interaction est déplacée ici ---
        # On vérifie si le clic est le bouton gauche et si le widget est MAINTENANT actif
        if event.button() == Qt.LeftButton and self.is_active:
            # CAS 1: Si on est en mode rognage, on commence à dessiner le rectangle
            if self.crop_mode:
                print("Action: Début du rognage")
                self.crop_selection_rect = QRect(event.pos(), QSize())
                self.update()
                # On stocke l'état pour mouseMoveEvent mais on ne fait rien d'autre
                return

            # CAS 2: On vérifie si on clique sur une poignée pour redimensionner
            for handle_id, handle_rect in self.handles.items():
                if handle_rect.contains(event.pos()):
                    print(f"Action: Début du redimensionnement (poignée {handle_id})")
                    self.active_handle = handle_id
                    self.drag_start_pos = event.pos()
                    self.original_rect = self.geometry()
                    return
            
            # CAS 3: Si on ne clique pas sur une poignée, on prépare le déplacement
            print("Action: Début du déplacement")
            self.active_handle = -1
            self.drag_start_offset = event.pos()
            self.original_rect = self.geometry()
            return # On a traité l'événement

    def setGeometry(self, rect):
        """Surcharge pour redimensionner le widget SVG interne en même temps."""
        super().setGeometry(rect)
        self.update_handles()

    def resizeEvent(self, event):
        """Gérer le redimensionnement pour mettre à jour le SVG et les poignées."""
        super().resizeEvent(event)
        self.update_handles()

    def mouseMoveEvent(self, event):
        """Gérer le déplacement de souris pour mettre à jour en temps réel"""
        if not self.is_active:
            return

        # CAS 1: L'utilisateur dessine un rectangle de rognage
        if self.crop_mode and self.crop_selection_rect is not None:
            # print("Déplacement: Dessin du rectangle de rognage") # Optionnel, peut être très verbeux
            self.crop_selection_rect.setBottomRight(event.pos())
            self.update()
            return

        # CAS 2 & 3: L'utilisateur déplace ou redimensionne le widget
        if self.active_handle is not None:
            if self.active_handle == -1:
                # print("Déplacement: Mouvement du widget") # Optionnel
                parent_coords = self.mapToParent(event.pos())
                self.move(parent_coords - self.drag_start_offset)
                return
            else:
                # print("Déplacement: Redimensionnement du widget") # Optionnel
                dx = event.pos().x() - self.drag_start_pos.x()
                dy = event.pos().y() - self.drag_start_pos.y()
                new_rect = QRect(self.original_rect)

                if self.active_handle in (self.HANDLE_TOP_LEFT, self.HANDLE_LEFT, self.HANDLE_BOTTOM_LEFT): new_rect.setLeft(self.original_rect.left() + dx)
                if self.active_handle in (self.HANDLE_TOP_LEFT, self.HANDLE_TOP, self.HANDLE_TOP_RIGHT): new_rect.setTop(self.original_rect.top() + dy)
                if self.active_handle in (self.HANDLE_TOP_RIGHT, self.HANDLE_RIGHT, self.HANDLE_BOTTOM_RIGHT): new_rect.setRight(self.original_rect.right() + dx)
                if self.active_handle in (self.HANDLE_BOTTOM_LEFT, self.HANDLE_BOTTOM, self.HANDLE_BOTTOM_RIGHT): new_rect.setBottom(self.original_rect.bottom() + dy)
                
                if new_rect.width() > 20 and new_rect.height() > 20:
                    self.setGeometry(new_rect)
                    self.update()

    def mouseReleaseEvent(self, event):
        """Terminer l'action lors du relâchement de la souris"""
        print(f"--- mouseReleaseEvent sur {self.svg_path.split('/')[-1]} ---")
        if not self.is_active or event.button() != Qt.LeftButton:
            print("Release ignoré (inactif ou pas le bouton gauche)")
            return

        # CAS 1: Fin du rognage
        if self.crop_mode and self.crop_selection_rect and self.crop_selection_rect.isValid():
            print("Action: Fin du rognage, application...")
            crop_rect_normalized = self.crop_selection_rect.normalized()
            
            orig_size = self.renderer.defaultSize()
            if self.rect().width() == 0 or self.rect().height() == 0: return # Eviter division par zéro
            scale_x = orig_size.width() / self.rect().width()
            scale_y = orig_size.height() / self.rect().height()
            
            crop_rect_svg = QRect(
                int(crop_rect_normalized.x() * scale_x),
                int(crop_rect_normalized.y() * scale_y),
                int(crop_rect_normalized.width() * scale_x),
                int(crop_rect_normalized.height() * scale_y)
            )
            
            self.crop_svg(crop_rect_svg)
            self.crop_selection_rect = None
            self.update()
            return

        # CAS 2 & 3: Fin du déplacement ou du redimensionnement
        print("Action: Fin du déplacement/redimensionnement, réinitialisation de l'état.")
        self.active_handle = None
        self.drag_start_pos = None
        self.original_rect = None
        self.update()

    def toggle_mode(self):
        """Basculer entre le mode redimensionnement et rognage"""
        self.crop_mode = not self.crop_mode
        self.update()
    
    def get_current_size(self):
        """Obtenir les dimensions actuelles du widget SVG"""
        return self.svg_rect.size()
    
    def crop_svg(self, crop_rect):
        """
        Rogner le SVG en modifiant le viewBox sans changer la taille d'affichage
        
        Args:
            crop_rect (QRect): Rectangle de rognage dans les coordonnées du SVG original
        """
        if not self.svg_path:
            return
            
        try:
            # Sauvegarder les dimensions actuelles d'affichage
            current_display_size = self.size()
            
            # Créer un nouveau nom de fichier pour le SVG rogné
            file_dir = os.path.dirname(self.svg_path)
            file_name = os.path.basename(self.svg_path)
            base_name, ext = os.path.splitext(file_name)
            cropped_path = os.path.join(file_dir, f"{base_name}_cropped{ext}")
            
            # Charger et analyser le SVG
            tree = ET.parse(self.svg_path)
            root = tree.getroot()
            
            # Obtenir le viewBox actuel
            view_box = root.attrib.get('viewBox', '0 0 100 100')
            view_box_parts = list(map(float, view_box.split()))
            
            # Ajuster les coordonnées de rognage en fonction du viewBox existant
            if len(view_box_parts) == 4:
                orig_x, orig_y, orig_width, orig_height = view_box_parts
                
                # Calculer le nouveau viewBox
                new_x = orig_x + crop_rect.x()
                new_y = orig_y + crop_rect.y()
                new_width = crop_rect.width()
                new_height = crop_rect.height()
                
                # Mettre à jour l'attribut viewBox
                new_view_box = f"{new_x} {new_y} {new_width} {new_height}"
                root.attrib['viewBox'] = new_view_box
                
                # IMPORTANT: Ne pas modifier les attributs width et height du SVG
                # Cela préserve la taille d'affichage tout en modifiant la zone visible
                
                # Enregistrer le SVG rogné
                tree.write(cropped_path)
                
                # Recharger le SVG et redimensionner le widget à la nouvelle taille
                self.svg_path = cropped_path
                self.renderer.load(cropped_path)
                
                # Redimensionner le widget pour qu'il corresponde au contenu rogné
                if self.renderer.isValid():
                    new_size = self.renderer.defaultSize()
                    if not new_size.isEmpty():
                        self.resize(new_size)
                
                self.update()
                return cropped_path
                
            else:
                print("Format de viewBox non reconnu.")
                return None
                
        except Exception as e:
            print(f"Erreur lors du rognage du SVG: {e}")
            return None

