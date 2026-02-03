// Database configuration for direct PostgreSQL connection
// WARNING: This exposes database credentials in the browser. Use only for development/internal tools.

import postgres from 'postgres';

// PostgreSQL connection configuration
const sql = postgres({
    host: '127.0.0.1',
    port: 5432,
    database: 'bqs',
    username: 'postgres',
    password: 'Abcd1234',
    // For browser compatibility, you may need to use a proxy or pg-browser
});

export default sql;
