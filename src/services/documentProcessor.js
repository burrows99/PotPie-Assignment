const fs = require('fs/promises');
const path = require('path');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const { v4: uuidv4 } = require('uuid');
const { createEmbedding } = require('./embedding');
const { saveVector } = require('./vectorDb');

async function extractText(buffer, originalname) {
  const ext = path.extname(originalname).toLowerCase();
  if (ext === '.txt') {
    return buffer.toString('utf8');
  } else if (ext === '.pdf') {
    const pdf = await pdfParse(buffer);
    return pdf.text;
  } else if (ext === '.doc' || ext === '.docx') {
    const result = await mammoth.extractRawText({ buffer });
    return result.value;
  } else {
    throw new Error('Unsupported file type: ' + ext);
  }
}

async function processDocument(buffer, originalname) {
  // 1. Extract text
  const text = await extractText(buffer, originalname);
  // 2. Create embedding
  const embedding = await createEmbedding(text);
  // 3. Assign asset ID
  const assetId = uuidv4();
  // 4. Store embedding and metadata
  await saveVector(assetId, embedding, { filename: originalname });
  // 5. Return asset ID
  return assetId;
}

module.exports = { processDocument };
