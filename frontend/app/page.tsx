import Link from 'next/link';
import styles from './page.module.css';

export default function HomePage() {
  return (
    <main className="container">
      <div className={styles.hero}>
        <div>
          <p className="badge">Quasi-live cosmic faucet</p>
          <h1>Replay historical LIGO gravitational waves in real time.</h1>
          <p className={styles.lede}>
            We ingest and preprocess open data from the LIGO Open Science Center, extract quasi-periodic segments, and
            restream them as a live-like feed you can plug into your own apps.
          </p>
          <div className={styles.actions}>
            <Link href="/stream"><button>Start the cosmic stream</button></Link>
            <a href="https://www.gw-openscience.org/" target="_blank" rel="noreferrer">Learn about GWOSC</a>
          </div>
        </div>
        <div className={styles.card}>
          <h3>What you&apos;ll see</h3>
          <ul>
            <li>Chunked strain samples delivered like a live socket.</li>
            <li>Metadata for event, detector, playback speed, and state.</li>
            <li>Interactive charting of the latest few seconds of data.</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
