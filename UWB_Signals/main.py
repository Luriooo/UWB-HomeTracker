import sys
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PySide6.QtGui import QIcon, QPixmap
from UWB_Signals import UWB_Generator
from Floorplan_Processor import Floorplan_Processor
from Anchor_Picker import AnchorPicker

###########################################################
## Um alle benötigten Libraries zu Installieren:         ##
## pip install -r requirements.txt im Terminal ausführen ##
##                                                       ##
## Um das Programm zu starten                            ##
## python main.py im Terminal ausführen                  ##
###########################################################

uwb = UWB_Generator()
prz = Floorplan_Processor()
app = FastAPI()
# CORS Settings
origins = [
    "http://localhost:8000/signal",
    "http://0.0.0.0:8000/signal",
    "http://localhost:8000",
    "http://0.0.0.0:8000",
    "http://localhost:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API Schema
@app.get("/")
def read_root():
    return {"message": "UWB Signal Simulator API"}

# /signals for Tag Coordinates
@app.get("/signal")
def get_signal():
    if uwb.tag_est is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No signal generated yet. Press 'Random Position' first."}
        )
    return {
        "estimated": {"x": float(uwb.tag_est[0]), "y": float(uwb.tag_est[1])},
        "true":      {"x": float(uwb.tag_true[0]), "y": float(uwb.tag_true[1])},
        "error":   float(uwb.error),
    }
# /misc for Floorplan path extent and anchor Positions
@app.get("/misc")
def get_misc():
    if prz.floorplan_path_json is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No Floorplan set"}
        )
    return {
        "Floorplan_Path": prz.floorplan_path_json,
        "Extent": {"x": prz.extent_x, "y": prz.extent_y},
        "Anchors": uwb.anchors.tolist()
    }

class Ui(QWidget):
    def __init__(self):

        Signal_icon = QIcon()
        Signal_icon.addFile("Icon_UWB.png")

        super().__init__()
        # UI Layout
        self.setWindowTitle("UWB Signal Simulator")
        self.setWindowIcon(Signal_icon)
        self.resize(400, 400)

        self.anchor_picker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.label = QLabel("Setup!")

        self.button = QPushButton("Set Floorplan")
        self.button.setFixedWidth(150)
        self.button.clicked.connect(self.set_floorplan)

        self.button2 = QPushButton("Set Anchors")
        self.button2.setFixedWidth(150)
        self.button2.clicked.connect(self.open_anchor_picker)

        self.label2 = QLabel("Select Scenario!")

        self.button3 = QPushButton("Random Position")
        self.button3.setFixedWidth(150)
        self.button3.clicked.connect(uwb.random_signal)

        self.button4 = QPushButton("Moving Position")
        self.button4.setFixedWidth(150)
        self.button4.clicked.connect(uwb.moving_signal)

        self.status = QLabel("")
        self.status.setStyleSheet("color: gray;")

        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        layout.addWidget(self.label2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        layout.addWidget(self.status)

    # call process_image from Florrplan_Processor.py
    def set_floorplan(self):
        prz.process_image()
        self.status.setText("Floorplan Gesetzt!")

    # call Anchor pick UI from AnchorPicker.py
    def open_anchor_picker(self):
        if prz.floorplan is None:
            self.status.setText("Bitte zuerst 'Set Floorplan' ausführen.")
            return
        self.anchor_picker = AnchorPicker(
            self, prz.floorplan, num_anchors=4, on_done=self.set_anchors
        )
        self.anchor_picker.show()

    #set anchors for UWB_Signals.py
    def set_anchors(self, coords):
        uwb.set_anchors(coords)
        self.status.setText(f"{len(coords)} Anchors gesetzt: {coords}")


if __name__ == "__main__":
    # FastAPI background daemon thread
    api_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000),
        daemon=True,  # dies automatically when UI closes
    )
    api_thread.start()
    print("FastAPI running at http://localhost:8000")

    qt_app = QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(qt_app.exec())
