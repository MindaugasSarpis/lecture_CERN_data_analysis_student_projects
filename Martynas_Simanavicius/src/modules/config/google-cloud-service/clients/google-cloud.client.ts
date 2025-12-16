import { Storage, Bucket } from '@google-cloud/storage';
import * as dotenv from 'dotenv';

dotenv.config();

export interface GoogleCloudConfig {
  projectId: string;
  credentials?: any;
  bucketName: string;
}

export class GoogleCloudService {
  private storage: Storage;
  private bucket: Bucket;
  private config: GoogleCloudConfig;

  constructor() {
    console.log('=== Initializing GoogleCloudService ===');
    
    this.config = {
      projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
      credentials: this.getCredentials(),
      bucketName: process.env.GOOGLE_CLOUD_BUCKET_NAME || '',
    };

    this.validateConfig();
    this.initializeStorage();
    
    console.log('✅ GoogleCloudService initialized successfully');
    console.log('=======================================');
  }

  private getCredentials(): any {
    // Priority 1: Individual credentials from environment variables (email + private key)
    // This is preferred for AWS environments as it's easier to manage in environment variables
    const clientEmail = process.env.GOOGLE_CLOUD_CLIENT_EMAIL;
    const privateKey = process.env.GOOGLE_CLOUD_PRIVATE_KEY;
    
    if (clientEmail && privateKey) {
      console.log('🔑 Found individual GOOGLE_CLOUD credentials (email + key)');
      let formattedKey = privateKey;
      
      // Fix private key formatting for AWS OpenSSL compatibility
      // Case 1: Replace escaped newlines (\n as literal string)
      if (formattedKey.includes('\\n')) {
        formattedKey = formattedKey.replace(/\\n/g, '\n');
        console.log('🔧 Fixed escaped newlines in private key');
      }
      
      // Normalize line endings (handle Windows/Unix/Mac differences)
      formattedKey = formattedKey.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      
      // Ensure proper PEM format - must start with BEGIN and end with END
      if (!formattedKey.includes('-----BEGIN')) {
        console.warn('⚠️  Private key may not be in PEM format');
      }
      
      // Remove excessive newlines but preserve structure
      formattedKey = formattedKey.replace(/\n{3,}/g, '\n\n');
      
      // Critical: Ensure proper PEM format with correct line breaks
      // Split by lines and clean up
      const lines = formattedKey.split('\n');
      const cleanedLines: string[] = [];
      let inKeyContent = false;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Skip completely empty lines
        if (line.length === 0 && !inKeyContent) {
          continue;
        }
        
        // Handle BEGIN marker
        if (line.startsWith('-----BEGIN')) {
          cleanedLines.push(line);
          inKeyContent = true;
          continue;
        }
        
        // Handle END marker
        if (line.startsWith('-----END')) {
          cleanedLines.push(line);
          inKeyContent = false;
          continue;
        }
        
        // Handle key content (base64)
        if (inKeyContent && line.length > 0) {
          // Remove any spaces from base64 content (shouldn't have spaces)
          const cleanedLine = line.replace(/\s/g, '');
          if (cleanedLine.length > 0) {
            cleanedLines.push(cleanedLine);
          }
        }
      }
      
      formattedKey = cleanedLines.join('\n');
      
      // Ensure key ends with a single newline (required for OpenSSL compatibility)
      formattedKey = formattedKey.trimEnd() + '\n';
      
      // Validate the key format
      const hasBegin = formattedKey.includes('-----BEGIN');
      const hasEnd = formattedKey.includes('-----END');
      const beginMatch = formattedKey.match(/-----BEGIN[^-]+-----/);
      const endMatch = formattedKey.match(/-----END[^-]+-----/);
      
      if (!hasBegin || !hasEnd || !beginMatch || !endMatch) {
        throw new Error('Invalid private key format: Missing BEGIN or END markers');
      }
      
      // Extract key content between markers
      const beginIndex = formattedKey.indexOf(beginMatch[0]) + beginMatch[0].length;
      const endIndex = formattedKey.indexOf(endMatch[0]);
      const keyContent = formattedKey.substring(beginIndex, endIndex).trim();
      
      if (keyContent.length === 0) {
        throw new Error('Invalid private key format: Empty key content');
      }
      
      console.log('✅ Private key format processed and validated for AWS OpenSSL compatibility');
      const keyType = formattedKey.includes('PRIVATE KEY') ? 'PKCS#8' : 
                     formattedKey.includes('RSA PRIVATE KEY') ? 'PKCS#1' : 'Unknown';
      console.log('📝 Key type detected:', keyType);
      console.log('📏 Key content length:', keyContent.length, 'characters');
      
      // Return full credentials object structure (required by Google Auth library)
      // Note: Use process.env directly since this.config is not yet initialized when getCredentials() is called
      return {
        type: 'service_account',
        project_id: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
        private_key_id: '', // Not required when using individual credentials
        private_key: formattedKey,
        client_email: clientEmail,
        client_id: '', // Not required when using individual credentials
        auth_uri: 'https://accounts.google.com/o/oauth2/auth',
        token_uri: 'https://oauth2.googleapis.com/token',
        auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
        client_x509_cert_url: '', // Not required for basic authentication
      };
    }
    
    // Priority 2: Full JSON credentials from environment variable (fallback)
    const credentialsJson = process.env.GOOGLE_CLOUD_CREDENTIALS;
    if (credentialsJson) {
      try {
        console.log('🔑 Found GOOGLE_CLOUD_CREDENTIALS JSON environment variable');
        const credentials = JSON.parse(credentialsJson);
        
        // Fix private key formatting - Case 1: Replace escaped newlines
        if (credentials.private_key) {
          let privateKey = credentials.private_key;
          
          // Case 1: Literal \n as two characters - replace with actual newlines
          if (privateKey.includes('\\n')) {
            privateKey = privateKey.replace(/\\n/g, '\n');
            console.log('🔧 Fixed escaped newlines in private key');
          }
          
          // Normalize line endings and ensure proper formatting
          privateKey = privateKey.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
          
          // Apply the same formatting logic as individual credentials
          const lines = privateKey.split('\n');
          const cleanedLines: string[] = [];
          let inKeyContent = false;
          
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (line.length === 0 && !inKeyContent) {
              continue;
            }
            
            if (line.startsWith('-----BEGIN')) {
              cleanedLines.push(line);
              inKeyContent = true;
              continue;
            }
            
            if (line.startsWith('-----END')) {
              cleanedLines.push(line);
              inKeyContent = false;
              continue;
            }
            
            if (inKeyContent && line.length > 0) {
              const cleanedLine = line.replace(/\s/g, '');
              if (cleanedLine.length > 0) {
                cleanedLines.push(cleanedLine);
              }
            }
          }
          
          privateKey = cleanedLines.join('\n');
          privateKey = privateKey.trimEnd() + '\n';
          
          credentials.private_key = privateKey;
          console.log('✅ Private key format processed for AWS OpenSSL compatibility');
        }
        
        return credentials;
      } catch (error) {
        console.error('Failed to parse GOOGLE_CLOUD_CREDENTIALS:', error);
        throw new Error(`Invalid GOOGLE_CLOUD_CREDENTIALS format: ${error}`);
      }
    }
    
    // Priority 3: Legacy file path support (for local development only)
    const keyFile = process.env.GOOGLE_CLOUD_KEY_FILE;
    if (keyFile) {
      console.warn('⚠️  GOOGLE_CLOUD_KEY_FILE is deprecated. Use GOOGLE_CLOUD_CREDENTIALS instead.');
      console.log('🔑 Attempting to use key file:', keyFile);
      // Return null to let Google Cloud SDK try to load the file
      // This will fail in production but work locally
      return null;
    }
    
    console.log('🔑 No credentials found, will try Application Default Credentials (ADC)');
    return null;
  }

  private validateConfig(): void {
    console.log('🔍 Validating Google Cloud config:');
    console.log('Project ID:', this.config.projectId);
    console.log('Bucket Name:', this.config.bucketName);
    console.log('Has Credentials:', !!this.config.credentials);
    
    if (!this.config.projectId) {
      throw new Error('GOOGLE_CLOUD_PROJECT_ID is required');
    }
    
    if (!this.config.bucketName) {
      throw new Error('GOOGLE_CLOUD_BUCKET_NAME is required');
    }

    if (this.config.credentials) {
      console.log('✅ Using Service Account Credentials from environment variables');
    } else {
      console.log('⚠️  No credentials configured. Attempting Application Default Credentials (ADC)');
    }
  }

  private initializeStorage(): void {
    try {
      const storageConfig: any = {
        projectId: this.config.projectId,
      };

      if (this.config.credentials) {
        console.log('🔑 Initializing Storage with credentials object');
        console.log('📋 Credentials structure:', {
          hasClientEmail: !!this.config.credentials.client_email,
          hasPrivateKey: !!this.config.credentials.private_key,
          privateKeyLength: this.config.credentials.private_key?.length || 0,
          privateKeyPreview: this.config.credentials.private_key?.substring(0, 50) + '...',
        });
        
        // Use credentials directly (already in correct format from getCredentials)
        storageConfig.credentials = this.config.credentials;
      } else {
        // Try file path or ADC
        const keyFile = process.env.GOOGLE_CLOUD_KEY_FILE;
        if (keyFile) {
          console.log('🔑 Initializing Storage with keyFilename:', keyFile);
          storageConfig.keyFilename = keyFile;
        } else {
          console.log('🔑 Initializing Storage with Application Default Credentials');
        }
      }

      // Note: SSL/TLS compatibility is handled via NODE_OPTIONS=--openssl-legacy-provider
      // Custom HTTP agents are not supported by the Google Cloud Storage SDK constructor
      // The SDK uses its own HTTP client internally which respects NODE_OPTIONS
      console.log('🔒 SSL/TLS compatibility relies on NODE_OPTIONS environment variable');
      console.log('🔍 NODE_OPTIONS:', process.env.NODE_OPTIONS || 'not set');

      this.storage = new Storage(storageConfig);
      this.bucket = this.storage.bucket(this.config.bucketName);
      
      console.log('✅ Storage client initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize Google Cloud Storage:', error);
      if (error instanceof Error) {
        console.error('❌ Error message:', error.message);
        console.error('❌ Error stack:', error.stack);
      }
      throw new Error(`Failed to initialize Google Cloud Storage: ${error}`);
    }
  }

  /**
   * Download an MP4 video file from Google Cloud Storage
   */
  async downloadVideo(fileName: string): Promise<Buffer> {
    try {
      // Validate MP4 format
      this.validateMp4File(fileName);
      
      const file = this.bucket.file(fileName);
      const [fileBuffer] = await file.download();
      return fileBuffer;
    } catch (error) {
      console.error('Error downloading MP4 video from Google Cloud Storage:', error);
      throw new Error(`Failed to download MP4 video: ${error}`);
    }
  }

  /**
   * Validate that the file is an MP4 video
   */
  private validateMp4File(fileName: string): void {
    if (!fileName.toLowerCase().endsWith('.mp4')) {
      throw new Error('Only MP4 video files are supported. Please upload a .mp4 file.');
    }
  }

  /**
   * Upload an MP4 video file with optimized settings
   */
  async uploadVideo(fileName: string, videoBuffer: Buffer, options?: {
    userId?: string;
    originalName?: string;
    metadata?: { [key: string]: string };
  }): Promise<string> {
    try {
      // Validate MP4 format
      this.validateMp4File(fileName);
      
      const file = this.bucket.file(fileName);
      const metadata = {
        ...options?.metadata,
        uploadDate: new Date().toISOString(),
        fileType: 'video',
        format: 'mp4',
        ...(options?.userId && { userId: options.userId }),
        ...(options?.originalName && { originalName: options.originalName })
      };
      
      const uploadOptions: any = {
        resumable: false,
        metadata: {
          contentType: 'video/mp4',
          metadata: metadata,
        },
      };

      await file.save(videoBuffer, uploadOptions);

      return `gs://${this.config.bucketName}/${fileName}`;
    } catch (error) {
      console.error('Error uploading MP4 video to Google Cloud Storage:', error);
      throw new Error(`Failed to upload MP4 video: ${error}`);
    }
  }

  /**
   * Generate a streaming URL for MP4 video with extended expiration
   */
  async getVideoStreamingUrl(fileName: string, expirationHours: number = 24): Promise<string> {
    try {
      // Validate MP4 format
      this.validateMp4File(fileName);
      
      const file = this.bucket.file(fileName);
      const expires = new Date(Date.now() + expirationHours * 60 * 60 * 1000);
      
      const signedUrlOptions = {
        version: 'v4' as const,
        action: 'read' as const,
        expires: expires,
      };

      const [signedUrl] = await file.getSignedUrl(signedUrlOptions);
      return signedUrl;
    } catch (error) {
      console.error('Error generating MP4 video streaming URL:', error);
      throw new Error(`Failed to generate MP4 video streaming URL: ${error}`);
    }
  }
}

// Export a singleton instance
export const googleCloudService = new GoogleCloudService();
