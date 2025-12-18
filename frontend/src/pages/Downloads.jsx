/**
 * Downloads page - View and manage downloaded content.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../api/client';

// Helper to get icon for content type
const getTypeIcon = (type) => {
  const icons = {
    podcast: '🎙️',
    meme: '😂',
    news: '🗞️',
    video: '▶️',
    article: '📰',
  };
  return icons[type] || '📄';
};

// Helper to get badge color for content type
const getTypeBadgeClass = (type) => {
  const classes = {
    podcast: 'bg-purple-100 text-purple-800',
    meme: 'bg-yellow-100 text-yellow-800',
    news: 'bg-blue-100 text-blue-800',
    video: 'bg-red-100 text-red-800',
    article: 'bg-green-100 text-green-800',
  };
  return classes[type] || 'bg-gray-100 text-gray-800';
};

export default function Downloads() {
  const { user } = useAuth();
  const [downloads, setDownloads] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all'); // all, queued, downloading, ready, failed
  const [filterType, setFilterType] = useState('all'); // all, podcast, meme, news
  const [expandedDescriptions, setExpandedDescriptions] = useState({}); // Track expanded descriptions

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

  const handleDownload = async (downloadId, mediaUrl, sourceType) => {
    try {
      // For memes and news, download directly from media URL
      if (['meme', 'news'].includes(sourceType) && mediaUrl) {
        const download = downloads.find(d => d.id === downloadId);
        const title = download?.title || 'download';
        
        // Fetch the image and trigger download
        const response = await fetch(mediaUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Get file extension from URL or content type
        const urlPath = mediaUrl.split('?')[0];
        let extension = urlPath.split('.').pop();
        if (!['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension?.toLowerCase())) {
          extension = 'jpg'; // Default for images
        }
        
        link.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}.${extension}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        return;
      }
      
      // For podcasts and other content, try API endpoint first
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

  const toggleDescription = (downloadId) => {
    setExpandedDescriptions(prev => ({
      ...prev,
      [downloadId]: !prev[downloadId]
    }));
  };

  // Apply both status and type filters
  const filteredDownloads = downloads.filter(d => {
    const statusMatch = filterStatus === 'all' || d.status === filterStatus;
    const typeMatch = filterType === 'all' || d.source_type === filterType;
    return statusMatch && typeMatch;
  });

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
      <div className="mb-6 space-y-4">
        {/* Status Filter */}
        <div className="flex items-center space-x-4 flex-wrap gap-2">
          <span className="text-sm font-medium text-gray-700">Status:</span>
          <div className="flex space-x-2 flex-wrap gap-2">
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
        </div>
        
        {/* Type Filter */}
        <div className="flex items-center space-x-4 flex-wrap gap-2">
          <span className="text-sm font-medium text-gray-700">Type:</span>
          <div className="flex space-x-2 flex-wrap gap-2">
            {[
              { key: 'all', label: 'All', icon: '🎯' },
              { key: 'podcast', label: 'Podcasts', icon: '🎙️' },
              { key: 'meme', label: 'Memes', icon: '😂' },
              { key: 'news', label: 'News', icon: '🗞️' },
            ].map((type) => (
              <button
                key={type.key}
                onClick={() => setFilterType(type.key)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  filterType === type.key
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {type.icon} {type.label}
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
          {filteredDownloads.map((download) => {
            const isExpanded = expandedDescriptions[download.id];
            const hasDescription = download.description && download.description.trim().length > 0;
            const isNewsOrMeme = ['news', 'meme'].includes(download.source_type);
            
            return (
              <div
                key={download.id}
                className={`bg-white shadow rounded-lg p-6 border-l-4 ${
                  download.source_type === 'meme' ? 'border-yellow-500' :
                  download.source_type === 'news' ? 'border-blue-500' :
                  download.source_type === 'podcast' ? 'border-purple-500' :
                  'border-gray-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Title with type icon and badges */}
                    <div className="flex items-center space-x-3 mb-2 flex-wrap gap-2">
                      <span className="text-2xl">{getTypeIcon(download.source_type)}</span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {download.title}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeBadgeClass(download.source_type)}`}>
                        {download.source_type || 'unknown'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(download.status)}`}>
                        {getStatusLabel(download.status)}
                      </span>
                    </div>
                    
                    {/* News article overview section */}
                    {download.source_type === 'news' && hasDescription && (
                      <div className="mb-3 bg-gray-50 rounded-lg p-3 border-l-2 border-blue-400">
                        <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Overview</p>
                        <p className={`text-sm text-gray-700 leading-relaxed ${isExpanded ? '' : 'line-clamp-3'}`}>
                          {download.description}
                        </p>
                        {download.description.length > 200 && (
                          <button
                            onClick={() => toggleDescription(download.id)}
                            className="text-sm text-blue-600 hover:text-blue-800 mt-2 font-medium"
                          >
                            {isExpanded ? '↑ Show less' : '↓ Read more'}
                          </button>
                        )}
                      </div>
                    )}
                    
                    {/* Meme description (simpler style) */}
                    {download.source_type === 'meme' && hasDescription && (
                      <div className="mb-3">
                        <p className={`text-sm text-gray-600 italic ${isExpanded ? '' : 'line-clamp-2'}`}>
                          {download.description}
                        </p>
                        {download.description.length > 150 && (
                          <button
                            onClick={() => toggleDescription(download.id)}
                            className="text-sm text-blue-600 hover:text-blue-800 mt-1"
                          >
                            {isExpanded ? 'Show less' : 'Read more'}
                          </button>
                        )}
                      </div>
                    )}
                    
                    {/* Podcast description */}
                    {!isNewsOrMeme && hasDescription && (
                      <div className="mb-3">
                        <p className={`text-sm text-gray-700 ${isExpanded ? '' : 'line-clamp-3'}`}>
                          {download.description}
                        </p>
                        {download.description.length > 200 && (
                          <button
                            onClick={() => toggleDescription(download.id)}
                            className="text-sm text-blue-600 hover:text-blue-800 mt-1"
                          >
                            {isExpanded ? 'Show less' : 'Read more'}
                          </button>
                        )}
                      </div>
                    )}
                    
                    {/* Meme/News image preview */}
                    {isNewsOrMeme && download.media_url && download.status === 'ready' && (
                      <div className="mb-3">
                        <img 
                          src={download.media_url} 
                          alt={download.title}
                          className="max-w-sm max-h-64 rounded-lg shadow-sm object-contain"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                    )}
                    
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
                        {isNewsOrMeme ? 'Read full article →' : 'View original →'}
                      </a>
                    )}
                  </div>
                  
                  <div className="ml-4 flex flex-col items-end space-y-2">
                    {/* Podcast/Video: Download and Play buttons */}
                    {download.status === 'ready' && download.media_url && !isNewsOrMeme && (
                      <>
                        <button
                          onClick={() => handleDownload(download.id, download.media_url, download.source_type)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-sm font-medium"
                        >
                          Download
                        </button>
                        <a
                          href={download.media_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 text-sm font-medium"
                        >
                          Play
                        </a>
                      </>
                    )}
                    
                    {/* Meme/News: Download and View buttons */}
                    {download.status === 'ready' && download.media_url && isNewsOrMeme && (
                      <>
                        <button
                          onClick={() => handleDownload(download.id, download.media_url, download.source_type)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-sm font-medium"
                        >
                          Download
                        </button>
                        <a
                          href={download.media_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 text-sm font-medium"
                        >
                          View Full
                        </a>
                      </>
                    )}
                    
                    {/* Processing state */}
                    {(download.status === 'downloading' || download.status === 'queued') && (
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span>Processing...</span>
                      </div>
                    )}
                    
                    {/* Failed state */}
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
            );
          })}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">💡 How Downloads Work</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Use the Agent Executor on the Dashboard to discover and queue content</li>
          <li>• <strong>Auto-Download:</strong> Files are automatically saved to your Downloads folder when ready</li>
          <li>• Content is matched based on your <strong>subscriptions</strong> and filtered by your <strong>preferences</strong></li>
          <li>• Podcasts can be played directly or downloaded for offline listening</li>
          <li>• Memes and news images can be downloaded or viewed in full size</li>
          <li>• Failed downloads can be retried by refreshing the page</li>
        </ul>
      </div>
    </div>
  );
}
