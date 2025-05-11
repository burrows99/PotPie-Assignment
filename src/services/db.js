const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool(); // uses env vars

module.exports = {
  query: (text, params) => pool.query(text, params),
  getClient: () => pool.connect(),
};
