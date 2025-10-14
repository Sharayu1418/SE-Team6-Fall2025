import React from 'react';
import DownloadsList from '../components/DownloadsList';

export default function Downloads({ downloads, setDownloads }) {
  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>📱 Your Downloads</h2>
        <small className="text-muted">Content ready for offline access</small>
      </div>
      <DownloadsList downloads={downloads} setDownloads={setDownloads} />
    </>
  );
}