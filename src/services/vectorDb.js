// Chroma-based vector DB storage
const { ChromaClient } = require('chromadb');

const client = new ChromaClient();
const COLLECTION_NAME = 'documents';

async function getCollection() {
  // Create or get the collection
  return client.getOrCreateCollection({ name: COLLECTION_NAME });
}

async function saveVector(assetId, embedding, metadata) {
  const collection = await getCollection();
  await collection.upsert({
    ids: [assetId],
    embeddings: [embedding],
    metadatas: [metadata],
  });
}

async function loadVector(assetId) {
  const collection = await getCollection();
  const results = await collection.get({ ids: [assetId] });
  if (!results || !results.ids || results.ids.length === 0) {
    throw new Error('Document not found');
  }
  return {
    id: results.ids[0],
    embedding: results.embeddings[0],
    metadata: results.metadatas[0],
  };
}

module.exports = { saveVector, loadVector };
