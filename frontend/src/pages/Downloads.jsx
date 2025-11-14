/**
 * Downloads page - View and manage downloaded content.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../api/client';

export default function Downloads() {
  const { user } = useAuth();
  const [downloads, setDownloads] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all'); // all, queued, downloading, ready, failed

  useEffect(() => {
    fetchDownloads();
  }, []);

  const fetchDownloads = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await api.get('/downloads/');
      // Handle paginated response from DRF
      const items = response.data.results || response.data;
      setDownloads(items);
    } catch (err) {
      setError('Failed to load downloads');
      console.error('Error fetching downloads:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      ready: 'bg-green-100 text-green-800',
      downloading: 'bg-blue-100 text-blue-800',
      queued: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
    };
    
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status) => {
    const labels = {
      ready: 'Ready',
      downloading: 'Downloading',
      queued: 'Queued',
      failed: 'Failed',
    };
    
    return labels[status] || status;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleDownload = async (downloadId, mediaUrl) => {
    try {
      // Try to download via the API endpoint first
      const response = await api.get(`/downloads/${downloadId}/file/`, {
        responseType: 'blob',
      });
      
      // Create a blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${downloads.find(d => d.id === downloadId)?.title || 'download'}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      // Fallback to direct media URL
      if (mediaUrl) {
        window.open(mediaUrl, '_blank');
      } else {
        alert('Download failed: ' + (err.response?.data?.error || err.message));
      }
    }
  };

  const filteredDownloads = filterStatus === 'all' 
    ? downloads 
    : downloads.filter(d => d.status === filterStatus);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Downloads</h1>
        <p className="mt-2 text-gray-600">
          View and manage your downloaded content
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filter Buttons */}
      <div className="mb-6 flex items-center space-x-4">
        <span className="text-sm font-medium text-gray-700">Filter by status:</span>
        <div className="flex space-x-2">
          {['all', 'ready', 'downloading', 'queued', 'failed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
        <div className="ml-auto">
          <button
            onClick={fetchDownloads}
            className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-600">Total</p>
          <p className="text-2xl font-bold text-gray-900">{downloads.length}</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-600">Ready</p>
          <p className="text-2xl font-bold text-green-600">
            {downloads.filter(d => d.status === 'ready').length}
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-600">In Progress</p>
          <p className="text-2xl font-bold text-blue-600">
            {downloads.filter(d => d.status === 'downloading' || d.status === 'queued').length}
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-600">Failed</p>
          <p className="text-2xl font-bold text-red-600">
            {downloads.filter(d => d.status === 'failed').length}
          </p>
        </div>
      </div>

      {/* Downloads List */}
      {filteredDownloads.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No downloads found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {filterStatus === 'all' 
              ? 'You don\'t have any downloads yet. Use the agent executor to discover and download content.' 
              : `No ${filterStatus} downloads. Try a different filter.`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredDownloads.map((download) => (
            <div
              key={download.id}
              className="bg-white shadow rounded-lg p-6 border-l-4 border-blue-500"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {download.title}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(download.status)}`}>
                      {getStatusLabel(download.status)}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>
                      <span className="font-medium">Source:</span> {download.source_name || 'Unknown'}
                    </p>
                    <p>
                      <span className="font-medium">Available from:</span> {formatDate(download.available_from)}
                    </p>
                    {download.file_size_bytes && (
                      <p>
                        <span className="font-medium">Size:</span> {formatFileSize(download.file_size_bytes)}
                      </p>
                    )}
                    {download.error_message && (
                      <p className="text-red-600">
                        <span className="font-medium">Error:</span> {download.error_message}
                      </p>
                    )}
                  </div>
                  
                  {download.original_url && (
                    <a
                      href={download.original_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 text-sm text-blue-600 hover:text-blue-800 inline-block"
                    >
                      View original →
                    </a>
                  )}
                </div>
                
                <div className="ml-4 flex flex-col items-end space-y-2">
                  {download.status === 'ready' && download.media_url && (
                    <button
                      onClick={() => handleDownload(download.id, download.media_url)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-sm font-medium"
                    >
                      Download
                    </button>
                  )}
                  {download.status === 'ready' && download.media_url && (
                    <a
                      href={download.media_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 text-sm font-medium"
                    >
                      Play
                    </a>
                  )}
                  {(download.status === 'downloading' || download.status === 'queued') && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span>Processing...</span>
                    </div>
                  )}
                  {download.status === 'failed' && (
                    <button
                      onClick={fetchDownloads}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm font-medium"
                    >
                      Retry
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">💡 How Downloads Work</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Use the Agent Executor on the Dashboard to discover and queue content</li>
          <li>• Downloads are automatically processed in the background</li>
          <li>• Ready downloads can be played or downloaded for offline access</li>
          <li>• Failed downloads can be retried by refreshing the page</li>
        </ul>
      </div>
    </div>
  );
}
