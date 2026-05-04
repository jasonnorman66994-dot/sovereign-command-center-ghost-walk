import { json } from '@sveltejs/kit';

export async function GET() {
  // TODO: Replace with real k8s health check logic and .env usage
  return json({ status: 'healthy' });
}
