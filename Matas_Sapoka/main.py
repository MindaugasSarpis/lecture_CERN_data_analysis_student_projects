from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import cv2
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import os
import shutil
import tempfile
from pathlib import Path

app = FastAPI(title="Pose Analysis API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MODEL_PATH = 'pose_landmarker_lite.task'
REFERENCE_VIDEO = 'nika.mp4'
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Pose comparison functions
def weighted_distance(landmarks1, landmarks2):
    """Weighted distance using confidence scores"""
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

# Initialize pose detector
options = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    min_pose_detection_confidence=0.3,
    min_pose_presence_confidence=0.3,
    min_tracking_confidence=0.3)

pose = vision.PoseLandmarker.create_from_options(options)

# Load reference video once at startup
print("Loading reference video...")
reference_poses = []
ref_cap = cv2.VideoCapture(REFERENCE_VIDEO)
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

selected_indices = [0, 11, 12, 13, 14, 19, 20, 26, 23, 24, 25, 30, 29]

landmark_names = {
    0: 'Nose', 11: 'L_Shoulder', 12: 'R_Shoulder', 
    13: 'L_Elbow', 14: 'R_Elbow', 19: 'L_Index', 20: 'R_Index',
    23: 'L_Hip', 24: 'R_Hip', 25: 'L_Knee', 
    26: 'R_Knee', 29: 'L_Heel', 30: 'R_Heel'
}

@app.get("/")
def root():
    return {
        "message": "Pose Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Upload video for pose analysis",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "reference_frames": len(reference_poses)}

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze uploaded video against reference (Nika)
    Returns: analyzed video, statistics chart, and JSON results
    """
    if not file.filename.endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Only video files (.mp4, .avi, .mov) are supported")
    
    # Save uploaded file
    temp_input = UPLOAD_DIR / f"temp_{file.filename}"
    with open(temp_input, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Create a new PoseLandmarker instance for this video to avoid timestamp state issues
        video_pose = vision.PoseLandmarker.create_from_options(options)
        
        # Process video
        cap = cv2.VideoCapture(str(temp_input))
        
        # Get video properties
        fps_out = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Check for rotation metadata
        rotation = int(cap.get(cv2.CAP_PROP_ORIENTATION_META))
        
        # Adjust dimensions if video is rotated 90 or 270 degrees
        if rotation in [90, 270]:
            width, height = height, width
        
        output_video = OUTPUT_DIR / f"analyzed_{file.filename}"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_video), fourcc, fps_out, (width, height))
        
        frame_timestamp_ms = 0
        frame_index = 0
        landmark_correct_frames = {idx: 0 for idx in selected_indices}
        landmark_threshold = 0.05
        
        while True:
            success, img = cap.read()
            if not success:
                break
            
            # Apply rotation correction if needed
            if rotation == 90:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif rotation == 180:
                img = cv2.rotate(img, cv2.ROTATE_180)
            elif rotation == 270:
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
            
            results = video_pose.detect_for_video(mp_image, frame_timestamp_ms)
            frame_timestamp_ms += 33
            
            if frame_index < len(reference_poses):
                ref_pose = reference_poses[frame_index]
            else:
                ref_pose = None
            
            frame_index += 1
            
            if results.pose_landmarks and ref_pose:
                comp_pose = results.pose_landmarks[0]
                
                # Calculate weighted distance for entire pose
                pose_distance = weighted_distance(comp_pose, ref_pose)
                
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
                    
                    actual_idx = selected_indices[id]
                    if actual_idx < len(comp_pose) and actual_idx < len(ref_pose):
                        comp_lm = comp_pose[actual_idx]
                        ref_lm = ref_pose[actual_idx]
                        
                        # Per-landmark Euclidean distance
                        dx = comp_lm.x - ref_lm.x
                        dy = comp_lm.y - ref_lm.y
                        landmark_distance = math.sqrt(dx*dx + dy*dy)
                        
                        is_correct = landmark_distance < landmark_threshold
                        color = (0, 255, 0) if is_correct else (0, 0, 255)
                        
                        if is_correct:
                            landmark_correct_frames[actual_idx] += 1
                    else:
                        color = (0, 0, 255)
                    
                    if id == 0:
                        cv2.rectangle(img, (cx - 40, cy - 40), (cx + 40, cy + 40), color, 2)
                    elif id == 5 or id == 6:
                        cv2.rectangle(img, (cx - 22, cy - 22), (cx + 22, cy + 22), color, 2)
                    else:
                        cv2.rectangle(img, (cx - 12, cy - 12), (cx + 12, cy + 12), color, 2)
            
            out.write(img)
        
        cap.release()
        out.release()
        
        # Generate statistics
        perfect_frames = len(reference_poses)
        labels = [landmark_names[idx] for idx in selected_indices]
        correct_counts = [landmark_correct_frames[idx] for idx in selected_indices]
        
        total_possible = perfect_frames * len(selected_indices)
        total_correct = sum(correct_counts)
        overall_score = (total_correct / total_possible) * 100
        
        # Create bar chart
        output_chart = OUTPUT_DIR / f"chart_{file.filename.replace('.mp4', '.png')}"
        fig, ax = plt.subplots(figsize=(14, 8))
        bars = ax.bar(labels, correct_counts, color='#4CAF50', edgecolor='black', linewidth=1.5)
        
        ax.axhline(y=perfect_frames, color='red', linestyle='--', linewidth=2, 
                   label=f'Perfect (Reference): {perfect_frames} frames')
        
        ax.set_xlabel('Body Parts', fontsize=14, fontweight='bold')
        ax.set_ylabel('Correct Frames (Green)', fontsize=14, fontweight='bold')
        ax.set_title(f'Pose Accuracy Analysis\nOverall Score: {overall_score:.2f}%', 
                     fontsize=16, fontweight='bold')
        ax.set_ylim(0, perfect_frames + 20)
        ax.legend(fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        
        for bar, count in zip(bars, correct_counts):
            height = bar.get_height()
            percentage = (count / perfect_frames) * 100
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}\n({percentage:.1f}%)',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(str(output_chart), dpi=150, bbox_inches='tight')
        plt.close()
        
        # Prepare response
        per_landmark_stats = {}
        for idx in selected_indices:
            name = landmark_names[idx]
            correct = landmark_correct_frames[idx]
            percentage = (correct / perfect_frames) * 100
            per_landmark_stats[name] = {
                "correct_frames": correct,
                "total_frames": perfect_frames,
                "accuracy_percentage": round(percentage, 2)
            }
        
        return JSONResponse(content={
            "overall_score": round(overall_score, 2),
            "frames_analyzed": frame_index,
            "reference_frames": perfect_frames,
            "per_landmark_accuracy": per_landmark_stats,
            "analyzed_video": f"/download/video/{output_video.name}",
            "stream_video": f"/stream/video/{output_video.name}",
            "chart": f"/download/chart/{output_chart.name}"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
    
    finally:
        # Cleanup temp file
        if temp_input.exists():
            temp_input.unlink()

@app.get("/download/video/{filename}")
def download_video(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

@app.get("/download/chart/{filename}")
def download_chart(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(file_path, media_type="image/png", filename=filename)

@app.get("/stream/video/{filename}")
async def stream_video(filename: str, request: Request):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_size = file_path.stat().st_size
    range_header = request.headers.get('range')
    
    if range_header:
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        if start >= file_size or end >= file_size:
            raise HTTPException(status_code=416, detail="Range not satisfiable")
        
        chunk_size = end - start + 1
        
        def generate():
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = chunk_size
                while remaining:
                    chunk = f.read(min(8192, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Type': 'video/mp4',
        }
        return StreamingResponse(generate(), status_code=206, headers=headers)
    else:
        def generate():
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        headers = {
            'Accept-Ranges': 'bytes',
            'Content-Length': str(file_size),
            'Content-Type': 'video/mp4',
        }
        return StreamingResponse(generate(), headers=headers)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
