import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose if hasattr(mp, "solutions") else None
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def extract_angles_from_video(video_path):

    cap = cv2.VideoCapture(video_path)

    elbow_angles, knee_angles, hip_angles = [], [], []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_pose.Pose().process(image)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Get points
            shoulder = [landmarks[11].x, landmarks[11].y]
            elbow = [landmarks[13].x, landmarks[13].y]
            wrist = [landmarks[15].x, landmarks[15].y]

            hip = [landmarks[23].x, landmarks[23].y]
            knee = [landmarks[25].x, landmarks[25].y]
            ankle = [landmarks[27].x, landmarks[27].y]

            # Calculate angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)

            elbow_angles.append(elbow_angle)
            knee_angles.append(knee_angle)
            hip_angles.append(hip_angle)

            # -------- DRAW --------
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # -------- FEEDBACK --------
            feedback = ""

            if elbow_angle > 90:
                feedback = "Go Lower"
            elif knee_angle > 100:
                feedback = "Bend Knees More"
            else:
                feedback = "Good Form"

            cv2.putText(frame, feedback, (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0,255,0), 2)

        

    cap.release()
    

    return elbow_angles, knee_angles, hip_angles