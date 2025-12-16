import 'reflect-metadata';

// Log Node.js version and environment info for debugging
console.log('=== Node.js Environment Info ===');
console.log('🔍 Node.js version:', process.version);
console.log('🔍 Node.js major version:', process.version.split('.')[0].slice(1));
console.log('🔍 NODE_OPTIONS:', process.env.NODE_OPTIONS || '(not set)');
console.log('🔍 Platform:', process.platform);
console.log('🔍 Architecture:', process.arch);
console.log('================================');

// Check if .platform/nodejs/configuration.yml is being applied
// Expected: Node.js 18.x if configuration.yml is working
const nodeMajorVersion = parseInt(process.version.split('.')[0].slice(1));
if (nodeMajorVersion === 18) {
  console.log('✅ Node.js 18 detected - .platform/nodejs/configuration.yml appears to be working!');
} else if (nodeMajorVersion === 22) {
  console.warn('⚠️  Node.js 22 detected - .platform/nodejs/configuration.yml may not be applied!');
  console.warn('⚠️  Check AWS EB Platform Configuration to ensure Node.js 18 is selected.');
} else {
  console.log(`ℹ️  Node.js ${nodeMajorVersion} detected`);
}
import express, { Application } from 'express';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';
import path from 'path';
import { AppDataSource } from './data-source';
import authRoutes from './modules/auth/auth.routes';
import videoRoutes from './modules/videos/videos.routes';
import userVideosRoutes from './modules/videos/user-videos.routes';
import learningTreesRoutes from './modules/learning_trees/learning-trees.routes';
import learningTreeNodesRoutes from './modules/learning_trees/learning-tree-nodes.routes';

const app: Application = express();
const PORT = parseInt(process.env.PORT || '3000', 10);

// Configure body parser with 500MB limit
const BODY_LIMIT = '500mb';
console.log('=== Configuring Express Body Parser ===');
console.log('JSON body limit:', BODY_LIMIT);
console.log('URL-encoded body limit:', BODY_LIMIT);
console.log('========================================');

app.use(express.json({ limit: BODY_LIMIT }));
app.use(express.urlencoded({ extended: true, limit: BODY_LIMIT }));

// Load OpenAPI specification
const openapiDocument = YAML.load(path.join(__dirname, '../openapi.yml'));

// API Documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openapiDocument));

// Health check endpoint for Elastic Beanstalk
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    message: 'Server is running',
    timestamp: new Date().toISOString()
  });
});

// Register module routes
app.use('/api/auth', authRoutes);
app.use('/api/videos', videoRoutes);
app.use('/api/user-videos', userVideosRoutes);
app.use('/api/learning-trees', learningTreesRoutes);
app.use('/api/learning-tree-nodes', learningTreeNodesRoutes);

// Global error handler (must be after all routes)
app.use((err: any, req: any, res: any, next: any) => {
  console.error('=== Global Error Handler ===');
  console.error('Error:', err);
  console.error('Stack:', err.stack);
  console.error('========================');
  
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV !== 'production' && { stack: err.stack })
  });
});

let server: any;

// Graceful shutdown handling
const gracefulShutdown = async (signal: string) => {
  console.log(`\n${signal} received. Starting graceful shutdown...`);
  
  if (server) {
    server.close(() => {
      console.log('HTTP server closed');
    });
  }
  
  if (AppDataSource.isInitialized) {
    await AppDataSource.destroy();
    console.log('Database connection closed');
  }
  
  process.exit(0);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start server first (so health checks work even if DB fails)
server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server is running on port ${PORT}`);
  console.log(`📚 API Documentation available at http://localhost:${PORT}/api-docs`);
  
  // Initialize database after server starts
  AppDataSource.initialize()
    .then(() => {
      console.log('✅ Database connection established');
    })
    .catch((error: Error) => {
      console.error('❌ Error during Data Source initialization:', error);
      console.error('⚠️  Server is running but database is not connected');
      // Don't exit - let health checks pass while you fix DB config
    });
});
