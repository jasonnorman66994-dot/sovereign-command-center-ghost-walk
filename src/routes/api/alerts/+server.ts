import type { RequestHandler } from '@sveltejs/kit';
import mysql from 'mysql2/promise';

// Load environment variables
const {
    DATABASE_URL
} = process.env;

// Parse DATABASE_URL (format: mysql://user:pass@host:port/dbname)
function parseDatabaseUrl(url: string) {
    const match = url.match(/^mysql:\/\/(.*?):(.*?)@(.*?):(\d+)\/(.*)$/);
    if (!match) throw new Error('Invalid DATABASE_URL');
    return {
        host: match[3],
        port: Number(match[4]),
        user: match[1],
        password: match[2],
        database: match[5]
    };
}

export const GET: RequestHandler = async () => {
    try {
        const config = parseDatabaseUrl(DATABASE_URL!);
        let connection;
        try {
            connection = await mysql.createConnection(config);
            console.log('✅ Database connection successful in /api/alerts');
        } catch (connErr) {
            console.error('❌ Database connection error in /api/alerts:', connErr);
            throw connErr;
        }
        const [rows] = await connection.execute('SELECT * FROM alerts');
        await connection.end();

        // Parse geo_location JSON for each row
        const alerts = (rows as any[]).map(row => ({
            ...row,
            geo_location: typeof row.geo_location === 'string' ? JSON.parse(row.geo_location) : row.geo_location
        }));

        return new Response(JSON.stringify({ alerts }), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (error) {
        console.error('❌ API route error in /api/alerts:', error);
        return new Response(JSON.stringify({ error: (error as Error).message, details: error }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
};
