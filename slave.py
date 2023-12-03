import rpyc
import win32com
import win32gui,win32ui, win32con
import win32api
from win32api import GetSystemMetrics
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QTimer

from share import get_connection
conn = get_connection()

# Now you can use the connection to interact with the server
# For example, you can call remote functions or access remote attributes
window = None



class TransparentWindow(QWidget):

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.current_x, self.current_y = self.pos().x(), self.pos().y()

    def __init__(self):
        global slave_key
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Set window flags to make it frameless and topmost
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        
        # Load the image
        pixmap = QPixmap("pointer.png").scaled(64, 64)  # Resize the image to 64x64
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label)
        
        # Add a label to display self.key
        self.key_label = QLabel('Not connect', self)
        self.key_label.setStyleSheet("background-color: black; color: white;")  # Set background color to black and text color to white
        layout.addWidget(self.key_label)
        
        
        # Create a QTimer with a timeout of 0.03 ms
        self.timer = QTimer()
        self.timer.start(30)  # 30 milliseconds = 0.03 seconds
        self.timer.timeout.connect(self.update_move)
        self.setLayout(layout)
        self.current_x, self.current_y = win32api.GetCursorPos()
        self.window().move(self.current_x, self.current_y)
        # Connect to the server
        self.conn = rpyc.connect("localhost", 18861)
        self.conn.root.add_slave(lambda key: self.init_connect(key))

        self.setMouseTracking(True)
        self.dragging = False
        self.offset = None
        
    def init_connect(self, key):
        self.key = key
        self.key_label.setText(str(self.key))
        print("Slave key: " + str(self.key))
        
    def update_move(self):
        slave = self.conn.root.query_slave(self.key)
        if slave is None:
            return
        dx, dy = self.conn.root.consume_move_slave(self.key)
        self.current_x += dx
        self.current_y += dy
        if dx != 0 or dy != 0:
            self.window().move(self.current_x, self.current_y)
    
    def closeEvent(self, event):
        self.conn.root.remove_slave(self.key)
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentWindow()
    try:
        window.show()
    except Exception as e:
        window.conn.root.remove_slave(window.key)
        window.conn.close()
    sys.exit(app.exec_())



