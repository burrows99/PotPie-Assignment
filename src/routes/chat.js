const express = require('express');
const authMiddleware = require('../middleware/auth');
const db = require('../services/db');
const { loadVector } = require('../services/vectorDb');
const { chatWithOllama } = require('../services/ollama');
const router = express.Router();

// Fetch all threads for user
router.get('/threads', authMiddleware, async (req, res) => {
  const { rows } = await db.query(
    'SELECT * FROM chat_threads WHERE user_id = $1 ORDER BY created_at DESC',
    [req.user.id]
  );
  res.json(rows);
});

// Fetch messages for a thread
router.get('/threads/:threadId/messages', authMiddleware, async (req, res) => {
  const { threadId } = req.params;
  const { rows } = await db.query(
    'SELECT * FROM chat_messages WHERE thread_id = $1 ORDER BY created_at ASC',
    [threadId]
  );
  res.json(rows);
});

// Chat with LLM and (optionally) asset context
router.post('/chat', authMiddleware, async (req, res) => {
  const { message, assetIds } = req.body;
  if (!message) return res.status(400).json({ error: 'Missing message' });

  let context = '';
  if (Array.isArray(assetIds) && assetIds.length > 0) {
    try {
      // Fetch all asset contexts and concatenate
      const contexts = await Promise.all(assetIds.map(async (id) => {
        try {
          const doc = await loadVector(id);
          // Use both metadata and embedding if needed, here just metadata
          return doc.metadata && doc.metadata.text ? doc.metadata.text : JSON.stringify(doc.metadata);
        } catch (e) {
          return '';
        }
      }));
      context = contexts.filter(Boolean).join('\n---\n');
    } catch (e) {
      // Ignore context errors
    }
  }

  try {
    const llmResponse = await chatWithOllama({ prompt: message, context });
    res.json({ response: llmResponse });
  } catch (e) {
    res.status(500).json({ error: 'LLM error', details: e.message });
  }
});

module.exports = router;