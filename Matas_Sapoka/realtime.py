import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import cv2
import time
import numpy as np
import math

model_path = 'C:\\Users\\Gaming\\Desktop\\UDULUS\\pose_landmarker_lite.task'

# General setup
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Global variable to store latest results
latest_results = None

# Callback function for LIVE_STREAM mode
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    global latest_results
    latest_results = result

# Pose comparison functions from Move Mirror article
def normalize_pose(landmarks):
    """L2 normalization of pose keypoints"""
    pose_vector = []
    for lm in landmarks:
        pose_vector.extend([lm.x, lm.y])
    
    # L2 normalization
    pose_array = np.array(pose_vector)
    norm = np.linalg.norm(pose_array)
    if norm == 0:
        return pose_array
    return pose_array / norm

def cosine_distance(pose1, pose2):
    """Calculate cosine distance between two normalized poses"""
    # Cosine similarity
    dot_product = np.dot(pose1, pose2)
    # Convert to distance: sqrt(2 * (1 - similarity))
    distance = math.sqrt(2 * (1 - dot_product))
    return distance

def weighted_distance(landmarks1, landmarks2):
    """Weighted distance using confidence scores (Move Mirror formula)"""
    total_distance = 0.0
    total_confidence = 0.0
    
    for i in range(len(landmarks1)):
        lm1 = landmarks1[i]
        lm2 = landmarks2[i]
        
        # Use visibility as confidence (MediaPipe provides this)
        confidence1 = lm1.visibility if hasattr(lm1, 'visibility') else 1.0
        confidence2 = lm2.visibility if hasattr(lm2, 'visibility') else 1.0
        
        # Weighted euclidean distance for this keypoint
        dx = lm1.x - lm2.x
        dy = lm1.y - lm2.y
        distance_squared = dx*dx + dy*dy
        
        # Weight by confidence
        weight = confidence1 * confidence2
        total_distance += weight * distance_squared
        total_confidence += weight
    
    if total_confidence == 0:
        return float('inf')
    
    return math.sqrt(total_distance / total_confidence)

options_live = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result,
    min_pose_detection_confidence=0.6,
    min_pose_presence_confidence=0.6,
    min_tracking_confidence=0.6)

options_video = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    min_pose_detection_confidence=0.6,
    min_pose_presence_confidence=0.6,
    min_tracking_confidence=0.6)

pose_live = PoseLandmarker.create_from_options(options_live)
pose_video = PoseLandmarker.create_from_options(options_video)
mpPose = mp.solutions.pose

# End of general setup

# Load reference video and process all frames
print("Loading reference video...")
ref_cap = cv2.VideoCapture('C:\\Users\\Gaming\\Desktop\\UDULUS\\nika.mp4')
reference_poses = []
ref_frame_timestamp = 0

while True:
    success, ref_frame = ref_cap.read()
    if not success:
        break
    
    ref_rgb = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2RGB)
    ref_mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=ref_rgb)
    ref_results = pose_video.detect_for_video(ref_mp_image, ref_frame_timestamp)
    ref_frame_timestamp += 33
    
    if ref_results.pose_landmarks:
        reference_poses.append(ref_results.pose_landmarks[0])
    else:
        reference_poses.append(None)

ref_cap.release()
print(f"Loaded {len(reference_poses)} reference frames")

# Start webcam
cap = cv2.VideoCapture(0)
pTime = 0
frame_timestamp_ms = 0
ref_frame_index = 0
selected_indices = [0, 11, 12, 13, 14, 26, 23, 24, 25, 30, 29]

while True:
    success, img = cap.read()
    if not success:
        break
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    
    frame_timestamp_ms = int(time.time() * 1000)
    pose_live.detect_async(mp_image, frame_timestamp_ms)
    
    # Get current reference pose (loop through reference video)
    if len(reference_poses) > 0:
        ref_pose = reference_poses[ref_frame_index % len(reference_poses)]
        ref_frame_index += 1
    else:
        ref_pose = None
    
    # Use latest results from callback
    if latest_results and latest_results.pose_landmarks and ref_pose:
        user_pose = latest_results.pose_landmarks[0]
        
        # Calculate similarity using weighted distance
        distance = weighted_distance(user_pose, ref_pose)
        
        # Threshold for matching (lower = more similar)
        match_threshold = 0.1
        is_match = distance < match_threshold
        
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        for idx in selected_indices:
            if idx < len(user_pose):
                lm = user_pose[idx]
                pose_landmarks_proto.landmark.append(
                    landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                )
        
        for id, im in enumerate(pose_landmarks_proto.landmark):
            h, w, c = img.shape
            cx, cy = int(im.x * w), int(im.y * h)
            
            # Green if match, Red if mismatch
            color = (0, 255, 0) if is_match else (0, 0, 255)
            
            if id == 0:
                cv2.rectangle(img, (cx - 40, cy - 40), (cx + 40, cy + 40), color)
            else:
                cv2.rectangle(img, (cx - 12, cy - 12), (cx + 12, cy + 12), color)
        
        # Display match info
        match_text = f"Match: {distance:.3f} ({'GOOD' if is_match else 'BAD'})"
        cv2.putText(img, match_text, (70, 100), cv2.FONT_HERSHEY_PLAIN, 2, 
                    (0, 255, 0) if is_match else (0, 0, 255), 2)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime 

    cv2.putText(img, f'FPS: {int(fps)}', (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()