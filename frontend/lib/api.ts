export type SegmentInfo = {
  segment_id: string;
  event_name: string;
  detector: string;
  sample_rate_hz: number;
  num_samples: number;
  duration_seconds: number;
  source_path: string;
};

export type StreamChunk = {
  segment_id: string;
  sample_rate_hz: number;
  t_start: number;
  t_end: number;
  samples: number[];
  metadata: {
    event_name: string;
    detector: string;
    playhead_position: number;
    total_chunks: number;
  };
};

export type ReplayState = {
  current_segment: SegmentInfo | null;
  playhead_position: number;
  total_chunks: number;
  config: {
    chunk_duration_seconds: number;
    playback_speed: number;
    loop_segments: boolean;
  };
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export async function fetchSegments(): Promise<SegmentInfo[]> {
  const res = await fetch(`${API_BASE}/api/segments`);
  if (!res.ok) throw new Error('Unable to load segments');
  return res.json();
}

export async function fetchNextChunk(): Promise<StreamChunk> {
  const res = await fetch(`${API_BASE}/api/stream/next`);
  if (!res.ok) throw new Error('Unable to load stream chunk');
  return res.json();
}

export async function selectSegment(segment_id: string): Promise<SegmentInfo> {
  const res = await fetch(`${API_BASE}/api/stream/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ segment_id }),
  });
  if (!res.ok) throw new Error('Unable to select segment');
  return res.json();
}

export async function fetchState(): Promise<ReplayState> {
  const res = await fetch(`${API_BASE}/api/stream/state`);
  if (!res.ok) throw new Error('Unable to load stream state');
  return res.json();
}
