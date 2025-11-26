import Link from 'next/link';

export default function DeveloperPage() {
  return (
    <main className="container" style={{ paddingTop: '2rem' }}>
      <p className="badge">For integrators</p>
      <h1>API guide</h1>
      <p style={{ color: 'var(--muted)' }}>
        Use the FastAPI service as a quasi-live faucet of gravitational-wave strain samples for prototypes, visualizations, or data-art experiments.
      </p>
      <div className="panel" style={{ marginTop: '1rem' }}>
        <h3>Endpoints</h3>
        <ul>
          <li><code>GET /api/segments</code> — list available segments & metadata.</li>
          <li><code>GET /api/stream/next</code> — fetch the next time slice.</li>
          <li><code>POST /api/stream/select</code> — body: {'{ "segment_id": "..." }'} to switch.</li>
          <li><code>GET /api/stream/state</code> — view playhead, total chunks, and playback settings.</li>
          <li><code>WS /ws/stream</code> — optional websocket stream delivering JSON chunks.</li>
        </ul>
        <p>See the README for docker-compose instructions and preprocessing pipeline details.</p>
        <Link href="/stream">Back to console</Link>
      </div>
    </main>
  );
}
