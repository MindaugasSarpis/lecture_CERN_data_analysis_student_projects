# Pose Analysis API

FastAPI-based pose analysis service that compares uploaded videos against a reference video (Nika) using MediaPipe pose detection and Move Mirror algorithms.

## Features

- Video upload and pose comparison
- Per-landmark accuracy tracking
- Weighted distance matching algorithm
- Automated video analysis output with color-coded landmarks (green = correct, red = incorrect)
- Statistical analysis with matplotlib bar charts
- RESTful API for easy integration

## Installation

```bash
# Create conda environment
conda create -n udulus python=3.11.9
conda activate udulus

# Install dependencies
pip install -r requirements.txt
```

## Running Locally

```bash
uvicorn main:app --reload
```

API will be available at: `http://localhost:8000`

## API Endpoints

### `GET /`
Returns API information and available endpoints

### `GET /health`
Health check endpoint - returns status and reference frame count

### `POST /analyze`
Upload a video for pose analysis

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (video file - .mp4, .avi, .mov)

**Response:**
```json
{
  "overall_score": 85.5,
  "frames_analyzed": 150,
  "reference_frames": 150,
  "per_landmark_accuracy": {
    "Nose": {
      "correct_frames": 145,
      "total_frames": 150,
      "accuracy_percentage": 96.67
    },
    ...
  },
  "analyzed_video": "/download/video/analyzed_video.mp4",
  "chart": "/download/chart/chart_video.png"
}
```

### `GET /download/video/{filename}`
Download the analyzed video with color-coded pose landmarks

### `GET /download/chart/{filename}`
Download the accuracy analysis bar chart

## Railway Deployment

1. Push code to GitHub
2. Connect Railway to your repository
3. Ensure `nika.mp4` and `pose_landmarker_lite.task` are included
4. Railway will automatically detect and deploy using `railway.json` configuration

## Configuration

- **Reference Video**: `nika.mp4` (loaded at startup)
- **Model**: `pose_landmarker_lite.task`
- **Landmark Threshold**: 0.05 (per-landmark matching)
- **Selected Body Parts**: Nose, Shoulders, Elbows, Hands, Hips, Knees, Heels

## Algorithm

Uses weighted distance matching from Google's Move Mirror:
- Normalizes pose landmarks
- Applies confidence-weighted distance calculation
- Per-landmark color coding (green = match within threshold, red = exceeds threshold)
- Overall accuracy: (correct_frames / total_possible) × 100

## Requirements

- Python 3.11.9
- MediaPipe 0.10.14
- OpenCV 4.10.0.84
- FastAPI 0.115.6
- NumPy 1.26.4
- Matplotlib 3.9.3
