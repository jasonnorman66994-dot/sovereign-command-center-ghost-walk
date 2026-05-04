// Legacy file intentionally left blank to avoid route conflict.

// This file is being removed to avoid route conflict with new SvelteKit +server.ts endpoint.
import mysql from 'mysql2/promise';
import { dbConfig } from '$lib/server/dbConfig';

export async function GET() {
  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);
    await connection.query('SELECT 1');
    await connection.end();
    return new Response(JSON.stringify({ status: 'CONNECTED' }), { status: 200 });
  } catch (err) {
    if (connection) await connection.end();
    return new Response(JSON.stringify({ status: 'DISCONNECTED', error: err.message || String(err) }), { status: 200 });
  }
}
