import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import cv2
import time
import numpy as np
import math
import matplotlib.pyplot as plt

model_path = 'C:\\Users\\Gaming\\Desktop\\UDULUS\\pose_landmarker_lite.task'

# General setup
BaseOptions = python.BaseOptions
PoseLandmarker = vision.PoseLandmarker
PoseLandmarkerOptions = vision.PoseLandmarkerOptions
VisionRunningMode = vision.RunningMode

# Pose comparison functions from Move Mirror article
def normalize_pose(landmarks):
    """L2 normalization of pose keypoints"""
    pose_vector = []
    for lm in landmarks:
        pose_vector.extend([lm.x, lm.y])
    
    pose_array = np.array(pose_vector)
    norm = np.linalg.norm(pose_array)
    if norm == 0:
        return pose_array
    return pose_array / norm

def cosine_distance(pose1, pose2):
    """Calculate cosine distance between two normalized poses"""
    dot_product = np.dot(pose1, pose2)
    distance = math.sqrt(2 * (1 - dot_product))
    return distance

def weighted_distance(landmarks1, landmarks2):
    """Weighted distance using confidence scores (Move Mirror formula)"""
    total_distance = 0.0
    total_confidence = 0.0
    
    for i in range(len(landmarks1)):
        lm1 = landmarks1[i]
        lm2 = landmarks2[i]
        
        confidence1 = lm1.visibility if hasattr(lm1, 'visibility') else 1.0
        confidence2 = lm2.visibility if hasattr(lm2, 'visibility') else 1.0
        
        dx = lm1.x - lm2.x
        dy = lm1.y - lm2.y
        distance_squared = dx*dx + dy*dy
        
        weight = confidence1 * confidence2
        total_distance += weight * distance_squared
        total_confidence += weight
    
    if total_confidence == 0:
        return float('inf')
    
    return math.sqrt(total_distance / total_confidence)

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    min_pose_detection_confidence=0.3,
    min_pose_presence_confidence=0.3,
    min_tracking_confidence=0.3)

pose = PoseLandmarker.create_from_options(options)

mpPose = mp.solutions.pose

# End of general setup

ref_cap = cv2.VideoCapture('C:\\Users\\Gaming\\Desktop\\UDULUS\\nika.mp4')
reference_poses = []
ref_frame_timestamp = 0

while True:
    success, ref_frame = ref_cap.read()
    if not success:
        break
    
    ref_rgb = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2RGB)
    ref_mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=ref_rgb)
    ref_results = pose.detect_for_video(ref_mp_image, ref_frame_timestamp)
    ref_frame_timestamp += 33
    
    if ref_results.pose_landmarks:
        reference_poses.append(ref_results.pose_landmarks[0])
    else:
        reference_poses.append(None)

ref_cap.release()
print(f"Loaded {len(reference_poses)} reference frames")

comparison_video_path = 'C:\\Users\\Gaming\\Desktop\\UDULUS\\matas.mp4'

cap = cv2.VideoCapture(comparison_video_path)

# Get video properties for output
fps_out = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('C:\\Users\\Gaming\\Desktop\\UDULUS\\matas_analyzed.mp4', fourcc, fps_out, (width, height))

pTime = 0
frame_timestamp_ms = ref_frame_timestamp
frame_index = 0
selected_indices = [0, 11, 12, 13, 14, 19, 20, 26, 23, 24, 25, 30, 29]

# Landmark names for display
landmark_names = {
    0: 'Nose', 11: 'Left_Shoulder', 12: 'Right_Shoulder', 
    13: 'Left_Elbow', 14: 'Right_Elbow', 19: 'Left_hand', 20: 'Right_hand',
    23: 'Left_Hip', 24: 'Right_Hip', 25: 'Left_Knee', 
    26: 'Right_Knee', 29: 'Left_Heel', 30: 'Right_Heel'
}

# Track correct frames per landmark
landmark_correct_frames = {idx: 0 for idx in selected_indices}

total_distance = 0
frame_count = 0

print("Processing and saving video...")

while True:
    success, img = cap.read()
    if not success:
        break
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    
    results = pose.detect_for_video(mp_image, frame_timestamp_ms)
    frame_timestamp_ms += 33
    
    # Get corresponding reference frame
    if frame_index < len(reference_poses):
        ref_pose = reference_poses[frame_index]
    else:
        ref_pose = None
    
    frame_index += 1
    
    if results.pose_landmarks and ref_pose:
        comp_pose = results.pose_landmarks[0]
        
        # Calculate weighted distance
        distance = weighted_distance(comp_pose, ref_pose)
        total_distance += distance
        frame_count += 1
        
        # Threshold for good match (per landmark)
        landmark_threshold = 0.05
        
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        for idx in selected_indices:
            if idx < len(comp_pose):
                lm = comp_pose[idx]
                pose_landmarks_proto.landmark.append(
                    landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                )
        
        for id, im in enumerate(pose_landmarks_proto.landmark):
            h, w, c = img.shape
            cx, cy = int(im.x * w), int(im.y * h)
            
            # Calculate distance for this specific landmark
            actual_idx = selected_indices[id]
            if actual_idx < len(comp_pose) and actual_idx < len(ref_pose):
                comp_lm = comp_pose[actual_idx]
                ref_lm = ref_pose[actual_idx]
                
                dx = comp_lm.x - ref_lm.x
                dy = comp_lm.y - ref_lm.y
                landmark_distance = math.sqrt(dx*dx + dy*dy)
                
                # Green if this landmark matches, Red if off
                is_correct = landmark_distance < landmark_threshold
                color = (0, 255, 0) if is_correct else (0, 0, 255)
                
                # Track correct frames
                if is_correct:
                    landmark_correct_frames[actual_idx] += 1
            else:
                color = (0, 0, 255)  # Red if landmark missing
            
            if id == 0:
                cv2.rectangle(img, (cx - 40, cy - 40), (cx + 40, cy + 40), color)
            elif id == 5 or id == 6:
                cv2.rectangle(img, (cx - 22, cy - 22), (cx + 22, cy + 22), color)
            else:
                cv2.rectangle(img, (cx - 12, cy - 12), (cx + 12, cy + 12), color)
    
    # Write frame to output video
    out.write(img)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

cap.release()
out.release()
print(f"Video saved as matas_analyzed.mp4")

# Generate statistics and bar chart
perfect_frames = len(reference_poses)
labels = [landmark_names[idx] for idx in selected_indices]
correct_counts = [landmark_correct_frames[idx] for idx in selected_indices]

# Calculate overall score
total_possible = perfect_frames * len(selected_indices)
total_correct = sum(correct_counts)
overall_score = (total_correct / total_possible) * 100

# Create bar chart
fig, ax = plt.subplots(figsize=(14, 8))
bars = ax.bar(labels, correct_counts, color='#4CAF50', edgecolor='black', linewidth=1.5)

# Add perfect frame line
ax.axhline(y=perfect_frames, color='red', linestyle='--', linewidth=2, label=f'Perfect (Nika): {perfect_frames} frames')

# Styling
ax.set_xlabel('Body Parts', fontsize=14, fontweight='bold')
ax.set_ylabel('Correct Frames (Green)', fontsize=14, fontweight='bold')
ax.set_title(f'Pose Accuracy Analysis: Matas vs Nika\nOverall Score: {overall_score:.2f}%', 
             fontsize=16, fontweight='bold')
ax.set_ylim(0, perfect_frames + 20)
ax.legend(fontsize=12)
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('C:\\Users\\Gaming\\Desktop\\UDULUS\\pose_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

