'use client';

import type { ReplayState, StreamChunk } from '../lib/api';

export function MetadataPanel({ state, latestChunk }: { state?: ReplayState; latestChunk?: StreamChunk }) {
  const meta = state?.current_segment;
  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Segment metadata</h3>
      {meta ? (
        <div style={{ display: 'grid', gap: '0.4rem' }}>
          <Row label="Event">{meta.event_name}</Row>
          <Row label="Detector">{meta.detector}</Row>
          <Row label="Segment ID">{meta.segment_id}</Row>
          <Row label="Duration">{meta.duration_seconds.toFixed(2)} s</Row>
          <Row label="Sample rate">{meta.sample_rate_hz} Hz</Row>
          <Row label="Playhead">
            {state?.playhead_position} / {state?.total_chunks}
          </Row>
          <Row label="Chunk size">{state?.config.chunk_duration_seconds}s @ {state?.config.playback_speed}x</Row>
          <Row label="Historical notice">
            This feed replays archival LIGO data; no live observations are being streamed.
          </Row>
          {latestChunk && <Row label="Last window">{latestChunk.samples.length} samples</Row>}
        </div>
      ) : (
        <p>No segment active.</p>
      )}
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--muted)' }}>
      <span>{label}</span>
      <strong style={{ color: 'var(--text)' }}>{children}</strong>
    </div>
  );
}
