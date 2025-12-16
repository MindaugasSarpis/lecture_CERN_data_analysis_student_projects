import { Router } from 'express';
import { VideoController } from './controllers/video.controller';

const router = Router();
const videoController = new VideoController();

// GET /api/user-videos
router.get('/', (req, res) => videoController.listUserVideos(req, res));

// GET /api/user-videos/:uuid
router.get('/:uuid', (req, res) => videoController.getUserVideo(req, res));

// PUT /api/user-videos/:uuid
router.put('/:uuid', (req, res) => videoController.updateUserVideo(req, res));

// DELETE /api/user-videos/:uuid
router.delete('/:uuid', (req, res) => videoController.deleteUserVideo(req, res));

export default router;
