// Simple Ollama client for LLM chat
const axios = require('axios');

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const MODEL = 'tinyllama';

async function chatWithOllama({ prompt, context }) {
  // Compose the prompt with context if provided
  let fullPrompt = prompt;
  if (context) {
    fullPrompt = `Context:\n${context}\n\nUser: ${prompt}`;
  }
  const response = await axios.post(`${OLLAMA_URL}/api/generate`, {
    model: MODEL,
    prompt: fullPrompt,
    stream: false
  });
  return response.data.response;
}

module.exports = { chatWithOllama };
