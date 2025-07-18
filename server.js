const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-here';

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false // Allow inline styles for demo
}));

// Trust proxy for rate limiting
app.set('trust proxy', 1);

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// CORS and body parsing
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Database setup
const db = new sqlite3.Database('./hackathon.db');

// Initialize database tables
db.serialize(() => {
  // Users table
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT NOT NULL,
      phone TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Carpooling rides table
  db.run(`
    CREATE TABLE IF NOT EXISTS carpool_rides (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      origin TEXT NOT NULL,
      destination TEXT NOT NULL,
      departure_time DATETIME NOT NULL,
      available_seats INTEGER NOT NULL,
      price_per_seat DECIMAL(10,2),
      description TEXT,
      status TEXT DEFAULT 'active',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // Travel buddies table
  db.run(`
    CREATE TABLE IF NOT EXISTS travel_plans (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      destination TEXT NOT NULL,
      start_date DATE NOT NULL,
      end_date DATE NOT NULL,
      description TEXT,
      budget_range TEXT,
      interests TEXT,
      status TEXT DEFAULT 'active',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // Historical sites table
  db.run(`
    CREATE TABLE IF NOT EXISTS historical_sites (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      location TEXT NOT NULL,
      description TEXT NOT NULL,
      historical_period TEXT,
      interesting_facts TEXT,
      visit_info TEXT,
      image_url TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Insert sample historical sites
  db.run(`
    INSERT OR IGNORE INTO historical_sites (name, location, description, historical_period, interesting_facts, visit_info, image_url)
    VALUES 
    ('Ancient Town Square', 'Downtown District', 'A historic town square that served as the heart of commerce and community gatherings for over 200 years.', '1800-1900', 'The original cobblestones were imported from Europe. The central fountain was built in 1845 and still functions today.', 'Open 24/7, free guided tours available on weekends at 2 PM', '/images/town-square.jpg'),
    ('Old Mill Museum', 'Riverside Park', 'A restored 19th-century grist mill that powered the early industrial development of the area.', '1820-1920', 'The mill wheel is 20 feet in diameter and can still turn. It ground grain for the entire region for 80 years.', 'Open Wed-Sun 10 AM-4 PM, admission $5', '/images/old-mill.jpg'),
    ('Heritage Library', 'Main Street', 'The citys first public library, built in 1889 with Carnegie funding, featuring original Victorian architecture.', '1889-present', 'Andrew Carnegie donated $25,000 for its construction. The reading room still has the original oak tables and brass lamps.', 'Open Mon-Fri 9 AM-8 PM, Sat 10 AM-5 PM, free admission', '/images/heritage-library.jpg'),
    ('Railway Station Monument', 'Station District', 'The preserved platform and station house from the original railway line that connected the town to major cities.', '1875-1960', 'Over 1 million passengers passed through this station. The last train departed in 1960 when the line was discontinued.', 'Outdoor monument, accessible 24/7, information plaques available', '/images/railway-station.jpg'),
    ('Founders Memorial Park', 'Park Avenue', 'A park dedicated to the three founding families, featuring monuments and the original settlement site.', '1799-1850', 'The oak tree in the center was planted by the first mayor in 1801 and is now over 220 years old.', 'Open sunrise to sunset, free admission, picnic areas available', '/images/founders-park.jpg')
  `);
});

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Routes

// Root route - serve homepage
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// User Registration
app.post('/api/register', async (req, res) => {
  try {
    const { email, password, name, phone } = req.body;

    if (!email || !password || !name) {
      return res.status(400).json({ message: 'Email, password, and name are required' });
    }

    // Check if user already exists
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
      if (err) {
        return res.status(500).json({ message: 'Database error' });
      }

      if (user) {
        return res.status(400).json({ message: 'User already exists' });
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 10);

      // Insert user
      db.run(
        'INSERT INTO users (email, password, name, phone) VALUES (?, ?, ?, ?)',
        [email, hashedPassword, name, phone],
        function(err) {
          if (err) {
            return res.status(500).json({ message: 'Error creating user' });
          }

          const token = jwt.sign({ userId: this.lastID, email }, JWT_SECRET, { expiresIn: '24h' });
          res.status(201).json({ token, user: { id: this.lastID, email, name, phone } });
        }
      );
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// User Login
app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required' });
    }

    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
      if (err) {
        return res.status(500).json({ message: 'Database error' });
      }

      if (!user) {
        return res.status(400).json({ message: 'Invalid credentials' });
      }

      const isValidPassword = await bcrypt.compare(password, user.password);
      if (!isValidPassword) {
        return res.status(400).json({ message: 'Invalid credentials' });
      }

      const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '24h' });
      res.json({ 
        token, 
        user: { 
          id: user.id, 
          email: user.email, 
          name: user.name, 
          phone: user.phone 
        } 
      });
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Carpool Routes
app.post('/api/carpool/rides', authenticateToken, (req, res) => {
  const { origin, destination, departure_time, available_seats, price_per_seat, description } = req.body;

  if (!origin || !destination || !departure_time || !available_seats) {
    return res.status(400).json({ message: 'All required fields must be provided' });
  }

  db.run(
    'INSERT INTO carpool_rides (user_id, origin, destination, departure_time, available_seats, price_per_seat, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [req.user.userId, origin, destination, departure_time, available_seats, price_per_seat, description],
    function(err) {
      if (err) {
        return res.status(500).json({ message: 'Error creating ride' });
      }
      res.status(201).json({ id: this.lastID, message: 'Ride created successfully' });
    }
  );
});

app.get('/api/carpool/rides', (req, res) => {
  const { origin, destination } = req.query;
  
  let query = `
    SELECT r.*, u.name as driver_name, u.phone as driver_phone 
    FROM carpool_rides r 
    JOIN users u ON r.user_id = u.id 
    WHERE r.status = 'active'
  `;
  let params = [];

  if (origin) {
    query += ' AND r.origin LIKE ?';
    params.push(`%${origin}%`);
  }

  if (destination) {
    query += ' AND r.destination LIKE ?';
    params.push(`%${destination}%`);
  }

  query += ' ORDER BY r.departure_time ASC';

  db.all(query, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ message: 'Error fetching rides' });
    }
    res.json(rows);
  });
});

// Travel Buddy Routes
app.post('/api/travel/plans', authenticateToken, (req, res) => {
  const { destination, start_date, end_date, description, budget_range, interests } = req.body;

  if (!destination || !start_date || !end_date) {
    return res.status(400).json({ message: 'Destination, start date, and end date are required' });
  }

  db.run(
    'INSERT INTO travel_plans (user_id, destination, start_date, end_date, description, budget_range, interests) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [req.user.userId, destination, start_date, end_date, description, budget_range, interests],
    function(err) {
      if (err) {
        return res.status(500).json({ message: 'Error creating travel plan' });
      }
      res.status(201).json({ id: this.lastID, message: 'Travel plan created successfully' });
    }
  );
});

app.get('/api/travel/plans', (req, res) => {
  const { destination } = req.query;
  
  let query = `
    SELECT t.*, u.name as traveler_name, u.phone as traveler_phone 
    FROM travel_plans t 
    JOIN users u ON t.user_id = u.id 
    WHERE t.status = 'active'
  `;
  let params = [];

  if (destination) {
    query += ' AND t.destination LIKE ?';
    params.push(`%${destination}%`);
  }

  query += ' ORDER BY t.start_date ASC';

  db.all(query, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ message: 'Error fetching travel plans' });
    }
    res.json(rows);
  });
});

// Historical Sites Routes
app.get('/api/historical/sites', (req, res) => {
  const { location } = req.query;
  
  let query = 'SELECT * FROM historical_sites';
  let params = [];

  if (location) {
    query += ' WHERE location LIKE ?';
    params.push(`%${location}%`);
  }

  query += ' ORDER BY name ASC';

  db.all(query, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ message: 'Error fetching historical sites' });
    }
    res.json(rows);
  });
});

app.get('/api/historical/sites/:id', (req, res) => {
  const { id } = req.params;

  db.get('SELECT * FROM historical_sites WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ message: 'Error fetching site details' });
    }
    if (!row) {
      return res.status(404).json({ message: 'Site not found' });
    }
    res.json(row);
  });
});

// Catch all handler for client-side routing - moved to end of file
// app.get('/*', (req, res) => {
//   res.sendFile(path.join(__dirname, 'public', 'index.html'));
// });

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something went wrong!' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on port ${PORT}`);
});