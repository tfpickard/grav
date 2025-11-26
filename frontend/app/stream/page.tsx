'use client';

import { useEffect, useState } from 'react';
import { Controls } from '../../components/Controls';
import { MetadataPanel } from '../../components/MetadataPanel';
import { StreamChart } from '../../components/Chart';
import { fetchNextChunk, fetchSegments, fetchState, selectSegment, type SegmentInfo, type StreamChunk, type ReplayState } from '../../lib/api';

export default function StreamPage() {
  const [segments, setSegments] = useState<SegmentInfo[]>([]);
  const [chunks, setChunks] = useState<StreamChunk[]>([]);
  const [state, setState] = useState<ReplayState>();
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    fetchSegments().then(setSegments).catch(console.error);
    fetchState().then(setState).catch(console.error);
  }, []);

  useEffect(() => {
    if (!playing) return;
    const interval = setInterval(async () => {
      try {
        const chunk = await fetchNextChunk();
        setChunks((prev) => [...prev.slice(-50), chunk]);
        const newState = await fetchState();
        setState(newState);
      } catch (err) {
        console.error(err);
      }
    }, 600);
    return () => clearInterval(interval);
  }, [playing]);

  const currentSegmentId = state?.current_segment?.segment_id;

  const handleSelect = async (segmentId: string) => {
    await selectSegment(segmentId);
    const newState = await fetchState();
    setState(newState);
    setChunks([]);
  };

  return (
    <main className="container" style={{ paddingTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p className="badge">Historical playback</p>
          <h1 style={{ marginBottom: 0 }}>Cosmic stream console</h1>
          <p style={{ color: 'var(--muted)' }}>Quasi-periodic gravitational wave segments restreamed from GWOSC archives.</p>
        </div>
      </div>

      <div className="grid" style={{ marginTop: '1.5rem' }}>
        <StreamChart chunks={chunks} />
        <MetadataPanel state={state} latestChunk={chunks.at(-1)} />
      </div>
      <div style={{ marginTop: '1rem' }}>
        <Controls segments={segments} currentSegmentId={currentSegmentId} onSelect={handleSelect} onToggle={() => setPlaying((p) => !p)} playing={playing} />
      </div>
    </main>
  );
}
