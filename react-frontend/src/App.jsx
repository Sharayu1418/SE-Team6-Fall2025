import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sources from './routes/Sources.jsx';
import Downloads from './routes/Downloads.jsx';
import { getReadyDownloads } from './services/storageManager';
import './App.css';

const Placeholder = ({ title }) => <h2 className="mt-4">{title}</h2>;

function App() {
  const [downloads, setDownloads] = useState([]);

  useEffect(() => {
    getReadyDownloads().then(setDownloads);
  }, []);

  const handleDownloadSuccess = (newDownload) => {
    setDownloads(currentDownloads => [newDownload, ...currentDownloads]);
  };

  return (
    <>
      <Navbar />
      <main className="container mt-4">
        <Routes>
          <Route path="/" element={<Placeholder title="Dashboard" />} />
          <Route 
            path="/sources" 
            element={<Sources onDownloadSuccess={handleDownloadSuccess} />} 
          />
          <Route 
            path="/downloads" 
            element={<Downloads downloads={downloads} setDownloads={setDownloads} />} 
          />
          <Route path="/commutes" element={<Placeholder title="Commutes" />} />
        </Routes>
      </main>
    </>
  );
}

export default App;