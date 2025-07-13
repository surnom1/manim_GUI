from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

class SlideList(QWidget):
    def __init__(self, parent=None):
        super(SlideList, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.slide_list_widget = QListWidget(self)
        self.layout.addWidget(self.slide_list_widget)
        self.setLayout(self.layout)

    def add_slide(self, slide_name):
        item = QListWidgetItem(slide_name)
        self.slide_list_widget.addItem(item)

    def clear_slides(self):
        self.slide_list_widget.clear()

    def get_selected_slide(self):
        selected_items = self.slide_list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def connect_slide_selection(self, callback):
        self.slide_list_widget.itemClicked.connect(callback)