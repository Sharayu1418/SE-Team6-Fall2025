import { openDB } from 'idb';

const DB_NAME = 'SmartCacheDB';
const DB_VERSION = 1;
const METADATA_STORE = 'contentMetadata';
const CACHE_NAME = 'SmartCacheMediaCache_v1';

// --- Database Setup ---
const dbPromise = openDB(DB_NAME, DB_VERSION, {
  upgrade(db) {
    if (!db.objectStoreNames.contains(METADATA_STORE)) {
      const store = db.createObjectStore(METADATA_STORE, { keyPath: 'original_url' });
      store.createIndex('status', 'status');
      store.createIndex('cached_at', 'cached_at');
    }
  },
});

/**
 * Downloads and stores a piece of content.
 * @param {object} metadata - e.g., { title, original_url, source_id, feed_url }
 */
export async function downloadAndStoreContent(metadata) {
  const cache = await caches.open(CACHE_NAME);
  const db = await dbPromise;

  const existing = await db.get(METADATA_STORE, metadata.original_url);
  if (existing && existing.status === 'ready') {
    console.log(`${metadata.title} is already saved.`);
    return { success: true, cached: true };
  }
  
  const response = await fetch(metadata.feed_url);
  if (!response.ok) throw new Error(`Fetch failed: ${response.statusText}`);
  await cache.put(metadata.feed_url, response);

  const updatedMetadata = {
    ...metadata,
    status: 'ready',
    cached_at: new Date(),
  };
  await db.put(METADATA_STORE, updatedMetadata);
  
  return { success: true, cached: false, metadata: updatedMetadata };
}

export async function getReadyDownloads() {
  const db = await dbPromise;
  // Get all items from the 'status' index that have the value 'ready'
  return db.getAllFromIndex(METADATA_STORE, 'status', 'ready');
}

/**
 * Deletes a piece of content from both stores.
 * @param {string} original_url - The unique URL of the content to delete.
 */
export async function deleteContent(original_url) {
  try {
    const cache = await caches.open(CACHE_NAME);
    const db = await dbPromise;

    await cache.delete(original_url); // Remove from Cache API
    await db.delete(METADATA_STORE, original_url); // Remove from IndexedDB
    
    console.log(`Deleted content: ${original_url}`);
    return { success: true };
  } catch (error) {
    console.error(`Failed to delete ${original_url}`, error);
    return { success: false };
  }
}