# Google Cloud Storage Service - Minimal MP4 Video Management

This module provides a minimal Google Cloud Storage client for MP4 video upload and retrieval.

## Features

- Upload MP4 video files to Google Cloud Storage (always private)
- Download MP4 video files from Google Cloud Storage  
- Generate signed URLs for secure MP4 video streaming
- Strict MP4-only format validation
- All videos are kept private by default - access via signed URLs only
- Minimal API focused on essential video operations only

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables in your `.env` file:
```env
GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
GOOGLE_CLOUD_BUCKET_NAME=your-mp4-video-bucket-name
GOOGLE_CLOUD_KEY_FILE=path/to/service-account-key.json  # Optional
```

## Authentication

The service supports two authentication methods:

1. **Service Account Key File**: Provide the path to your service account JSON file via `GOOGLE_CLOUD_KEY_FILE`
2. **Application Default Credentials**: If no key file is specified, the service will use Google Cloud's default credential discovery

## Usage

```typescript
import { googleCloudService } from './modules/config';
import fs from 'fs';

// Upload an MP4 video file
const videoBuffer = fs.readFileSync('path/to/video.mp4');
const videoUrl = await googleCloudService.uploadVideo('videos/user-123/video-456.mp4', videoBuffer, {
  userId: '123',
  originalName: 'my-awesome-video.mp4',
  metadata: {
    description: 'User uploaded MP4 video',
    category: 'personal'
  }
});

// Generate an MP4 video streaming URL (24 hours by default)
const streamingUrl = await googleCloudService.getVideoStreamingUrl('videos/user-123/video.mp4');

// Generate streaming URL with custom expiration (48 hours)
const longStreamingUrl = await googleCloudService.getVideoStreamingUrl('videos/user-123/video.mp4', 48);

// Download an MP4 video file
const downloadedVideo = await googleCloudService.downloadVideo('videos/user-123/video.mp4');
```

## MP4 Video-Specific Features

### Supported Video Format
- **MP4 only** (video/mp4) - Strict validation enforced
- Files must have `.mp4` extension
- Automatic content-type detection
- Format validation on upload and streaming URL generation

### Best Practices for MP4 Video Storage

1. **File Organization**: Use a structured folder hierarchy:
   ```
   videos/
   ├── user-{userId}/
   │   └── {videoId}.mp4
   ```

2. **File Naming**: Always use `.mp4` extension (case-insensitive)

3. **Security**: MP4 videos are always kept private. Use signed URLs for controlled access.

4. **Streaming**: Generated signed URLs work directly with HTML5 video players for MP4 playback.

5. **Metadata**: Include relevant metadata when uploading:
   - User ID
   - Upload date
   - Original filename
   - Video description/category

### Minimal API
Only essential operations are available:
- **Upload**: Store MP4 videos securely
- **Download**: Retrieve MP4 video files as buffers
- **Stream**: Generate temporary access URLs for playback

### Format Validation
The service automatically validates that:
- File names end with `.mp4` (case-insensitive)
- Content-type is set to `video/mp4`
- All videos are kept private (no public access)
- Throws descriptive errors for unsupported formats

## Error Handling

All methods include proper error handling and will throw descriptive errors if operations fail. Make sure to wrap calls in try-catch blocks.
