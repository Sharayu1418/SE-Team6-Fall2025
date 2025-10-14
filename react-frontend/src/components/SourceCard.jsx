import React, { useState } from 'react';
import axios from 'axios';
import { useOfflineStorage } from '../hooks/useOfflineStorage';

export default function SourceCard({ source, onDownloadSuccess }) {
  const [isSubscribed, setIsSubscribed] = useState(source.is_subscribed);
  const [subscriptionId, setSubscriptionId] = useState(source.subscription_id);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { status: offlineStatus, saveForOffline } = useOfflineStorage(
    {
      title: source.name,
      original_url: source.feed_url,
      feed_url: source.feed_url,
      source_id: source.id,
      get_type_display: source.get_type_display,
    },
    onDownloadSuccess
  );

  const handleSubscribeToggle = async () => {
    setIsSubmitting(true);
    
    const YOUR_AUTH_TOKEN = import.meta.env.VITE_SOME_API_KEY;
    const API_URL = 'http://localhost:8000/api/subscriptions/';
    
    try {
      if (isSubscribed) {
        await axios.delete(`${API_URL}${subscriptionId}/`, {
          headers: { 'Authorization': `Token ${YOUR_AUTH_TOKEN}` }
        });
        setIsSubscribed(false);
        setSubscriptionId(null);
      } else {
        const response = await axios.post(API_URL, { source: source.id }, {
          headers: { 'Authorization': `Token ${YOUR_AUTH_TOKEN}` }
        });
        setIsSubscribed(true);
        setSubscriptionId(response.data.id);
      }
    } catch (error) {
      console.error("Subscription toggle failed:", error.response?.data || error.message);
      alert("Subscription toggle failed. Check the console.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getOfflineButtonState = () => {
    switch (offlineStatus) {
      case 'saving': return { text: 'Saving...', disabled: true, className: 'btn-secondary' };
      case 'saved': return { text: '✓ Saved', disabled: true, className: 'btn-success' };
      case 'error': return { text: 'Retry Save', disabled: false, className: 'btn-danger' };
      default: return { text: 'Save for Offline', disabled: false, className: 'btn-outline-secondary' };
    }
  };
  const offlineBtn = getOfflineButtonState();

  return (
    <div className="col">
      <div className="card h-100 shadow-sm">
        <div className="card-body d-flex flex-column">
          <div className="d-flex justify-content-between align-items-start mb-2">
            <div className="fs-4">{source.type === 'podcast' ? '🎧' : '📰'}</div>
            <span className="badge rounded-pill text-bg-light">{source.get_type_display}</span>
          </div>

          <h5 className="card-title">{source.name}</h5>
          
          <div className="d-grid gap-2 mt-auto">
            <button
              className={`btn ${isSubscribed ? 'btn-success' : 'btn-primary'}`}
              onClick={handleSubscribeToggle}
              disabled={isSubmitting}
            >
              {isSubscribed ? 'Unsubscribe' : 'Subscribe'}
            </button>
            <button
              className={`btn ${offlineBtn.className}`}
              onClick={saveForOffline}
              disabled={offlineBtn.disabled}
            >
              {offlineBtn.text}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}