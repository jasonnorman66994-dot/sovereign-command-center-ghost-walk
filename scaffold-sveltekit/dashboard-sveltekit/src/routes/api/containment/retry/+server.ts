import type { RequestHandler } from '@sveltejs/kit';
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
import { KubeConfig, CoreV1Api, NetworkingV1Api } from '@kubernetes/client-node';
import { PatchStrategy } from '@kubernetes/client-node/dist/patch.js';
dotenv.config();

export const POST: RequestHandler = async ({ request }) => {
  const { log_id } = await request.json();
  let connection;
  try {
    connection = await mysql.createConnection(process.env.DATABASE_URL!);
    // Find the log entry by id
    const [rows] = await connection.execute(
      `SELECT * FROM incident_response_logs WHERE id = ? AND action_taken = 'Queued' LIMIT 1`,
      [log_id]
    );
    if (!rows || rows.length === 0) {
      return new Response(JSON.stringify({ error: 'No queued action found for this log_id.' }), { status: 404 });
    }
    const log = rows[0];
    const pod_name = log.pod_name;
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
      // Update log to mark as executed
      await connection.execute(
        `UPDATE incident_response_logs SET action_taken = 'Executed', reason = 'Retried and succeeded', timestamp_utc = UTC_TIMESTAMP() WHERE id = ?`,
        [log_id]
      );
      return new Response(JSON.stringify({ success: true }));
    } catch (err) {
      return new Response(JSON.stringify({ error: 'K8s still unreachable.' }), { status: 503 });
    }
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 });
  } finally {
    if (connection) await connection.end();
  }
};
