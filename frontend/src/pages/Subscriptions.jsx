/**
 * Subscriptions page - Browse and subscribe to content sources.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../api/client';

export default function Subscriptions() {
  const { user } = useAuth();
  const [sources, setSources] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('all'); // all, podcast, article

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch both sources and subscriptions (page_size=200 to get all)
      const [sourcesRes, subsRes] = await Promise.all([
        api.get('/sources/?page_size=200'),
        api.get('/subscriptions/?page_size=200')
      ]);
      
      // Handle both paginated ({results: [...]}) and non-paginated ([...]) responses
      const sourcesData = sourcesRes.data?.results || sourcesRes.data || [];
      const subsData = subsRes.data?.results || subsRes.data || [];
      
      setSources(Array.isArray(sourcesData) ? sourcesData : []);
      setSubscriptions(Array.isArray(subsData) ? subsData : []);
    } catch (err) {
      setError('Failed to load content sources');
      console.error('Error fetching data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const isSubscribed = (sourceId) => {
    return subscriptions.some(sub => sub.source === sourceId && sub.is_active);
  };

  const getSubscriptionId = (sourceId) => {
    const sub = subscriptions.find(s => s.source === sourceId && s.is_active);
    return sub?.id;
  };

  const handleSubscribe = async (sourceId) => {
    try {
      const response = await api.post('/subscriptions/', {
        source: sourceId,
        priority: 1,
        is_active: true
      });
      
      setSubscriptions([...subscriptions, response.data]);
    } catch (err) {
      alert('Failed to subscribe: ' + (err.response?.data?.error || err.message));
      console.error('Subscribe error:', err);
    }
  };

  const handleUnsubscribe = async (sourceId) => {
    try {
      const subId = getSubscriptionId(sourceId);
      if (!subId) return;
      
      await api.delete(`/subscriptions/${subId}/`);
      
      setSubscriptions(subscriptions.filter(sub => sub.id !== subId));
    } catch (err) {
      alert('Failed to unsubscribe: ' + (err.response?.data?.error || err.message));
      console.error('Unsubscribe error:', err);
    }
  };

  const toggleSubscription = async (sourceId) => {
    if (isSubscribed(sourceId)) {
      await handleUnsubscribe(sourceId);
    } else {
      await handleSubscribe(sourceId);
    }
  };

  const getSourceIcon = (type) => {
    const icons = {
      podcast: '🎙️',
      article: '📰',
      video: '🎬',
      meme: '😂',
      news: '📰',
    };
    return icons[type] || '📄';
  };

  const filteredSources = filterType === 'all' 
    ? sources 
    : sources.filter(s => (s.source_type || s.type) === filterType);

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
        <h1 className="text-3xl font-bold text-gray-900">Content Sources</h1>
        <p className="mt-2 text-gray-600">
          Subscribe to podcasts, articles, videos, and memes to receive personalized content
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filter Buttons */}
      <div className="mb-6 flex items-center space-x-4 flex-wrap gap-2">
        <span className="text-sm font-medium text-gray-700">Filter by type:</span>
        <div className="flex space-x-2 flex-wrap gap-2">
          {[
            { key: 'all', label: 'All', icon: '🎯' },
            { key: 'podcast', label: 'Podcast', icon: '🎙️' },
            { key: 'meme', label: 'Meme', icon: '😂' },
            { key: 'news', label: 'News', icon: '📰' },
          ].map((filter) => (
            <button
              key={filter.key}
              onClick={() => setFilterType(filter.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filterType === filter.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {filter.icon} {filter.label}
            </button>
          ))}
        </div>
        <div className="ml-auto">
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Subscription Stats */}
      <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-blue-900">Active Subscriptions</p>
            <p className="text-2xl font-bold text-blue-600">
              {subscriptions.filter(s => s.is_active).length} / {sources.length}
            </p>
          </div>
          <div className="text-blue-600">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
        </div>
      </div>

      {/* Sources Grid */}
      {filteredSources.length === 0 ? (
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
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No sources found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {filterType === 'all' 
              ? 'No content sources available.' 
              : `No ${filterType}s available. Try a different filter.`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSources.map((source) => {
            const subscribed = isSubscribed(source.id);
            
            return (
              <div
                key={source.id}
                className={`bg-white shadow rounded-lg p-6 border-2 transition-all ${
                  subscribed ? 'border-blue-500' : 'border-transparent hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{getSourceIcon(source.type || source.source_type)}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      {
                        podcast: 'bg-purple-100 text-purple-800',
                        article: 'bg-green-100 text-green-800',
                        video: 'bg-red-100 text-red-800',
                        meme: 'bg-yellow-100 text-yellow-800',
                        news: 'bg-blue-100 text-blue-800',
                      }[source.type || source.source_type] || 'bg-gray-100 text-gray-800'
                    }`}>
                      {source.type || source.source_type}
                    </span>
                  </div>
                  {subscribed && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                      ✓ Subscribed
                    </span>
                  )}
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {source.name}
                </h3>

                {source.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {source.description}
                  </p>
                )}

                <div className="mb-4 text-xs text-gray-500">
                  <p className="truncate">
                    <span className="font-medium">Feed:</span> {source.feed_url || source.url}
                  </p>
                </div>

                <button
                  onClick={() => toggleSubscription(source.id)}
                  className={`w-full px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    subscribed
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {subscribed ? 'Unsubscribe' : 'Subscribe'}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">💡 How Subscriptions Work</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Subscribe to podcasts and article feeds you're interested in</li>
          <li>• The Discovery Agent will find new content from your subscribed sources</li>
          <li>• Content is filtered based on your preferences (topics, limits)</li>
          <li>• You can unsubscribe anytime to stop receiving content from a source</li>
        </ul>
      </div>
    </div>
  );
}

