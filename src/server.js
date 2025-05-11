const app = require('./app');
const PORT = process.env.PORT || 3000;

const { execSync } = require('child_process');
// ChromaDB connection check before starting server
const { ChromaClient } = require('chromadb');
const chromaClient = new ChromaClient({ path: 'http://localhost:8000' });

async function startOllamaIfNeeded() {
  try {
    // Check if Docker daemon is running
    try {
      execSync('docker info', { stdio: 'ignore' });
    } catch (e) {
      console.error('Docker daemon is not running. Please start Docker Desktop (or your Docker daemon) and try again.');
      process.exit(1);
    }
    // Check if an Ollama container is already running
    const result = execSync('docker ps --filter "ancestor=ollama/ollama" --format "{{.ID}}"').toString().trim();
    if (!result) {
      console.log('Starting Ollama in Docker...');
      execSync('docker run -d -p 11434:11434 --name ollama_server ollama/ollama');
    } else {
      console.log('Ollama Docker container already running.');
    }
  } catch (e) {
    console.error('Failed to start or check Ollama Docker container. Make sure Docker is installed and running.');
    process.exit(1);
  }
}

async function startChromaIfNeeded() {
  try {
    // Check if Docker daemon is running
    try {
      execSync('docker info', { stdio: 'ignore' });
    } catch (e) {
      console.error('Docker daemon is not running. Please start Docker Desktop (or your Docker daemon) and try again.');
      process.exit(1);
    }
    // Check if a chromadb container is already running
    const result = execSync('docker ps --filter "ancestor=chromadb/chroma" --format "{{.ID}}"').toString().trim();
    if (!result) {
      console.log('Starting ChromaDB in Docker...');
      execSync('docker run -d -p 8000:8000 chromadb/chroma');
    } else {
      console.log('ChromaDB Docker container already running.');
    }
  } catch (e) {
    console.error('Failed to start or check ChromaDB Docker container. Make sure Docker is installed and running.');
    process.exit(1);
  }
}

async function waitForChroma(timeout = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      await chromaClient.listCollections();
      return true;
    } catch (e) {
      await new Promise(res => setTimeout(res, 500));
    }
  }
  return false;
}

(async () => {
  await startOllamaIfNeeded();
  await startChromaIfNeeded();
  const ready = await waitForChroma();
  if (!ready) {
    console.error('Failed to connect to ChromaDB after starting Docker container.');
    process.exit(1);
  }
  console.log('Connected to ChromaDB successfully.');
  // Start Express server and attach all routes as configured in app.js
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
})();
