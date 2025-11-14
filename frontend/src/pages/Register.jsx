/**
 * Registration page with user preferences.
 */

import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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

export default function Register() {
  const navigate = useNavigate();
  const { register, isAuthenticated, isLoading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    preferences: {
      topics: [],
      max_daily_items: 10,
      max_storage_mb: 500,
    },
    subscriptions: [], // Array of source IDs to subscribe to
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  const [availableSources, setAvailableSources] = useState([]);
  const [loadingSources, setLoadingSources] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  // Fetch available content sources on mount
  useEffect(() => {
    const fetchSources = async () => {
      try {
        setLoadingSources(true);
        const response = await api.get('/sources/');
        // Handle paginated response from DRF
        const sources = response.data.results || response.data;
        setAvailableSources(sources);
      } catch (err) {
        console.error('Failed to fetch content sources:', err);
      } finally {
        setLoadingSources(false);
      }
    };
    
    fetchSources();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name in formData.preferences) {
      setFormData({
        ...formData,
        preferences: {
          ...formData.preferences,
          [name]: name === 'topics' ? value : parseInt(value, 10),
        },
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const handleTopicToggle = (topic) => {
    const currentTopics = formData.preferences.topics;
    const newTopics = currentTopics.includes(topic)
      ? currentTopics.filter((t) => t !== topic)
      : [...currentTopics, topic];
    
    setFormData({
      ...formData,
      preferences: {
        ...formData.preferences,
        topics: newTopics,
      },
    });
  };

  const handleSourceToggle = (sourceId) => {
    const currentSources = formData.subscriptions;
    const newSources = currentSources.includes(sourceId)
      ? currentSources.filter((id) => id !== sourceId)
      : [...currentSources, sourceId];
    
    setFormData({
      ...formData,
      subscriptions: newSources,
    });
  };

  const validateForm = () => {
    const errors = {};

    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    if (formData.preferences.topics.length === 0) {
      errors.topics = 'Please select at least one topic';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    const { confirmPassword, ...registrationData } = formData;
    const result = await register(registrationData);
    
    if (result.success) {
      navigate('/');
    }
    
    setIsSubmitting(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join SmartCache AI
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Account Information */}
          <div className="bg-white shadow rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
            
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username *
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Choose a username"
                value={formData.username}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email (optional)
              </label>
              <input
                id="email"
                name="email"
                type="email"
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="At least 6 characters"
                value={formData.password}
                onChange={handleChange}
              />
              {formErrors.password && (
                <p className="mt-1 text-sm text-red-600">{formErrors.password}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Password *
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Re-enter password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
              {formErrors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{formErrors.confirmPassword}</p>
              )}
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-white shadow rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Content Preferences</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topics of Interest *
              </label>
              <div className="flex flex-wrap gap-2">
                {AVAILABLE_TOPICS.map((topic) => (
                  <button
                    key={topic}
                    type="button"
                    onClick={() => handleTopicToggle(topic)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      formData.preferences.topics.includes(topic)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {topic}
                  </button>
                ))}
              </div>
              {formErrors.topics && (
                <p className="mt-1 text-sm text-red-600">{formErrors.topics}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="max_daily_items" className="block text-sm font-medium text-gray-700">
                  Max Daily Items
                </label>
                <input
                  id="max_daily_items"
                  name="max_daily_items"
                  type="number"
                  min="1"
                  max="50"
                  className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  value={formData.preferences.max_daily_items}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label htmlFor="max_storage_mb" className="block text-sm font-medium text-gray-700">
                  Max Storage (MB)
                </label>
                <input
                  id="max_storage_mb"
                  name="max_storage_mb"
                  type="number"
                  min="100"
                  max="5000"
                  step="100"
                  className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  value={formData.preferences.max_storage_mb}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          {/* Content Sources Subscriptions */}
          <div className="bg-white shadow rounded-lg p-6 space-y-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Subscribe to Content Sources</h3>
              <p className="mt-1 text-sm text-gray-500">
                Choose podcasts and content sources you'd like to follow (optional)
              </p>
            </div>
            
            {loadingSources ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : availableSources.length === 0 ? (
              <p className="text-sm text-gray-500 py-4">No content sources available yet.</p>
            ) : (
              <div className="space-y-3">
                {availableSources.map((source) => (
                  <div
                    key={source.id}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      formData.subscriptions.includes(source.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleSourceToggle(source.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-gray-900">{source.name}</h4>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            source.type === 'podcast' 
                              ? 'bg-purple-100 text-purple-800' 
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {source.type}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div
                          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                            formData.subscriptions.includes(source.id)
                              ? 'border-blue-500 bg-blue-500'
                              : 'border-gray-300'
                          }`}
                        >
                          {formData.subscriptions.includes(source.id) && (
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {formData.subscriptions.length > 0 && (
              <p className="text-sm text-gray-600">
                {formData.subscriptions.length} source{formData.subscriptions.length !== 1 ? 's' : ''} selected
              </p>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                Sign in here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

