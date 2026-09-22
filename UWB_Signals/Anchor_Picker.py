from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor, QPen, QBrush, QPainter, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
)
from PIL.ImageQt import ImageQt


class ClickableGraphicsView(QGraphicsView):

    clicked = Signal(int, int)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.clicked.emit(int(scene_pos.x()), int(scene_pos.y()))
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene() is not None:
            # Grundriss bleibt beim Skalieren/Resizen immer komplett sichtbar.
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)


class AnchorPicker(QDialog):

    def __init__(self, master, pil_image, num_anchors=4, on_done=None):
        super().__init__(master)
        self.setWindowTitle("Anchor-Positionen setzen")
        self.pil_image = pil_image
        self.num_anchors = num_anchors
        self.on_done = on_done
        self.points = []
        self.marker_items = []

        # Referenz auf QImage/QPixmap halten, sonst wird sie vom GC entfernt
        self.qt_image = ImageQt(pil_image)
        self.pixmap = QPixmap.fromImage(self.qt_image)

        layout = QVBoxLayout(self)

        # Button-Leiste zuerst egal wie groß das Grundriss-Bild ist 
        btn_frame = QHBoxLayout()
        reset_button = QPushButton("Zurücksetzen")
        reset_button.clicked.connect(self.reset)
        btn_frame.addWidget(reset_button)

        self.done_button = QPushButton("Übernehmen")
        self.done_button.setEnabled(False)
        self.done_button.clicked.connect(self.finish)
        btn_frame.addWidget(self.done_button)
        btn_frame.addStretch()
        layout.addLayout(btn_frame)

        self.info_label = QLabel(self._status_text())
        layout.addWidget(self.info_label)

        # Canvas-Ansicht Grundriss wird immer komplett skaliert
        # Klick-Koordinaten werden über mapToScene in echte Bild-Pixel umgerechnet.
        self.scene = QGraphicsScene(0, 0, pil_image.width, pil_image.height)
        self.scene.addPixmap(self.pixmap)

        self.view = ClickableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.clicked.connect(self.on_click)
        layout.addWidget(self.view)

        # Fenstergröße den verfügbaren Bildschirmplatz anpassen

        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        chrome_w, chrome_h = 60, 160  
        if avail is not None:
            max_w = max(400, avail.width() - chrome_w)
            max_h = max(300, avail.height() - chrome_h)
        else:
            max_w, max_h = 1000, 700

        target_w = min(pil_image.width, max_w)
        target_h = min(pil_image.height, max_h)
        self.resize(target_w, target_h + chrome_h)

    def showEvent(self, event):
        super().showEvent(event)
        # Erst nach dem tatsächlichen Anzeigen hat die View ihre finale
        # Größe, daher hier zusätzlich zu resizeEvent noch einmal einpassen.
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def _status_text(self):
        return f"Klicke {self.num_anchors} Anchor-Positionen an ({len(self.points)}/{self.num_anchors})"

    def on_click(self, x, y):
        if len(self.points) >= self.num_anchors:
            return
        self.points.append((x, y))

        r = 4
        marker = QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
        marker.setPen(QPen(QColor("red")))
        marker.setBrush(QBrush(QColor("red")))
        self.scene.addItem(marker)
        self.marker_items.append(marker)

        label = QGraphicsSimpleTextItem(f"A{len(self.points)} ({x},{y})")
        label.setBrush(QBrush(QColor("red")))
        label.setPos(x + 8, y - 8)
        self.scene.addItem(label)
        self.marker_items.append(label)

        self.info_label.setText(self._status_text())

        if len(self.points) == self.num_anchors:
            self.done_button.setEnabled(True)

    def reset(self):
        self.points = []
        for item in self.marker_items:
            self.scene.removeItem(item)
        self.marker_items = []
        self.info_label.setText(self._status_text())
        self.done_button.setEnabled(False)

    def finish(self):
        if self.on_done:
            self.on_done(self.points)
        self.close()