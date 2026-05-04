import type { RequestHandler } from '@sveltejs/kit';
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
import { KubeConfig, CoreV1Api, NetworkingV1Api } from '@kubernetes/client-node';
import { PatchStrategy } from '@kubernetes/client-node/dist/patch.js';
dotenv.config();

export const POST: RequestHandler = async ({ request }) => {
  const { pod_name } = await request.json();
  let connection;
  try {
    connection = await mysql.createConnection(process.env.DATABASE_URL!);
    // Find the latest queued log for this pod
    const [rows] = await connection.execute(
      `SELECT * FROM incident_response_logs WHERE pod_name = ? AND action_taken = 'Queued' ORDER BY timestamp_utc DESC LIMIT 1`,
      [pod_name]
    );
    if (!rows || rows.length === 0) {
      return new Response(JSON.stringify({ error: 'No queued action found.' }), { status: 404 });
    }
    // Try containment again (simulate the same logic as in alerts/+server.ts)
    // For demo, you may want to fetch namespace from the log or another source
    const log = rows[0];
    const namespace = log.namespace || 'default';
    try {
      const kc = new KubeConfig();
      kc.loadFromDefault();
      const k8sApi = kc.makeApiClient(CoreV1Api);
      const netApi = kc.makeApiClient(NetworkingV1Api);
      const patch = [
        { op: 'add', path: '/metadata/labels/status', value: 'quarantine' }
      ];
      await k8sApi.patchNamespacedPod(
        pod_name,
        namespace,
        patch,
        undefined,
        undefined,
        undefined,
        undefined,
        { headers: { 'Content-Type': PatchStrategy.JsonPatch } }
      );
      const netPolicyName = `quarantine-egress-${pod_name}`;
      const netPolicy = {
        metadata: { name: netPolicyName, namespace },
        spec: {
          podSelector: { matchLabels: { status: 'quarantine', app: pod_name } },
          policyTypes: ['Egress'],
          egress: []
        }
      };
      await netApi.createNamespacedNetworkPolicy(namespace, netPolicy);
      // Update log to mark as completed
      await connection.execute(
        `UPDATE incident_response_logs SET action_taken = 'quarantine & block egress', reason = 'Retried and succeeded', timestamp_utc = UTC_TIMESTAMP() WHERE id = ?`,
        [log.id]
      );
      return new Response(JSON.stringify({ success: true }));
    } catch (err) {
      // If still offline, keep as queued
      return new Response(JSON.stringify({ error: 'K8s still unreachable.' }), { status: 503 });
    }
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 });
  } finally {
    if (connection) await connection.end();
  }
};