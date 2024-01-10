from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from SurveillanceSystem import *
import ast
from PyQt5.QtGui import QIcon

class config_App(QMainWindow):
    def __init__(self):
        super().__init__()

        icon = QIcon('_internal/assets/icon/logo2.ico')  # Replace with your icon file path
        self.setWindowIcon(icon)

        self.setWindowTitle("Configuration")
        self.setGeometry(100, 100, 800, 500)

        self.initUI()

    def initUI(self): 
        self.data = '_internal/data'
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setStyleSheet("*{\n"
"    color:#ffffff;\n"
"    background-color:rgb(81, 81, 81);\n"
"}\n"
"QVBoxLayout{\n"
"    background-color: rgb(106, 106, 106);\n"
"    border-radius :10px;\n"
"    background-image: url('_internal/assets/655.png');\n"
"}\n"
"#left_menu, #mainFrame{\n"
"    background-color:rgb(81, 81, 81);\n"
"    border-radius :5px;\n"
"}\n"
"QPushButton{\n"
"    background-color:rgb(35, 106, 106);\n"
"    color:rgb(199, 199, 199);\n"
"    border-radius :5px;\n"
"    height:20px;\n"
"    margin:4px;\n"
"}\n"
"QPushButton:hover, QComboBox::drop-down:hover{\n"
"    background-color:rgb(21, 54, 54);\n"
"    border:1px solid rgb(158, 158, 158);\n"
"}\n"
"QLabel{\n"
"    color:rgb(232, 232, 232);\n"
"    border-radius :5px;\n"
"}\n"
"QTextEdit, QComboBox{\n"
"    background-color:rgb(109, 109, 109);\n"
"    border-radius :5px;\n"
"}\n"
"QComboBox::drop-down {\n"
"    background-color: rgb(35, 106, 106);\n"
"    color: #333333;\n"
"    border-top-right-radius: 5px;\n"
"    border-bottom-right-radius: 5px;\n"
"}\n"
"QComboBox::down-arrow{\n"
"    image: url('icon/white/chevron-down.svg');\n"
"    width: 16px;\n"
"    height: 16px;\n"
"}\n"
"QComboBox::up-arrow {\n"
"     \n"
"    image: url('icon/white/chevron-up.svg');\n"
"    width: 16px; \n"
"    height: 16px; \n"
"}\n"
"#image{\n"
"    image: url('_internal/assets/65.png');\n"
"}")        



        # Layouts
        main_layout = QHBoxLayout(central_widget)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Camera Selector
        camera_label = QLabel("Select Camera:")
        self.camera_combo = QComboBox()
        num_cameras = self.populate_camera_combo()

        # Set the default camera index to 0
        default_camera_index = 0
        self.camera_combo.setCurrentIndex(default_camera_index)
        self.camera_combo.setMinimumSize(QtCore.QSize(0, 20))
        # Resolution Selector
        resolution_label = QLabel("Select Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.setMinimumSize(QtCore.QSize(0, 20))
        self.resolution_combo.addItem("(640, 480)")
        self.resolution_combo.addItem("(1280, 720)")

        # Polygon Vertices Input
        polygon_label = QLabel("Vertices of pool in Percentage:")
        polygon_label.setWordWrap(True)
        self.polygon_input = QTextEdit()
        self.polygon_input.setMaximumSize(QtCore.QSize(16777215, 50))
        
        # self.polygon_input.setPlainText("(0, 0), (1, 0), (1, 1), (0, 1)")
        polygon_vertices_percent = self.read_percentage_coordinates(f'{self.data}/coordinates.txt')
        self.polygon_input.setPlainText(f'{polygon_vertices_percent}')

        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.get_user_inputs)

        # rest Burron
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_coordinates)

        set_button = QPushButton("Set")
        set_button.clicked.connect(self.select_camera)
        # Add buttons to the button layout
        button_layout.addWidget(set_button)
        button_layout.addWidget(reset_button)

        # Add widgets to left layout
        left_layout.addWidget(camera_label)
        left_layout.addWidget(self.camera_combo)
        left_layout.addWidget(resolution_label)
        left_layout.addWidget(self.resolution_combo)

        # Add the button layout to the left layout
        left_layout.addLayout(button_layout)
        left_layout.addWidget(polygon_label)
        left_layout.addWidget(self.polygon_input)

        self.spacerItem = QtWidgets.QLabel("")
        self.spacerItem.setMinimumSize(QtCore.QSize(16777215, 200))

        left_layout.addWidget(self.spacerItem)
        left_layout.addWidget(ok_button)
        
        # Video Preview
        self.video_label = QLabel(self)
        self.video_label.setText(f'Select the camera and press the set then select the hazardous zone then press the OK. if You want to \nprivious configarations press OK')
        if num_cameras == 0:
            print("No cameras available")
            self.video_label.setText(f'No cameras available. check the camera inputs and press the reset')
        self.video_label.setWordWrap(True)
        self.video_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.video_label)

        # Set layout proportions
        main_layout.addLayout(left_layout, 20)
        main_layout.addLayout(right_layout, 85)

        # Initialize video-related variables
        self.video_capture = None
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.update_video_frame)
        self.video_frame = None
        self.coordinates = []
        
        self.draw_circle_flag = False


    def select_camera(self):
        selected_camera_index = int(self.camera_combo.currentText())  # Retrieve selected camera index
        selected_resolution = eval(self.resolution_combo.currentText())
        # polygon_input = self.polygon_input.toPlainText()

        # Initialize the video capture with the selected camera and resolution
        self.video_capture = cv2.VideoCapture(selected_camera_index)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, selected_resolution[0])
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, selected_resolution[1])

        # Start the video timer to update the video frame
        self.video_timer.start(20)  # Adjust the timer interval as needed

    def get_user_inputs(self):
        selected_camera_index = int(self.camera_combo.currentText())  # Retrieve selected camera index
        selected_resolution = eval(self.resolution_combo.currentText())
        polygon_input = ast.literal_eval(self.polygon_input.toPlainText())
        
        # Save the inputs to files
        self.save_camera_index(f'{self.data}/camera_index.txt', selected_camera_index)
        self.save_resolution(f'{self.data}/resolution.txt', selected_resolution) 
        self.save_percentage_coordinates(f'{self.data}/coordinates.txt', polygon_input)

        # Initialize the video capture with the selected camera and resolution
        self.video_capture = cv2.VideoCapture(selected_camera_index)

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, selected_resolution[0])
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, selected_resolution[1])

        # Start the video timer to update the video frame
        self.video_timer.start(20)  # Adjust the timer interval as needed

        # Process user inputs as needed
        print(f"Selected Camera Index: {selected_camera_index}")
        print(f"Selected Resolution: {selected_resolution}")
        print(f"Polygon Vertices (Percentage): {polygon_input}")

        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

        # Open the second window
        Surveillanceapp = Surveillance_app()
        Surveillanceapp.show()
        self.close()
        Surveillanceapp.process_video()

    def update_video_frame(self):
        if self.video_capture is not None and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if ret:
                self.video_frame = frame.copy()

                # Draw the polygon if four points are selected
                if len(self.coordinates) == 4:
                    self.draw_polygon()
                    self.draw_circle_flag = False  # Reset the flag
                
                if self.draw_circle_flag:
                    # Draw the circle on the video frame
                    for x, y in self.coordinates:
                        cv2.circle(self.video_frame, (x, y), 5, (0, 255, 0), -1)
                    # self.draw_circle_flag = False  # Reset the flag

                # Update the video frame in the QLabel
                frame_rgb = cv2.cvtColor(self.video_frame, cv2.COLOR_BGR2RGB)
                q_image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.video_label.setPixmap(pixmap)

    def draw_polygon(self):
        if len(self.coordinates) == 4:
            polygon_pts = np.array(self.coordinates, np.int32)
            polygon_pts = polygon_pts.reshape((-1, 1, 2))
            cv2.polylines(self.video_frame, [polygon_pts], isClosed=True, color=(0, 255, 0), thickness=2)
           
            # Update the Polygon Vertices (Percentage) QTextEdit
            percentage_coordinates = [(x / self.video_frame.shape[1], y / self.video_frame.shape[0]) for x, y in self.coordinates]
            self.polygon_input.setPlainText(str(percentage_coordinates))

    def mousePressEvent(self, event):
        if self.video_capture is not None and self.video_capture.isOpened():
            x_window = event.x()  # Get the x-coordinate of the mouse click in window coordinates
            y_window = event.y()  # Get the y-coordinate of the mouse click in window coordinates

            # Get the position and size of the video frame within the window
            video_frame_geometry = self.video_label.geometry()
            x_frame = video_frame_geometry.x()
            y_frame = video_frame_geometry.y()
            width_frame = video_frame_geometry.width()
            height_frame = video_frame_geometry.height()

            # Get the resolution of the video frame
            frame_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            # Calculate the scaling factors to map window coordinates to video frame coordinates
            x_scale = frame_width / width_frame
            y_scale = frame_height / height_frame

            # Calculate the adjusted mouse click coordinates in video frame coordinates
            x_video = int((x_window - x_frame) * x_scale)
            y_video = int((y_window - y_frame) * y_scale)

            if len(self.coordinates) < 4:
                self.coordinates.append((x_video, y_video))
                self.draw_circle_flag = True  # Set the flag to draw a circle

    def load_files(self):
        try:
            with open('_internal/data/coordinates.txt', 'r') as file:
                self.data = '_internal/data'
        except FileNotFoundError:
            self.data = 'data'  
        except ValueError:
            self.data = 'data'

    def reset_coordinates(self):
        self.coordinates = []  # Clear the coordinates list
        self.polygon_input.setPlainText("[(0, 0), (1, 0), (1, 1), (0, 1)]")
        self.video_capture = None
        self.video_label.setText(f'Select the camera and press the set then select the hazardous zone then press the OK. if You want to privious configarations press OK')
    
    def populate_camera_combo(self):
        num_cameras = 0
        while True:
            cap = cv2.VideoCapture(num_cameras)
            if not cap.isOpened():
                break
            cap.release()
            self.camera_combo.addItem(str(num_cameras))  # Add camera index as an item
            num_cameras += 1
        # num_cameras = 0
        if num_cameras == 0:
            self.camera_combo.addItem("No cameras available")  # Add camera index as an item
        return num_cameras

    def read_percentage_coordinates(self, file_path):
        percentage_coordinates = []
        with open(file_path, 'r') as file:
            for line in file:
                x, y = map(float, line.strip().split(','))
                percentage_coordinates.append((x, y))
        return percentage_coordinates

    def save_percentage_coordinates(self, file_path, percentage_coordinates):
        with open(file_path, 'w') as file:
            for x, y in percentage_coordinates:
                file.write(f"{x:.6f},{y:.6f}\n")

    def save_resolution(self, file_path, resolution):
        with open(file_path, 'w') as file:
            file.write(f"{resolution[0]},{resolution[1]}\n")
    
    def save_camera_index(self, file_path, camera_index):
        with open(file_path, 'w') as file:
            file.write(f"{camera_index}\n")

