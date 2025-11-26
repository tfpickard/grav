'use client';

import { useMemo } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { StreamChunk } from '../lib/api';

export function StreamChart({ chunks }: { chunks: StreamChunk[] }) {
  const data = useMemo(() => {
    const flattened: { t: number; y: number }[] = [];
    chunks.forEach((chunk) => {
      const dt = 1 / chunk.sample_rate_hz;
      chunk.samples.forEach((sample, idx) => {
        const time = chunk.t_start + idx * dt;
        flattened.push({ t: Number(time.toFixed(3)), y: sample });
      });
    });
    return flattened.slice(-4000);
  }, [chunks]);

  return (
    <div style={{ height: 320 }} className="panel">
      <h3 style={{ marginTop: 0 }}>Live strain preview</h3>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data} margin={{ top: 10, bottom: 10, left: 0, right: 0 }}>
          <XAxis dataKey="t" stroke="#6b7280" tick={{ fontSize: 12 }} tickFormatter={(v) => `${v}s`} />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ background: '#0d1117', border: '1px solid #1f2937' }} />
          <Line type="monotone" dataKey="y" stroke="#a78bfa" dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
