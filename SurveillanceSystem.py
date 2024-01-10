import sys
import cv2
import mediapipe as mp
import numpy as np
import statistics
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PIL import Image, ImageDraw
import threading
import pygame
from PyQt5.QtGui import QIcon

from clf import *
from config_ui import *

class Surveillance_app(QMainWindow):
    def __init__(self):
        super().__init__()
        self.q_image = None

        self.alert_status = False  
        self.alert_duration = 20 

        # Initialize pygame mixer
        pygame.mixer.init()
        self.alarm_sound = pygame.mixer.Sound("_internal/data/alarm.wav")  

        icon = QIcon('./_internal/assets/icon/logo2.ico')  # Replace with your icon file path
        self.setWindowIcon(icon)

        self.setWindowTitle("Surveillance System")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
      
    def initUI(self):
        self.data = "data"
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


        # layouts
        main_layout = QVBoxLayout(central_widget)
        bottom_layout = QHBoxLayout()

        # Create a label to display the video feed
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.video_label, 90)  # Allocate 90% of space to video preview

        # Back Button
        self.back_button = QPushButton("Back")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.back_to_config)
        bottom_layout.addWidget(self.back_button)
        self.back_button.setVisible(False)

        # Notification
        self.landmark_label = QLabel(self)
        self.landmark_label.setWordWrap(True) 
        bottom_layout.addWidget(self.landmark_label)
        main_layout.addLayout(bottom_layout, 10)  # Allocate 10% of space to notifications
    
        # Alarm button
        self.alert_button = QPushButton(self)
        self.alert_button.setIcon(QIcon("icon/white/bell.svg"))  
        self.alert_button.setFixedWidth(30)
        self.alert_button.clicked.connect(self.stop_alert)
        bottom_layout.addWidget(self.alert_button)

        # Create a button to toggle fullscreen mode
        self.fullscreen_button = QPushButton(self)
        self.fullscreen_button.setIcon(QIcon("icon/white/maximize.svg")) 
        self.fullscreen_button.setFixedWidth(30)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        bottom_layout.addWidget(self.fullscreen_button)

    def start_alert(self):
        if not self.alert_status:
            self.alert_status = True
            print("Drowning alert system is ON")
            self.alarm_sound.play() 

    def stop_alert(self):
        if self.alert_status:
            self.alert_status = False
            print("Drowning alert system is OFF")
            self.alarm_sound.stop()  
            self.alert_button.setVisible(False)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()  # Exit fullscreen mode
            self.fullscreen_button.setIcon(QIcon("icon/white/maximize.svg"))
        else:
            self.showFullScreen()  # Enter fullscreen mode
            self.fullscreen_button.setIcon(QIcon("icon/white/minimize.svg"))

    def back_to_config(self):
        from config_ui import config_App
        config = config_App()
        config.show()
        self.close()
       
    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        super().closeEvent(event)

    def read_camera_index(self,file_path):
        try:
            with open(file_path, 'r') as file:
                camera_index = int(file.readline().strip())
            return camera_index
        except FileNotFoundError:
            return None  
        except ValueError:
            return None  

    def read_duration(self,file_path):
        try:
            with open(file_path, 'r') as file:
                duration = int(file.readline().strip())
            return duration
        except FileNotFoundError:
            return 75  
        except ValueError:
            return 75

    def read_resolution(self, file_path):
        with open(file_path, 'r') as file:
            width, height = map(int, file.readline().strip().split(','))
        return width, height

    def read_percentage_coordinates(self, file_path):
        percentage_coordinates = []
        with open(file_path, 'r') as file:
            for line in file:
                x, y = map(float, line.strip().split(','))
                percentage_coordinates.append((x, y))
        return percentage_coordinates

    def percent_to_pixel(self, width, height, percentages):
        return [(int(width * x), int(height * y)) for x, y in percentages]

    def point_inside_polygon(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(1, n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def process_video(self):

        sys.stdout = open(os.devnull, 'w')
        # Read the texts
        camera_index = self.read_camera_index("_internal/data/camera_index.txt")
        # camera_index = "Testing_video\WhatsApp Unknown 2023-10-29 at 1.53.29 PM\WhatsApp Video 2023-10-28 at 11.18.18 PM.mp4"


        frame_width, frame_height = self.read_resolution('_internal/data/resolution.txt')
        polygon_vertices_percent = self.read_percentage_coordinates('_internal/data/coordinates.txt')
        scene_size = self.read_duration("_internal/data/read_duration.txt")
        self.alert_button.setVisible(False)

        polygon_vertices = self.percent_to_pixel(frame_width, frame_height, polygon_vertices_percent)
        # Create a mask
        mask = Image.new('L', (frame_width, frame_height), 0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(polygon_vertices, fill=255)

        # Create a capture object for the video file with the specified resolution
        self.cap = cv2.VideoCapture(camera_index)
        
        # Initialize the MediaPipe Pose model
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Initialize MediaPipe's drawing module for visualizing landmarks
        mp_drawing = mp.solutions.drawing_utils

        range_width = 150 
        rande_height = 150
        box_color = (0, 255, 0)
        desired_frame_rate = 30
        scene = []
        self.landmark_label.setText(f'Please wait ...')

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (frame_width, frame_height))

            if not ret:
                break
                
            # Create a copy of the frame to draw on
            frame_with_overlay = frame.copy()

            # Convert the frame to PIL Image
            frame_pil = Image.fromarray(cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB))

            # Apply the mask to the frame
            cropped_frame = Image.new('RGB', (frame_width, frame_height))
            cropped_frame.paste(frame_pil, mask=mask)

            # Convert the cropped frame back to OpenCV format
            cropped_frame_cv2 = cv2.cvtColor(np.array(cropped_frame), cv2.COLOR_RGB2BGR)

            # Convert the frame to RGB format
            RGB = cv2.cvtColor(cropped_frame_cv2, cv2.COLOR_BGR2RGB)

            # Process the RGB frame to get the pose landmarks
            results = pose.process(RGB)

            # Check if landmarks are detected
            if results.pose_landmarks:
                # Store the pixel coordinates of the detected landmarks
                landmark_coordinates = []

                for connection in mp_pose.POSE_CONNECTIONS:
                    # Extract the indices of the connected landmarks
                    start_landmark, end_landmark = connection

                    # Get the pixel coordinates of the connected landmarks
                    start_x = int(results.pose_landmarks.landmark[start_landmark].x * frame_width)
                    start_y = int(results.pose_landmarks.landmark[start_landmark].y * frame_height)
                    end_x = int(results.pose_landmarks.landmark[end_landmark].x * frame_width)
                    end_y = int(results.pose_landmarks.landmark[end_landmark].y * frame_height)

                    # Check if both the start and end landmarks are inside the polygon
                    if self.point_inside_polygon(start_x, start_y, polygon_vertices) and self.point_inside_polygon(end_x, end_y, polygon_vertices):
                        # cv2.line(frame_with_overlay, (start_x, start_y), (end_x, end_y), (255, 0, 0), 1)
                        # cv2.circle(frame_with_overlay, (start_x, start_y), 5, (255, 0, 0), -2)
                        # cv2.circle(frame_with_overlay, (end_x, end_y), 5, (255, 0, 0), -1)

                        # Store the pixel coordinates of the connected landmarks
                        landmark_coordinates.append((start_landmark, (start_x, start_y)))
                        landmark_coordinates.append((end_landmark, (end_x, end_y)))

                # Calculate the bounding box around the stored landmark coordinates
                if landmark_coordinates:
                    min_x = min(landmark_coordinates, key=lambda x: x[1][0])[1][0] - 1
                    max_x = max(landmark_coordinates, key=lambda x: x[1][0])[1][0] + 1
                    min_y = min(landmark_coordinates, key=lambda x: x[1][1])[1][1] - 1
                    max_y = max(landmark_coordinates, key=lambda x: x[1][1])[1][1] + 1

                    # Draw the bounding box
                    cv2.rectangle(frame_with_overlay, (min_x, min_y), (max_x, max_y), box_color, 2)

                    # Calculate and print the coordinates of the skeleton points within the bounding box
                    landmark_positions = [{landmark: (int((x - min_x) / (max_x - min_x) * range_width), int((y - min_y) / (max_y - min_y) * rande_height))} for landmark, (x, y) in landmark_coordinates if min_x <= x <= max_x and min_y <= y <= max_y]
                    # print(f'Landmark positions: {landmark_positions} (within {range_width}x{rande_height} box)')

                predicted_y = classification(landmark_positions)
                y_test_pred_classes = np.argmax(predicted_y, axis=1)
                print(y_test_pred_classes)
                # Append the number to the list
                scene.append(y_test_pred_classes[0])
                # self.landmark_label.setText(f'Classifition: {y_test_pred_classes}')

            else:
                scene.append(3)
            
            # scene Clf
            # Check if we have collected scene
            if len(scene) == scene_size:
                mode = statistics.mode(scene)
                # mode = 0                                      
                if mode == 0:
                    box_color = (0, 0, 255)
                    self.start_alert()
                    self.landmark_label.setText(f'Classifition: Drowning')
                    self.alert_button.setVisible(True)
                elif mode == 1:
                    self.landmark_label.setText(f'Classifition: None')
                    box_color = (0, 255, 0)
                elif mode == 2:
                    self.landmark_label.setText(f'Classifition: Swimming')
                    box_color = (0, 255, 0)
                elif mode == 3:
                    self.landmark_label.setText(f'No swimmer avialable')
                    box_color = (0, 255, 0)
                else:
                    box_color = (0, 255, 0)
                scene = []

            # Draw the polygon outline on the frame
            cv2.polylines(frame_with_overlay, [np.array(polygon_vertices)], isClosed=True, color=(0, 255, 0), thickness=2)
            
            frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
            self.q_image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(self.q_image)
            self.video_label.setPixmap(pixmap)

            # Control the frame rate by introducing a delay
            delay_ms = int(1000 / desired_frame_rate)  # Calculate delay in milliseconds
            # Break the loop if the 'q' key is pressed
            if cv2.waitKey() & 0xFF == ord('q'):
                break
        
        # Release the capture object and destroy any OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()
    sys.stdout = sys.__stdout__

# def main():
#     app = QApplication(sys.argv)
#     window = Surveillance_app()
#     window.show()
#     window.process_video()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()

