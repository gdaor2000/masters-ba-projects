const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const fetch = require('node-fetch'); // assuming you're using node-fetch v2.x

const app = express();
const PORT = process.env.PORT || 3000;
const db = new sqlite3.Database('./db/cocktails.db', (err) => {
  if (err) {
    console.error(err.message);
    throw err;
  }
  console.log('Connected to the SQLite database.');
});

app.use(express.static('public'));
app.use(express.json());

app.get('/cocktail-by-mood', (req, res) => {
  const mood = req.query.mood;
  const query = 'SELECT ID FROM Moods WHERE Mood = ? ORDER BY RANDOM() LIMIT 1';

  // Execute the query against the database
  db.get(query, [mood], (err, row) => {
    if (err) {
      console.log(err)
      res.status(500).send('Error fetching from the database');
      return;
    }
    if (row) {
      const apiURL = `https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=${row.ID}`;
      fetch(apiURL)
        .then(response => response.json())
        .then(data => {
          if (data.drinks && data.drinks.length > 0) {
            res.json(data.drinks[0]); // Send the cocktail data back to the client
          } else {
            res.status(404).send('Cocktail not found');
          }
        })
        .catch(apiError => {
          res.status(500).send('Error fetching from the API');
        });
    } else {
      res.status(404).send('No cocktails found for this mood');
    }
  });
});

app.post('/submit-rating', (req, res) => {
    const { id, rating, date } = req.body;
    const sql = `INSERT INTO CocktailRatings (cocktail_id, rating, rated_date) VALUES (?, ?, ?)`;
    
    db.run(sql, [id, rating, date], function(err) {
        if (err) {
            console.error(err.message);
            res.status(500).send('Error saving the rating');
            return;
        }
        res.json({ message: 'Rating submitted successfully' });
    });
});

app.get('/average-rating/:cocktailId', (req, res) => {
  const { cocktailId } = req.params;
  const sql = `
    SELECT AVG(rating) as avgRating, COUNT(rated_date) as ratingCount 
    FROM CocktailRatings 
    WHERE cocktail_id = ?
  `;

  db.get(sql, [cocktailId], (err, row) => {
    console.log(row)
      if (err) {
          console.error(err.message);
          res.status(500).json({ error: 'Error fetching average rating' });
          return;
      }
      res.json({ 
        averageRating: row && row.avgRating ? row.avgRating.toFixed(2) : 'Not rated',
        ratingCount: row ? row.ratingCount : 0
      });
  });
});

app.get('/top-rated-cocktail', (req, res) => {
  const now = new Date();
  const currentMonth = now.getMonth() + 1;
  const currentYear = now.getFullYear();

  const query = `
    SELECT cocktail_id, AVG(rating) as avgRating
    FROM CocktailRatings
    WHERE strftime('%m', rated_date) = $1 AND strftime('%Y', rated_date) = $2
    GROUP BY cocktail_id
    ORDER BY avgRating DESC
    LIMIT 1;
  `;

  db.get(query, [currentMonth.toString().padStart(2, '0'), currentYear.toString()], (err, row) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error fetching the top-rated cocktail for the current month');
      return;
    }
    if (row) {
      const apiURL = `https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=${row.cocktail_id}`;
      fetch(apiURL)
        .then(response => response.json())
        .then(data => {
          if (data.drinks && data.drinks.length > 0) {
            res.json(data.drinks[0]);
          } else {
            res.status(404).send('Cocktail not found');
          }
        })
        .catch(apiError => {
          console.error(apiError);
          res.status(500).send('Error fetching from the API');
        });
    } else {
      res.status(404).send('No top-rated cocktails found for the current month');
    }
  });
});

app.get('/top-rated-cocktail-week', (req, res) => {
  const now = new Date();
  const firstDayOfWeek = new Date(now.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1))); // Adjust for Sunday start
  const lastDayOfWeek = new Date(firstDayOfWeek);
  lastDayOfWeek.setDate(firstDayOfWeek.getDate() + 6);

  const query = `
    SELECT cocktail_id, AVG(rating) as avgRating
    FROM CocktailRatings
    WHERE rated_date BETWEEN date(?) AND date(?)
    GROUP BY cocktail_id
    ORDER BY avgRating DESC
    LIMIT 1;
  `;

  db.get(query, [firstDayOfWeek.toISOString().split('T')[0], lastDayOfWeek.toISOString().split('T')[0]], (err, row) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error fetching the top-rated cocktail for the current week');
      return;
    }
    if (row) {
      const apiURL = `https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=${row.cocktail_id}`;
      fetch(apiURL)
        .then(response => response.json())
        .then(data => {
          if (data.drinks && data.drinks.length > 0) {
            res.json(data.drinks[0]);
          } else {
            res.status(404).send('Cocktail not found');
          }
        })
        .catch(apiError => {
          console.error(apiError);
          res.status(500).send('Error fetching from the API');
        });
    } else {
      res.status(404).send('No top-rated cocktails found for the current week');
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

