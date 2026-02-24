const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DB_FILE = path.join(__dirname, 'orders.db.json');

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize DB file if not exists
if (!fs.existsSync(DB_FILE)) {
    fs.writeFileSync(DB_FILE, JSON.stringify([]));
}

// Routes
// 1. Get all orders (for admin)
app.get('/api/orders', (req, res) => {
    try {
        const data = fs.readFileSync(DB_FILE, 'utf8');
        res.json(JSON.parse(data));
    } catch (err) {
        res.status(500).json({ error: 'Failed to read orders' });
    }
});

// 2. Place a new order
app.post('/api/orders', (req, res) => {
    try {
        const newOrder = req.body;
        const data = fs.readFileSync(DB_FILE, 'utf8');
        const orders = JSON.parse(data);

        orders.push({
            ...newOrder,
            id: Date.now().toString(),
            timestamp: new Date().toISOString()
        });

        fs.writeFileSync(DB_FILE, JSON.stringify(orders, null, 2));
        res.status(201).json({ message: 'Order placed successfully', id: newOrder.id });
    } catch (err) {
        res.status(500).json({ error: 'Failed to save order' });
    }
});

// 3. Reset all orders (admin)
app.delete('/api/orders', (req, res) => {
    try {
        fs.writeFileSync(DB_FILE, JSON.stringify([]));
        res.json({ message: 'All orders cleared' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to clear orders' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
