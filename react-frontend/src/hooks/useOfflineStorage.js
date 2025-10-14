import { useState } from 'react';
import { downloadAndStoreContent } from '../services/storageManager';

export function useOfflineStorage(metadata, onDownloadSuccess) { // <-- Receive callback
  const [status, setStatus] = useState('idle');

  const saveForOffline = async () => {
    setStatus('saving');
    try {
      const result = await downloadAndStoreContent(metadata);
      if (result.success) {
        setStatus('saved');
        if (onDownloadSuccess && result.metadata) {
          onDownloadSuccess(result.metadata); // <-- Call it on success!
        }
      } else {
        setStatus('error');
      }
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  return { status, saveForOffline };
}