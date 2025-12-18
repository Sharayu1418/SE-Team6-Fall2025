/**
 * Agent Executor Component
 * 
 * Provides a button to trigger the RoundRobinGroupChat agents
 * and displays real-time updates via WebSocket.
 * 
 * Auto-downloads files to user's device when content is ready.
 */

import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../hooks/useAuth';

// Helper to format file size
const formatFileSize = (bytes) => {
  if (!bytes) return '';
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(2)} MB`;
};

export default function AgentExecutor() {
  const { user } = useAuth();
  const { messages, status, connect, disconnect, send, clearMessages } = useWebSocket('/ws/agents/');
  const [maxItems, setMaxItems] = useState(5);
  const [executionSummary, setExecutionSummary] = useState(null);
  const [autoDownloads, setAutoDownloads] = useState([]); // Track auto-downloaded files

  // Auto-trigger browser download
  const triggerBrowserDownload = useCallback((fileUrl, title, downloadId) => {
    try {
      // Create a hidden anchor element
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = title || `download_${downloadId}`;
      link.style.display = 'none';
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log(`Auto-download triggered for: ${title}`);
      return true;
    } catch (error) {
      console.error('Failed to trigger auto-download:', error);
      return false;
    }
  }, []);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const handleExecute = () => {
    clearMessages();
    setExecutionSummary(null);
    setAutoDownloads([]); // Clear previous auto-downloads
    connect();
  };

  useEffect(() => {
    if (status === 'connected') {
      // Send trigger message once connected
      send({
        type: 'trigger_agents',
        max_items: maxItems,
      });
    }
  }, [status, maxItems, send]);

  // Handle auto-downloads when download_ready messages arrive
  useEffect(() => {
    const downloadReadyMessages = messages.filter((m) => m.type === 'download_ready');
    
    downloadReadyMessages.forEach((msg) => {
      // Check if we already processed this download
      if (!autoDownloads.some((d) => d.download_id === msg.download_id)) {
        // Trigger browser download
        const success = triggerBrowserDownload(msg.file_url, msg.title, msg.download_id);
        
        // Track this download
        setAutoDownloads((prev) => [
          ...prev,
          {
            download_id: msg.download_id,
            title: msg.title,
            source_name: msg.source_name,
            source_type: msg.source_type,
            file_size: msg.file_size,
            success,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    });
  }, [messages, autoDownloads, triggerBrowserDownload]);

  useEffect(() => {
    // Check for execution complete message
    const completeMsg = messages.find((m) => m.type === 'execution_complete');
    if (completeMsg) {
      setExecutionSummary(completeMsg.summary);
      // Keep connection open longer to receive download_ready messages
      setTimeout(() => disconnect(), 5000);
    }
  }, [messages, disconnect]);

  const getStatusBadge = () => {
    const badges = {
      disconnected: 'bg-gray-200 text-gray-700',
      connecting: 'bg-yellow-200 text-yellow-800',
      connected: 'bg-blue-200 text-blue-800 animate-pulse',
      error: 'bg-red-200 text-red-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badges[status]}`}>
        {status}
      </span>
    );
  };

  const renderMessage = (msg, index) => {
    const { type } = msg;

    switch (type) {
      case 'connection_established':
        return (
          <div key={index} className="text-sm text-green-600 border-l-4 border-green-500 pl-3 py-2">
            ✓ {msg.message}
          </div>
        );

      case 'execution_started':
        return (
          <div key={index} className="text-sm text-blue-600 border-l-4 border-blue-500 pl-3 py-2">
            ▶ {msg.message}
          </div>
        );

      case 'agent_message':
        return (
          <div key={index} className="text-sm border-l-4 border-gray-300 pl-3 py-2">
            <span className="font-semibold text-gray-700">{msg.agent}:</span> {msg.message}
          </div>
        );

      case 'download_queued':
        return (
          <div key={index} className="text-sm border-l-4 border-purple-300 pl-3 py-2">
            <span className="font-semibold text-purple-700">Download #{msg.download_id}:</span>{' '}
            {msg.title} ({msg.source}) - <span className="text-xs">{msg.status}</span>
          </div>
        );

      case 'download_ready':
        return (
          <div key={index} className="text-sm border-l-4 border-green-400 pl-3 py-2 bg-green-50">
            <span className="font-semibold text-green-700">⬇️ Auto-downloading:</span>{' '}
            {msg.title}
            <span className="text-xs text-gray-500 ml-2">
              ({msg.source_name} • {formatFileSize(msg.file_size)})
            </span>
          </div>
        );

      case 'execution_complete':
        return (
          <div key={index} className="text-sm text-green-600 border-l-4 border-green-500 pl-3 py-2 bg-green-50">
            ✓ {msg.message}
          </div>
        );

      case 'error':
        return (
          <div key={index} className="text-sm text-red-600 border-l-4 border-red-500 pl-3 py-2 bg-red-50">
            ✗ {msg.message}
          </div>
        );

      default:
        return (
          <div key={index} className="text-sm text-gray-600 border-l-4 border-gray-200 pl-3 py-2">
            {JSON.stringify(msg)}
          </div>
        );
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Agent Execution</h2>
        {getStatusBadge()}
      </div>

      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <div>
            <label htmlFor="maxItems" className="block text-sm font-medium text-gray-700 mb-1">
              Max Items to Discover
            </label>
            <input
              id="maxItems"
              type="number"
              min="1"
              max="20"
              value={maxItems}
              onChange={(e) => setMaxItems(parseInt(e.target.value, 10))}
              disabled={status === 'connected' || status === 'connecting'}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100"
            />
          </div>

          <div className="flex-1 flex justify-end items-end">
            <button
              onClick={handleExecute}
              disabled={status === 'connected' || status === 'connecting'}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {status === 'connected' || status === 'connecting'
                ? 'Executing...'
                : 'Discover & Download Content'}
            </button>
          </div>
        </div>

        {/* Execution Summary */}
        {executionSummary && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-green-800 mb-2">Execution Summary</h3>
            <div className="grid grid-cols-5 gap-2 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{executionSummary.total_downloads}</div>
                <div className="text-xs text-gray-600">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{executionSummary.queued}</div>
                <div className="text-xs text-gray-600">Queued</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{executionSummary.downloading}</div>
                <div className="text-xs text-gray-600">Downloading</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{executionSummary.ready}</div>
                <div className="text-xs text-gray-600">Ready</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{executionSummary.failed}</div>
                <div className="text-xs text-gray-600">Failed</div>
              </div>
            </div>
          </div>
        )}

        {/* Auto-Downloads Summary */}
        {autoDownloads.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">
              📥 Auto-Downloaded to Your Device ({autoDownloads.length} files)
            </h3>
            <div className="space-y-2">
              {autoDownloads.map((download) => (
                <div
                  key={download.download_id}
                  className="flex items-center justify-between text-sm bg-white rounded p-2"
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">
                      {download.source_type === 'podcast' ? '🎙️' :
                       download.source_type === 'meme' ? '😂' :
                       download.source_type === 'news' ? '📰' : '📄'}
                    </span>
                    <div>
                      <p className="font-medium text-gray-900 truncate max-w-xs">
                        {download.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {download.source_name} • {formatFileSize(download.file_size)}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    download.success 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {download.success ? '✓ Saved' : '✗ Failed'}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-blue-600 mt-2">
              💡 Files are saved to your browser's Downloads folder
            </p>
          </div>
        )}

        {/* Message Log */}
        {messages.length > 0 && (
          <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Agent Activity Log</h3>
            <div className="space-y-2">{messages.map((msg, idx) => renderMessage(msg, idx))}</div>
          </div>
        )}
      </div>
    </div>
  );
}

