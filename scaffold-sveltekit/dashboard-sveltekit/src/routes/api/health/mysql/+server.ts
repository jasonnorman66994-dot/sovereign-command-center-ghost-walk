import { json } from '@sveltejs/kit';

export async function GET() {
  // TODO: Replace with real MySQL health check logic and .env usage
  return json({ status: 'healthy' });
}
