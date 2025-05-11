const express = require('express');
const cors = require('cors');
const documentsRouter = require('./routes/documents');
const authRouter = require('./routes/auth');
const chatRouter = require('./routes/chat');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api/documents', documentsRouter);
app.use('/api/auth', authRouter);
app.use('/api/chat', chatRouter);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

module.exports = app;
