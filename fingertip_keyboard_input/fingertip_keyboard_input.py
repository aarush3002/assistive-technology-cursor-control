"""
    Main File
    Modified from two_handed_gestures/gesture_mapping/video_recognition/
    

"""
import sys
import numpy as np
import cv2
import mediapipe as mp

sys.path.append('../two_handed_gestures/gesture_mapping')

import alignment as alignment
import util

def draw_path(image, points):
    thickness = 5
    color = (0, 255, 0)
    for i in range(0, len(points) - 1):
        image = cv2.line(image, points[i], points[i+1], color, thickness)

    return image

def mediapipe_hand_setup(model_complexity=0,
                         min_detection_confidence=0.5,
                         min_tracking_confidence=0.9):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(model_complexity=model_complexity,
                           min_detection_confidence=min_detection_confidence,
                           min_tracking_confidence=min_tracking_confidence)
    return hands, mp_hands

# mediapipe setup
mp_drawing, mp_drawing_styles = util.mediapipe_draw_setup()
hands, mp_hands = mediapipe_hand_setup()
# gesture recognition setup
templates, templates_category = util.load_temp('../two_handed_gestures/gesture_mapping/data/template_image_new_wide_data/')
# video streaming setup
cap = cv2.VideoCapture(0)

# array to hold drawn points
fingertip_path_right = []

# loop start
while cap.isOpened():
    # image shape: height * width = 720 * 1280, 9:16
    success, image = cap.read()
    image = cv2.flip(image, 1)
    image_height, image_width, channels = image.shape

    if not success:
        print("Ignoring empty camera frame.")
        # streaming: continue; vedio: break
        continue
    # get hand keypoints
    mp_success, num_hands, results = util.mediapipe_process(image, hands)
    if mp_success:
        for i in range(num_hands):
            score, handedness, hand_landmarks = util.get_mediapipe_result(results, i)
            
            if handedness == 'Right': 
                    x_pixel = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x\
                                  * image_width)
                    y_pixel = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y\
                                  * image_height)
                    fingertip_path_right.append((x_pixel, y_pixel))
            
            category = util.recognize_gesture(templates, templates_category, hand_landmarks)
            util.mediapipe_draw(image, hand_landmarks, mp_hands, mp_drawing, mp_drawing_styles)
            cv2.putText(image, 'pose: ' + category, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (209, 80, 0, 255), 3)

        # draw the path of the fingertip
        image = draw_path(image, fingertip_path_right)
    
    else:
        fingertip_path_right = []

    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
