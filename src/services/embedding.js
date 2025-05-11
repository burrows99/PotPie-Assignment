// Embedding service using @xenova/transformers
const { pipeline } = require('@xenova/transformers');

let embedder = null;

async function loadEmbedder() {
  if (!embedder) {
    embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  }
  return embedder;
}

async function createEmbedding(text) {
  const embed = await loadEmbedder();
  // The output is [1, tokens, 384], so we average across tokens
  const result = await embed(text, { pooling: 'mean', normalize: true });
  return Array.from(result.data);
}

module.exports = { createEmbedding };
