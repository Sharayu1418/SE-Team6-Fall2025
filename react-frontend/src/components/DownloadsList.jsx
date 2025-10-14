import React, { useState, useEffect } from 'react';
import { getReadyDownloads, deleteContent } from '../services/storageManager';

export default function DownloadsList() {
  const [downloads, setDownloads] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadDownloads() {
      try {
        const items = await getReadyDownloads();
        setDownloads(items);
      } catch (error) {
        console.error("Failed to load downloads:", error);
      } finally {
        setIsLoading(false);
      }
    }
    loadDownloads();
  }, []);

  const handleDelete = async (url) => {
    const result = await deleteContent(url);
    if (result.success) {
      // If deletion is successful, update the UI by filtering out the deleted item
      setDownloads(currentDownloads => currentDownloads.filter(d => d.original_url !== url));
    } else {
      alert("Failed to delete the item. Please try again.");
    }
  };

  if (isLoading) {
    return <p>Loading downloads...</p>;
  }

  return (
    <div className="downloads-section">
      <h2>📱 Your Downloads</h2>
      {downloads.length > 0 ? (
        <div className="card-container">
          {downloads.map(item => (
            <div className="card" key={item.original_url}>
              <h6>{item.title}</h6>
              <small>Status: {item.status}</small>
              <button 
                onClick={() => handleDelete(item.original_url)} 
                className="btn btn-sm btn-outline-danger mt-2"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p>No content saved for offline use yet.</p>
      )}
    </div>
  );
}