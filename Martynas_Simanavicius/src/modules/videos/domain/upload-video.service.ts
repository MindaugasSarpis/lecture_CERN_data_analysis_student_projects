import { googleCloudService } from '../../config/google-cloud-service';

export interface UploadVideoInput {
  fileName: string;
  fileBuffer: Buffer;
  userId?: string; // Made optional since it's not used for upload metadata
  originalName?: string; // Made optional since it's not used for upload metadata
}

export interface UploadVideoOutput {
  videoUrl: string;
  fileName: string;
  message: string;
}

export class UploadVideoService {
  async run(input: UploadVideoInput): Promise<UploadVideoOutput> {
    // Validate MP4 file
    if (!input.fileName.toLowerCase().endsWith('.mp4')) {
      throw new Error('Only MP4 video files are supported');
    }

    // Generate unique file path
    const timestamp = Date.now();
    const fileName = `${timestamp}-${input.fileName}`;

    try {
      // Upload video to Google Cloud Storage
      const videoUrl = await googleCloudService.uploadVideo(fileName, input.fileBuffer);

      return {
        videoUrl,
        fileName,
        message: 'Video uploaded successfully',
      };
    } catch (error) {
      console.error('Error uploading video:', error);
      throw new Error(`Failed to upload video: ${error}`);
    }
  }
}
