import { googleCloudService } from '../../config/google-cloud-service';

export interface GetVideoStreamUrlInput {
  fileName: string;
  expirationHours?: number;
}

export interface GetVideoStreamUrlOutput {
  streamingUrl: string;
  expiresAt: Date;
  fileName: string;
}

export class GetVideoStreamUrlService {
  async run(input: GetVideoStreamUrlInput): Promise<GetVideoStreamUrlOutput> {
    // Validate input
    if (!input.fileName) {
      throw new Error('fileName is required');
    }

    // Validate MP4 file
    if (!input.fileName.toLowerCase().endsWith('.mp4')) {
      throw new Error('Only MP4 video files are supported');
    }

    const expirationHours = input.expirationHours || 24; // Default 24 hours

    try {
      // Generate streaming URL
      const streamingUrl = await googleCloudService.getVideoStreamingUrl(
        input.fileName,
        expirationHours
      );

      const expiresAt = new Date(Date.now() + expirationHours * 60 * 60 * 1000);

      return {
        streamingUrl,
        expiresAt,
        fileName: input.fileName,
      };
    } catch (error) {
      console.error('Error generating streaming URL:', error);
      throw new Error(`Failed to generate streaming URL: ${error}`);
    }
  }
}
