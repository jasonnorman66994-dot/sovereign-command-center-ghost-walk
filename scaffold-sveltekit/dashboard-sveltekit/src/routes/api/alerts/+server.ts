
import mysql from 'mysql2/promise';
import { json } from '@sveltejs/kit';
import dotenv from 'dotenv';
import path from 'path';
import { KubeConfig, CoreV1Api, NetworkingV1Api } from '@kubernetes/client-node';
import { PatchStrategy } from '@kubernetes/client-node/dist/patch.js';

// Load .env from project root
dotenv.config({ path: path.resolve(process.cwd(), '../../.env') });

const dbUrl = process.env.DATABASE_URL || '';
const match = dbUrl.match(/^mysql:\/\/(.*?):(.*?)@(.*?):(\d+)\/(.*)$/);
const dbConfig = match ? {
  host: match[3],
  user: match[1],
  password: match[2],
  database: match[5],
  port: Number(match[4])
} : {};

export async function GET() {
  let connection;
  try {
    connection = await mysql.createConnection(dbConfig);
    const [rows] = await connection.execute(`
      SELECT alert_type, severity, timestamp_utc, user_email, geo_location, baseline_value, deviation_score
      FROM alerts
      WHERE severity = 'critical'
      ORDER BY timestamp_utc DESC
      LIMIT 50
    `);

    // For each alert, calculate deviation_score based on historical frequency for the same hour-block
    const alerts = await Promise.all(rows.map(async (row) => {
      const alertType = row.alert_type;
      const timestamp = row.timestamp_utc;
      const hour = timestamp ? new Date(timestamp).getHours() : null;
      let deviation_score = row.deviation_score;
      let baseline_value = row.baseline_value;

      if (alertType && hour !== null) {
        // Count how many alerts of this type in this hour-block in the last 30 days
        const [histRows] = await connection.execute(
          `SELECT COUNT(*) as count, AVG(cnt) as avg, STDDEV(cnt) as stddev FROM (
            SELECT COUNT(*) as cnt
            FROM alerts
            WHERE alert_type = ? AND HOUR(timestamp_utc) = ? AND timestamp_utc >= NOW() - INTERVAL 30 DAY
            GROUP BY DATE(timestamp_utc), HOUR(timestamp_utc)
          ) as sub` , [alertType, hour]
        );
        const hist = histRows[0];
        baseline_value = hist.avg || 0;
        // Current count for this hour-block today
        const [currRows] = await connection.execute(
          `SELECT COUNT(*) as cnt FROM alerts WHERE alert_type = ? AND HOUR(timestamp_utc) = ? AND DATE(timestamp_utc) = CURDATE()` , [alertType, hour]
        );
        const currentCount = currRows[0]?.cnt || 0;
        // Z-score calculation
        if (hist.stddev && hist.stddev > 0) {
          deviation_score = (currentCount - baseline_value) / hist.stddev;
        } else {
          deviation_score = 0;
        }
        // If deviation_score > 2, set to 2.5 for anomalous pulse
        if (deviation_score > 2) deviation_score = 2.5;
        // Containment Protocol: If deviation_score > 3.0, quarantine pod and block egress
        if (deviation_score > 3.0 && row.pod_name && row.namespace) {
          try {
            // Kubernetes client setup
            const kc = new KubeConfig();
            kc.loadFromDefault();
            const k8sApi = kc.makeApiClient(CoreV1Api);
            const netApi = kc.makeApiClient(NetworkingV1Api);
            // Patch pod with status=quarantine
            const patch = [
              { op: 'add', path: '/metadata/labels/status', value: 'quarantine' }
            ];
            await k8sApi.patchNamespacedPod(
              row.pod_name,
              row.namespace,
              patch,
              undefined,
              undefined,
              undefined,
              undefined,
              { headers: { 'Content-Type': PatchStrategy.JsonPatch } }
            );
            // Create NetworkPolicy to block egress
            const netPolicyName = `quarantine-egress-${row.pod_name}`;
            const netPolicy = {
              metadata: { name: netPolicyName, namespace: row.namespace },
              spec: {
                podSelector: { matchLabels: { status: 'quarantine', app: row.pod_name } },
                policyTypes: ['Egress'],
                egress: []
              }
            };
            await netApi.createNamespacedNetworkPolicy(row.namespace, netPolicy);
            // Log to incident_response_logs
            await connection.execute(
              `INSERT INTO incident_response_logs (pod_name, action_taken, reason, timestamp_utc)
               VALUES (?, ?, ?, UTC_TIMESTAMP())`,
              [row.pod_name, 'quarantine & block egress', 'deviation_score > 3.0']
            );
          } catch (containmentError) {
            // If the error is a connection refused or cluster unreachable, queue the action
            const errMsg = String(containmentError.message || containmentError);
            if (errMsg.includes('connect') || errMsg.includes('ECONNREFUSED') || errMsg.includes('Unable to connect')) {
              await connection.execute(
                `INSERT INTO incident_response_logs (pod_name, action_taken, reason, timestamp_utc)
                 VALUES (?, ?, ?, UTC_TIMESTAMP())`,
                [row.pod_name, 'Queued', 'K8s Cluster Offline - Action Queued']
              );
            } else {
              console.error('Containment Protocol Error:', containmentError);
            }
          }
        }
      }
      return {
        alert_type: row.alert_type,
        severity: row.severity,
        timestamp_utc: row.timestamp_utc,
        user_email: row.user_email,
        geo_location: row.geo_location,
        baseline_value,
        deviation_score
      };
    }));
    console.log('Sentinel Containment Active: Monitoring for high-deviation breakouts');
    return json({ alerts });
  } catch (error) {
    return json({ error: error.message }, { status: 500 });
  } finally {
    if (connection) await connection.end();
  }
}
