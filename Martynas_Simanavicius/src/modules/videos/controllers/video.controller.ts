import { Request, Response } from 'express';
import multer from 'multer';
import { UploadVideoService } from '../domain/upload-video.service';
import { GetVideoStreamUrlService } from '../domain/get-video-stream-url.service';
import { GetUserVideoService } from '../domain/get-user-video.service';
import { ListUserVideosService } from '../domain/list-user-videos.service';
import { UpdateUserVideoService } from '../domain/update-user-video.service';
import { DeleteUserVideoService } from '../domain/delete-user-video.service';
import { BaseError, ValidationError } from '../../../errors';

// Extend Request interface to include file property
interface RequestWithFile extends Request {
  file?: Express.Multer.File;
}

// Configure multer for memory storage (we'll upload directly to Google Cloud)
const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB max file size

console.log('=== Configuring Multer Video Upload ===');
console.log('Max file size:', MAX_FILE_SIZE, 'bytes');
console.log('Max file size:', (MAX_FILE_SIZE / 1024 / 1024).toFixed(0), 'MB');
console.log('Storage: Memory');
console.log('Allowed formats: MP4');
console.log('========================================');

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: MAX_FILE_SIZE,
  },
  fileFilter: (req: any, file: any, cb: any) => {
    // Only allow MP4 files
    if (file.mimetype === 'video/mp4' || file.originalname.toLowerCase().endsWith('.mp4')) {
      cb(null, true);
    } else {
      cb(new Error('Only MP4 video files are allowed'));
    }
  },
});

export class VideoController {
  // Multer middleware for single video upload
  public uploadMiddleware = upload.single('video');

  async uploadVideo(req: RequestWithFile, res: Response): Promise<void> {
    try {
      // Check if file was uploaded
      if (!req.file) {
        res.status(400).json({
          error: 'No video file provided. Please upload an MP4 file.',
        });
        return;
      }

      // For now, we'll use a mock userId. In real app, this would come from JWT token
      const userId = req.body.userId || '1'; // TODO: Get from authenticated user

      // Upload video using the service
      const uploadVideoService = new UploadVideoService();
      const result = await uploadVideoService.run({
        fileName: req.file.originalname,
        fileBuffer: req.file.buffer,
        userId,
        originalName: req.file.originalname,
      });

      // Return success response
      res.status(201).json({
        success: true,
        data: result,
      });
    } catch (error) {
      console.error('Error uploading video:', error);
      
      // Handle specific multer errors
      if (error instanceof multer.MulterError) {
        if ((error as any).code === 'LIMIT_FILE_SIZE') {
          res.status(400).json({
            error: 'File too large. Maximum size is 500MB.',
          });
          return;
        }
      }

      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to upload video',
      });
    }
  }

  async getStreamingUrl(req: Request, res: Response): Promise<void> {
    try {
      const { fileName } = req.params;
      const { expirationHours } = req.query;

      // Validate required parameters
      if (!fileName) {
        res.status(400).json({
          error: 'fileName parameter is required',
        });
        return;
      }

      // Parse expiration hours
      const expiration = expirationHours ? parseInt(expirationHours as string) : 24;

      // Get streaming URL using the service
      const getStreamUrlService = new GetVideoStreamUrlService();
      const result = await getStreamUrlService.run({
        fileName,
        expirationHours: expiration,
      });

      // Return success response
      res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error) {
      console.error('Error generating streaming URL:', error);
      
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to generate streaming URL',
      });
    }
  }

  async getUserVideo(req: Request, res: Response): Promise<void> {
    try {
      const { uuid } = req.params;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      const getUserVideoService = new GetUserVideoService();
      const userVideo = await getUserVideoService.run(uuid);

      res.status(200).json({
        uuid: userVideo.uuid,
        user_id: userVideo.user_id,
        learning_tree_node_id: userVideo.learning_tree_node_id,
        video_file_name: userVideo.video_file_name,
        createdAt: userVideo.createdAt,
        updatedAt: userVideo.updatedAt,
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async listUserVideos(req: Request, res: Response): Promise<void> {
    try {
      const { user_id, learning_tree_node_id } = req.query;

      const filters: any = {};
      if (user_id) {
        filters.user_id = parseInt(user_id as string, 10);
      }
      if (learning_tree_node_id) {
        filters.learning_tree_node_id = parseInt(learning_tree_node_id as string, 10);
      }

      const listUserVideosService = new ListUserVideosService();
      const userVideos = await listUserVideosService.run(
        Object.keys(filters).length > 0 ? filters : undefined
      );

      res.status(200).json(
        userVideos.map((video) => ({
          uuid: video.uuid,
          user_id: video.user_id,
          learning_tree_node_id: video.learning_tree_node_id,
          video_file_name: video.video_file_name,
          createdAt: video.createdAt,
          updatedAt: video.updatedAt,
        }))
      );
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async updateUserVideo(req: Request, res: Response): Promise<void> {
    try {
      const { uuid } = req.params;
      const { video_file_name, learning_tree_node_id } = req.body;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      const updateUserVideoService = new UpdateUserVideoService();
      const userVideo = await updateUserVideoService.run(uuid, {
        video_file_name,
        learning_tree_node_id,
      });

      res.status(200).json({
        uuid: userVideo.uuid,
        user_id: userVideo.user_id,
        learning_tree_node_id: userVideo.learning_tree_node_id,
        video_file_name: userVideo.video_file_name,
        createdAt: userVideo.createdAt,
        updatedAt: userVideo.updatedAt,
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async deleteUserVideo(req: Request, res: Response): Promise<void> {
    try {
      const { uuid } = req.params;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      const deleteUserVideoService = new DeleteUserVideoService();
      await deleteUserVideoService.run(uuid);

      res.status(200).json({
        message: 'User video deleted successfully',
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}
