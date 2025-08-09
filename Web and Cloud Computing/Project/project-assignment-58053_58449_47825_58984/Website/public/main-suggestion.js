document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch a random cocktail and display it
    function fetchSuggestion() {
        fetch('/top-rated-cocktail-week')
        .then(response => response.json())
        .then(data => {
            const drink = data;
            sessionStorage.setItem('suggestion', JSON.stringify(drink)); // Save to sessionStorage
            displaySuggestion(drink);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('suggestion').innerHTML = `<p>Failed to load the top-rated cocktail of the week. Please try again later.</p>`;
        });
    }

    // Function to display the cocktail suggestion, now also displaying the rating
    async function displaySuggestion(drink) {
        const section = document.getElementById('suggestion');
        try {
            const avgData = await fetchAverageRating(drink.idDrink);
            const ratingText = avgData.averageRating !== 'Not rated'
                ? `Average Rating: ${avgData.averageRating} (${avgData.ratingCount} ratings)`
                : 'Not yet rated';
            section.innerHTML = `
                <h3><a href='cocktail_info.html?id=${drink.idDrink}' style="text-decoration: none; color: inherit;">${drink.strDrink}</a></h3>
                <p>${ratingText}</p>
                <img src="${drink.strDrinkThumb}" alt="Cocktail Image" style="max-width:50%;">
                <h3>Ingredients:</h3>
                <ul>${renderIngredients(drink)}</ul>
                <h3>Instructions:</h3>
                <p>${drink.strInstructions}</p>`;
        } catch (error) {
            console.error('Error fetching average rating:', error);
            section.innerHTML = `
                <h3>${drink.strDrink}</h3>
                <p>Rating not available.</p>
                <img src="${drink.strDrinkThumb}" alt="Cocktail Image">
                <h3>Ingredients:</h3>
                <ul>${renderIngredients(drink)}</ul>
                <h3>Instructions:</h3>
                <p>${drink.strInstructions}</p>`;
        }
    }

    function renderIngredients(cocktail) {
        let ingredientsList = '';
        for (let i = 1; i <= 15; i++) {
            const ingredient = cocktail[`strIngredient${i}`];
            const measure = cocktail[`strMeasure${i}`];
            if (ingredient) {
                ingredientsList += `<li>${measure ? measure.trim() + ' ' : ''}${ingredient}</li>`;
            }
        }
        return ingredientsList;
    }

    // Function to fetch the average rating of a cocktail
    async function fetchAverageRating(cocktailId) {
        try {
            const response = await fetch(`/average-rating/${cocktailId}`);
            const avgData = await response.json();
            if (!avgData || avgData.error) {
                throw new Error('Failed to fetch average rating');
            }
            return avgData;
        } catch (error) {
            console.error('Error fetching average rating:', error);
            return { averageRating: 'Not rated', ratingCount: 0 };
        }
    }

    // Initialize suggestion from sessionStorage or fetch a new one
    const savedSuggestion = sessionStorage.getItem('suggestion');
    if (savedSuggestion) {
        const drink = JSON.parse(savedSuggestion);
        displaySuggestion(drink);
    } else {
        fetchSuggestion();
    }

    // Fetch the list of ingredients
    fetch("https://www.thecocktaildb.com/api/json/v1/1/list.php?i=list")
    .then(response => response.json())
    .then(data => {
        const ingredients = data.drinks.map(drink => drink.strIngredient1);
        // Sort the ingredients alphabetically
        ingredients.sort();
        
        const ingredientSelect = document.getElementById('ingredientSelect');
        ingredients.forEach(ingredient => {
            const option = document.createElement('option');
            option.text = ingredient;
            option.value = ingredient;
            ingredientSelect.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Function to display search results for a given ingredient
    document.getElementById('searchButton').addEventListener('click', function() {
        const ingredient = document.getElementById('ingredientSelect').value;
        if (ingredient) {
            fetch(`https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=${ingredient}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data.drinks);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });

    // Function to render search results
    function displaySearchResults(drinks) {
        const resultsContainer = document.getElementById('searchResults');
        resultsContainer.innerHTML = ''; // Clear previous results

        if (drinks && drinks.length > 0) {
            const ul = document.createElement('ul');
            drinks.forEach(drink => {
                const li = document.createElement('li');
                const anchor = document.createElement('a');
                anchor.href = `cocktail_info.html?id=${drink.idDrink}`;
                anchor.innerHTML = `<h3>${drink.strDrink}</h3>
                                    <img src="${drink.strDrinkThumb}" alt="Drink Image" style="max-width:100%;">`;
                li.appendChild(anchor);
                ul.appendChild(li);
            });
            resultsContainer.appendChild(ul);
        } else {
            resultsContainer.innerHTML = '<p>No results found.</p>';
        }
    }

    // Define fetchMoodSuggestion function
    window.fetchMoodSuggestion = function(mood) {
        console.log("Fetching suggestion for mood: " + mood);
        // Fetch from your Node.js server endpoint with the mood parameter
        fetch(`/cocktail-by-mood?mood=${encodeURIComponent(mood)}`)
        .then(response => response.json())
        .then(data => {
            // Assuming you have a function to display the cocktail data
            displaySuggestion(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
