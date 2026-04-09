const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
const Task = require('./models/Task');
const User = require('./models/User');

const app = express();
const PORT = 3000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://mongo:27017/tasksdb';

// Parse JSON request bodies.
app.use(express.json());

// Serve static frontend files from the public folder.
app.use(express.static(path.join(__dirname, 'public')));

// Root route: show the website in browsers, keep plain text status for API clients.
app.get('/', (req, res) => {
  const acceptHeader = (req.get('accept') || '').toLowerCase();
  const acceptsHtml = acceptHeader.includes('text/html');

  if (acceptsHtml) {
    return res.sendFile(path.join(__dirname, 'public', 'index.html'));
  }

  res.type('text/plain').send('App is running');
});

// Sign up a new user.
app.post('/signup', async (req, res, next) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !name.trim() || !email || !email.trim() || !password || !password.trim()) {
      return res.status(400).json({ message: 'Name, email, and password are required.' });
    }

    const normalizedEmail = email.trim().toLowerCase();
    const existingUser = await User.findOne({ email: normalizedEmail });

    if (existingUser) {
      return res.status(409).json({ message: 'An account with this email already exists.' });
    }

    const user = await User.create({
      name: name.trim(),
      email: normalizedEmail,
      password: password.trim(),
    });

    res.status(201).json({
      message: 'Signup successful.',
      user: {
        _id: user._id,
        name: user.name,
        email: user.email,
      },
    });
  } catch (error) {
    next(error);
  }
});

// Log in an existing user.
app.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;

    if (!email || !email.trim() || !password || !password.trim()) {
      return res.status(400).json({ message: 'Email and password are required.' });
    }

    const user = await User.findOne({ email: email.trim().toLowerCase() });

    if (!user || user.password !== password.trim()) {
      return res.status(401).json({ message: 'Invalid email or password.' });
    }

    res.json({
      message: 'Login successful.',
      user: {
        _id: user._id,
        name: user.name,
        email: user.email,
      },
    });
  } catch (error) {
    next(error);
  }
});

function validateUserId(userId) {
  return !!userId && mongoose.Types.ObjectId.isValid(userId);
}

// Return all tasks from the database.
app.get('/tasks', async (req, res, next) => {
  try {
    const { userId } = req.query;

    if (!validateUserId(userId)) {
      return res.status(400).json({ message: 'A valid userId is required.' });
    }

    const tasks = await Task.find({ userId }).sort({ createdAt: -1 });
    res.json(tasks);
  } catch (error) {
    next(error);
  }
});

// Add a new task to the database.
app.post('/add', async (req, res, next) => {
  try {
    const { title, userId } = req.body;

    if (!validateUserId(userId)) {
      return res.status(400).json({ message: 'A valid userId is required.' });
    }

    if (!title || !title.trim()) {
      return res.status(400).json({ message: 'Task title is required.' });
    }

    const task = await Task.create({
      userId,
      title: title.trim(),
    });

    res.status(201).json({ message: 'Task added successfully.', task });
  } catch (error) {
    next(error);
  }
});

// Toggle a task between to-do and done for the current user.
app.patch('/tasks/:id/toggle', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { userId } = req.body;

    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ message: 'Invalid task id.' });
    }

    if (!validateUserId(userId)) {
      return res.status(400).json({ message: 'A valid userId is required.' });
    }

    const task = await Task.findOne({ _id: id, userId });

    if (!task) {
      return res.status(404).json({ message: 'Task not found.' });
    }

    task.completed = !task.completed;
    task.completedAt = task.completed ? new Date() : null;
    await task.save();

    res.json({ message: 'Task updated.', task });
  } catch (error) {
    next(error);
  }
});

// Delete a task for the current user.
app.delete('/tasks/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { userId } = req.body;

    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ message: 'Invalid task id.' });
    }

    if (!validateUserId(userId)) {
      return res.status(400).json({ message: 'A valid userId is required.' });
    }

    const task = await Task.findOneAndDelete({ _id: id, userId });

    if (!task) {
      return res.status(404).json({ message: 'Task not found.' });
    }

    res.json({ message: 'Task deleted successfully.' });
  } catch (error) {
    next(error);
  }
});

// Catch-all error handler so API failures return clean JSON.
app.use((error, req, res, next) => {
  console.error(error);
  res.status(500).json({ message: 'Something went wrong on the server.' });
});

// Keep trying to connect to MongoDB until the database is ready.
async function connectWithRetry() {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB');

    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  } catch (error) {
    console.error('MongoDB connection failed. Retrying in 5 seconds...');
    setTimeout(connectWithRetry, 5000);
  }
}

connectWithRetry();