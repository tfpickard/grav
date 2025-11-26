'use client';

import { useState } from 'react';
import type { SegmentInfo } from '../lib/api';

interface Props {
  segments: SegmentInfo[];
  currentSegmentId?: string;
  onSelect: (segmentId: string) => void;
  onToggle: () => void;
  playing: boolean;
}

export function Controls({ segments, currentSegmentId, onSelect, onToggle, playing }: Props) {
  const [selected, setSelected] = useState(currentSegmentId);
  return (
    <div className="panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>Controls</h3>
        <button onClick={onToggle}>{playing ? 'Pause stream' : 'Resume stream'}</button>
      </div>
      <div style={{ marginTop: '1rem' }}>
        <label htmlFor="segment">Select segment</label>
        <select
          id="segment"
          style={{ width: '100%', marginTop: '0.5rem', background: '#0d1117', color: 'white', padding: '0.8rem', borderRadius: 10 }}
          value={selected}
          onChange={(e) => {
            setSelected(e.target.value);
            onSelect(e.target.value);
          }}
        >
          {segments.map((s) => (
            <option key={s.segment_id} value={s.segment_id}>
              {s.event_name} · {s.detector} · {s.segment_id}
            </option>
          ))}
        </select>
      </div>
      <p style={{ color: 'var(--muted)' }}>Use the developer API or backend config to adjust playback speed.</p>
    </div>
  );
}
