import { DataSource } from 'typeorm';
import * as dotenv from 'dotenv';

dotenv.config();

export const AppDataSource = new DataSource({
  // Use Postgres to match docker-compose service
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
  database: process.env.DB_DATABASE || 'main',
  synchronize: process.env.NODE_ENV !== 'production', // Disable in production, use migrations instead
  logging: process.env.NODE_ENV === 'development',
  entities: process.env.NODE_ENV === 'production' 
    ? ['dist/modules/**/models/*.entity.js']
    : ['src/modules/**/models/*.entity.ts'],
  migrations: process.env.NODE_ENV === 'production'
    ? ['dist/migrations/*.js']
    : ['src/migrations/*.ts'],
  subscribers: [],
});

