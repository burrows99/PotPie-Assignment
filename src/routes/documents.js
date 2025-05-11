const express = require('express');
const multer = require('multer');
const router = express.Router();
const { processDocument } = require('../services/documentProcessor');
const authMiddleware = require('../middleware/auth');

const upload = multer(); // memory storage

// POST /api/documents/process
router.post('/process', authMiddleware, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded.' });
    const assetId = await processDocument(req.file.buffer, req.file.originalname, req.user.id);
    res.json({ assetId });
  } catch (err) {
    console.error('Error processing document:', err);
    res.status(500).json({ error: 'Failed to process document.' });
  }
});

module.exports = router;
