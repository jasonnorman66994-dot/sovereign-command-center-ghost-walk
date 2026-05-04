import dotenv from 'dotenv';
dotenv.config();

// Parse DATABASE_URL from .env
// Example: mysql://root:password@localhost:3306/omni_soc_db
const url = process.env.DATABASE_URL || '';
const match = url.match(/^mysql:\/\/(.*?):(.*?)@(.*?):(\d+)\/(.*)$/);

export const dbConfig = match ? {
  host: match[3],
  user: match[1],
  password: match[2],
  database: match[5],
  port: Number(match[4]),
} : {};
