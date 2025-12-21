from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
from PIL import Image
from processing import Vector
import serial

import socket

import requests
import time

ESP32_IP = "XXX"  # ESP32 IP
URL = f"http://{ESP32_IP}/send"

def send_data_to_esp32(data):
    try:
        response = requests.post(URL, data={"data": data})
        if response.status_code == 200:
            print(f"Data sent successfully: {data}")
        else:
            print(f"Failed to send data: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")



model_path = "pose_landmarker_heavy.task"
shouder_pivot_point = Vector(0, 0, 0)
elbow_point = Vector(0, 0, 0)
wrist_point = Vector(0, 0, 0)

elbow_angle = 0
arm__vert_angle  = 0
arm_hori_angle =  0

def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  pose_world_landmarks_list = detection_result.pose_world_landmarks
  annotated_image = np.copy(rgb_image)
  height, width, _ = annotated_image.shape

  

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]
    pose_world_landmarks = pose_world_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
    
    
    for i in [11, 13, 15]:
       if i < len(pose_landmarks) and i < len(pose_world_landmarks):
          screen_lm = pose_landmarks[i]
          world_lm = pose_world_landmarks[i]

        
          if (world_lm.visibility > 0.7):
             cx, cy = int(screen_lm.x * width), int(screen_lm.y * height)
             coord_text = f"{world_lm.x - shouder_pivot_point.x: .2f}, {world_lm.y - shouder_pivot_point.y: .2f}, {world_lm.z - shouder_pivot_point.z: .2f}"
             cv2.putText(annotated_image, coord_text, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    shoulder_point = Vector(pose_world_landmarks[11].x, pose_world_landmarks[11].y, pose_world_landmarks[11].z)
    elbow_point = Vector(pose_world_landmarks[13].x, pose_world_landmarks[13].y, pose_world_landmarks[13].z)
    wrist_point = Vector(pose_world_landmarks[15].x, pose_world_landmarks[15].y, pose_world_landmarks[15].z)
    vertical = Vector(0, 1, 0)
    horizontal = Vector(0, 0, 1)
    upper_arm = shoulder_point.subtract(elbow_point)
    forearm = wrist_point.subtract(elbow_point)
    elbow_angle = upper_arm.angle_with(forearm) - 60.0
    arm__vert_angle  = 180 - vertical.angle_with(upper_arm)
    arm_hori_angle =  horizontal.angle_with(upper_arm)
    cv2.putText(annotated_image, f"Angle: {elbow_angle:.2f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(annotated_image, f"Angle: {arm__vert_angle:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(annotated_image, f"Angle: {arm_hori_angle:.2f}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    send = f"{elbow_angle:.2f} {arm__vert_angle:.2f}-{arm_hori_angle:.2f}\n"
    # SEND DATA TO ESP
    # write_data(send)
    send_data(send)


    

  return annotated_image



# DEFAULT CAMERA
cam = cv2.VideoCapture(0)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))


# AI CONFIG
base_options = python.BaseOptions(model_asset_path=model_path)
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
 
def send_data(message):
    data = message
    if data.__class__ is str:
        send_data_to_esp32(data)
   

def print_pose_landmarker_result(result):
    print("PoseLandmarkerResult:")
    
    #if result.pose_landmarks:
    #    print("  Landmarks:")
    #    for i, landmark in enumerate(result.pose_landmarks[0]):  # Assuming one pose
    #        print(f"    Landmark #{i}:")
    #        print(f"      x            : {landmark.x:.6f}")
    #        print(f"      y            : {landmark.y:.6f}")
    #        print(f"      z            : {landmark.z:.6f}")
    #        print(f"      visibility   : {landmark.visibility}")
    #        print(f"      presence     : {landmark.presence}")
    
    if result.pose_world_landmarks:
        print("  WorldLandmarks:")
        for i, landmark in enumerate(result.pose_world_landmarks[0]):  # Assuming one pose
            if (i == 11 or i == 13 or i == 15 or i == 17 or i == 19 or i == 21):
              if (landmark.visibility > 0.7):
                  print(f"    Landmark #{i} - {numToName[i]}:")
                  print(f"      x            : {landmark.x:.6f}")
                  print(f"      y            : {landmark.y:.6f}")
                  print(f"      z            : {landmark.z:.6f}")
                  print(f"      visibility   : {landmark.visibility}")
                  print(f"      presence     : {landmark.presence}")

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True)
detector = vision.PoseLandmarker.create_from_options(options)

while True:
    ret, frame = cam.read()

    frame = cv2.flip(frame, 1)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    # PROCESSING
    outFrame = detector.detect(image)
    annotated_image = draw_landmarks_on_image(image.numpy_view(), outFrame)

    


    # Write the frame to the output file
    out.write(annotated_image)

    # Display the captured frame
    ##cv2.imshow('Camera', cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    cv2.imshow('Camera', annotated_image)
    # !!!!! print_pose_landmarker_result(outFrame)
    

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
out.release()
cv2.destroyAllWindows()


'''
POSE LADNMARK DETECTION
- Takes live video intake and produces landmark coordinates
0 - nose
1 - left eye (inner)
2 - left eye
3 - left eye (outer)
4 - right eye (inner)
5 - right eye
6 - right eye (outer)
7 - left ear
8 - right ear
9 - mouth (left)
10 - mouth (right)
11 - left shoulder
12 - right shoulder
13 - left elbow
14 - right elbow
15 - left wrist
16 - right wrist
17 - left pinky
18 - right pinky
19 - left index
20 - right index
21 - left thumb
22 - right thumb
23 - left hip
24 - right hip
25 - left knee
26 - right knee
27 - left ankle
28 - right ankle
29 - left heel
30 - right heel
31 - left foot index
32 - right foot index

NEEDED:
11 - left shoulder
13 - left elbow
15 - left wrist
17 - left pinky
19 - left index
21 - left thumb
'''

numToName = {
0 : "nose",
1 : "left eye (inner)",
2 : "left eye",
3 : "left eye (outer)",
4 : "right eye (inner)",
5 : "right eye",
6 : "right eye (outer)",
7 : "left ear",
8 : "right ear",
9 : "mouth (left)",
10 : "mouth (right)",
11 : "left shoulder",
12 : "right shoulder",
13 : "left elbow",
14 : "right elbow",
15 : "left wrist",
16 : "right wrist",
17 : "left pinky",
18 : "right pinky",
19 : "left index",
20 : "right index",
21 : "left thumb",
22 : "right thumb",
23 : "left hip",
24 : "right hip",
25 : "left knee",
26 : "right knee",
27 : "left ankle",
28 : "right ankle",
29 : "left heel",
30 : "right heel",
31 : "left foot index",
32 : "right foot index"
}