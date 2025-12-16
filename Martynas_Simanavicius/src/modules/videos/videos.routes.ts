import { Router } from 'express';
import { VideoController } from './controllers/video.controller';

const router = Router();
const videoController = new VideoController();

// POST /api/videos/upload - Upload a new MP4 video
router.post('/upload', videoController.uploadMiddleware, (req, res) => 
  videoController.uploadVideo(req, res)
);

// GET /api/videos/:fileName/stream - Get streaming URL for a video
router.get('/:fileName/stream', (req, res) => 
  videoController.getStreamingUrl(req, res)
);

export default router;
