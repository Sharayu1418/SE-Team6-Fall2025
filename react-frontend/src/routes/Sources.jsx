import { useState, useEffect } from 'react';
import SourceCard from '../components/SourceCard';

export default function Sources({ onDownloadSuccess }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const YOUR_AUTH_TOKEN = 'c2dd7b4b6867b18fa6089224437b875e2a5a12e9';

    async function fetchSources() {
      try {
        const response = await fetch('http://localhost:8000/api/sources/', {
          headers: { 'Authorization': `Token ${YOUR_AUTH_TOKEN}` }
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setSources(data.results);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    fetchSources();
  }, []);

  if (loading) return <div>Loading content sources...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>📡 Content Sources</h2>
        <small className="text-muted">Subscribe to your favorite sources</small>
      </div>
      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        {sources.map(source => (
          <SourceCard 
            key={source.id} 
            source={source} 
            onDownloadSuccess={onDownloadSuccess} 
          />
        ))}
      </div>
    </>
  );
}