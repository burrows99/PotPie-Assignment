const express = require('express');
const { hashPassword, comparePassword, generateToken, findUserByEmail } = require('../services/auth');
const db = require('../services/db');
const router = express.Router();

// Registration
router.post('/register', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
  const existing = await findUserByEmail(email);
  if (existing) return res.status(400).json({ error: 'Email already registered' });
  const password_hash = await hashPassword(password);
  const { rows } = await db.query(
    'INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email',
    [email, password_hash]
  );
  const user = rows[0];
  const token = generateToken(user);
  res.json({ token, user: { id: user.id, email: user.email } });
});

// Login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
  const user = await findUserByEmail(email);
  if (!user) return res.status(400).json({ error: 'Invalid credentials' });
  const valid = await comparePassword(password, user.password_hash);
  if (!valid) return res.status(400).json({ error: 'Invalid credentials' });
  const token = generateToken(user);
  res.json({ token, user: { id: user.id, email: user.email } });
});

module.exports = router;