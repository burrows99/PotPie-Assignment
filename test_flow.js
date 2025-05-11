const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const { spawn } = require('child_process');
const SERVER_URL = 'http://localhost:3000';

async function waitForServer(url, timeout = 10000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      await axios.get(`${url}/api/health`);
      return true;
    } catch (e) {
      await new Promise(res => setTimeout(res, 500));
    }
  }
  throw new Error('Server did not start in time');
}

async function registerUser(email, password) {
  const res = await axios.post(`${SERVER_URL}/api/auth/register`, { email, password });
  return res.data;
}

async function loginUser(email, password) {
  const res = await axios.post(`${SERVER_URL}/api/auth/login`, { email, password });
  return res.data.token;
}

async function uploadDocument(token, filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  const res = await axios.post(`${SERVER_URL}/api/documents/process`, form, {
    headers: { ...form.getHeaders(), Authorization: `Bearer ${token}` }
  });
  return res.data.assetId;
}

async function getThreads(token) {
  const res = await axios.get(`${SERVER_URL}/api/chat/threads`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data;
}

async function getMessages(token, threadId) {
  const res = await axios.get(`${SERVER_URL}/api/chat/threads/${threadId}/messages`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data;
}

async function main() {
  // Start server as a child process
  console.log('Starting server...');
  const serverProcess = spawn('node', ['src/server.js'], { stdio: 'inherit' });
  await waitForServer(SERVER_URL);

  try {
    // 1. Register two users
    console.log('Registering users...');
    await registerUser('user1@example.com', 'password123');
    await registerUser('user2@example.com', 'password123');

    // 2. Login as user 1
    console.log('Logging in as user 1...');
    const token1 = await loginUser('user1@example.com', 'password123');

    // 3. User 1 uploads a document
    console.log('User 1 uploading document...');
    const assetId1 = await uploadDocument(token1, 'test1.pdf');
    console.log('User 1 assetId:', assetId1);

    // 4. User 1 queries chat threads and messages
    const threads1 = await getThreads(token1);
    console.log('User 1 threads:', threads1);
    if (threads1.length > 0) {
      const messages1 = await getMessages(token1, threads1[0].id);
      console.log('User 1 messages:', messages1);
    }

    // 5. Login as user 2
    console.log('Logging in as user 2...');
    const token2 = await loginUser('user2@example.com', 'password123');

    // 6. User 2 uploads a document
    console.log('User 2 uploading document...');
    const assetId2 = await uploadDocument(token2, 'test2.pdf');
    console.log('User 2 assetId:', assetId2);

    // 7. User 2 queries chat threads and messages
    const threads2 = await getThreads(token2);
    console.log('User 2 threads:', threads2);
    if (threads2.length > 0) {
      const messages2 = await getMessages(token2, threads2[0].id);
      console.log('User 2 messages:', messages2);
    }
  } finally {
    // Kill the server process after tests
    serverProcess.kill();
  }
}

main().catch(err => {
  console.error('Test script error:', err.response ? err.response.data : err);
});