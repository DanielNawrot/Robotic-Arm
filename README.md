# Computer Vision Control for Robotic Arm

In this project I am attempting to bridge computer vision and robotics control. I am using a AI model from Google AI for developers: (https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker)

The project uses a basic laptop camera, an ESP32, and servos. The design and creation of the robotic arm is currently under work, with the vision of a small 3D printable arm. 

I use the Pose Landmark detection model to identify key points on my body by inputing video frames from a camera live. The model runs on each frame and keeps track of the point of interest. With this data, the program determines the angles of the user's elbow, and shoulder, resulting in three output angles. Using the ESP32 WiFi library, the angle data is wirelessly sent the ESP32. When the ESP32 recieves this data it sets the servos to the apprepriate angle. 

This project is currently being worked on to complete a few core objecties:
- Smooth the input data for usability.
- Optimize how the model is used and data processing.
- Have a costom designed 3D printable robotic arm be controlled using this software.
