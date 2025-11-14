/**
 * Preferences management page.
 * 
 * Allows users to update their content preferences.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../api/client';

const AVAILABLE_TOPICS = [
  'technology',
  'science',
  'AI',
  'programming',
  'news',
  'business',
  'entertainment',
  'sports',
  'health',
];

export default function Preferences() {
  const { user, fetchUser } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    topics: [],
    max_daily_items: 10,
    max_storage_mb: 500,
  });
  const [preferenceId, setPreferenceId] = useState(null);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.get('/preferences/');
      
      if (response.data && response.data.length > 0) {
        const prefs = response.data[0];
        setPreferenceId(prefs.id);
        setFormData({
          topics: prefs.topics || [],
          max_daily_items: prefs.max_daily_items || 10,
          max_storage_mb: prefs.max_storage_mb || 500,
        });
      }
    } catch (err) {
      setError('Failed to load preferences');
      console.error('Error fetching preferences:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTopicToggle = (topic) => {
    const currentTopics = formData.topics;
    const newTopics = currentTopics.includes(topic)
      ? currentTopics.filter((t) => t !== topic)
      : [...currentTopics, topic];
    
    setFormData({
      ...formData,
      topics: newTopics,
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: parseInt(value, 10),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.topics.length === 0) {
      setError('Please select at least one topic');
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(false);

      if (preferenceId) {
        // Update existing preferences
        await api.patch(`/preferences/${preferenceId}/`, formData);
      } else {
        // Create new preferences
        const response = await api.post('/preferences/', formData);
        setPreferenceId(response.data.id);
      }

      setSuccess(true);
      // Refresh user data
      await fetchUser();
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save preferences');
      console.error('Error saving preferences:', err);
    } finally {
      setIsSaving(false);
    }
  };

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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Preferences</h1>
        <p className="mt-2 text-gray-600">
          Customize your content discovery preferences
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-md bg-red-50 border border-red-200 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="rounded-md bg-green-50 border border-green-200 p-4">
            <p className="text-sm text-green-800">Preferences saved successfully!</p>
          </div>
        )}

        {/* Topics */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Topics of Interest</h3>
          <p className="text-sm text-gray-600 mb-4">
            Select the topics you're interested in. The agents will use these to recommend content for you.
          </p>
          <div className="flex flex-wrap gap-2">
            {AVAILABLE_TOPICS.map((topic) => (
              <button
                key={topic}
                type="button"
                onClick={() => handleTopicToggle(topic)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  formData.topics.includes(topic)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
          {formData.topics.length === 0 && (
            <p className="mt-2 text-sm text-red-600">Please select at least one topic</p>
          )}
        </div>

        {/* Limits */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Content Limits</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="max_daily_items" className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Daily Items
              </label>
              <input
                id="max_daily_items"
                name="max_daily_items"
                type="number"
                min="1"
                max="50"
                value={formData.max_daily_items}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              <p className="mt-1 text-sm text-gray-500">
                Maximum number of content items to discover per day
              </p>
            </div>

            <div>
              <label htmlFor="max_storage_mb" className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Storage (MB)
              </label>
              <input
                id="max_storage_mb"
                name="max_storage_mb"
                type="number"
                min="100"
                max="5000"
                step="100"
                value={formData.max_storage_mb}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              <p className="mt-1 text-sm text-gray-500">
                Maximum storage space for downloaded content
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving || formData.topics.length === 0}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isSaving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </form>

      {/* Current Topics Display */}
      {formData.topics.length > 0 && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Selected Topics ({formData.topics.length})</h3>
          <div className="flex flex-wrap gap-2">
            {formData.topics.map((topic) => (
              <span
                key={topic}
                className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-medium"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

