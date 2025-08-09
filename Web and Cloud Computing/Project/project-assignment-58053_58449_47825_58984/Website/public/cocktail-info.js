document.addEventListener('DOMContentLoaded', function() {
    // Initialize or retrieve the rated cocktails list from the session storage
    let ratedCocktails = sessionStorage.getItem('ratedCocktails') ? JSON.parse(sessionStorage.getItem('ratedCocktails')) : [];
    const urlParams = new URLSearchParams(window.location.search);
    const cocktailId = urlParams.get('id');

    // Fetch and display cocktail details
    fetchCocktailDetails(cocktailId);

    // Event listener for the submit rating button
    document.getElementById('submitRating').addEventListener('click', function() {
        submitCocktailRating(cocktailId, ratedCocktails);
    });
});

function fetchCocktailDetails(cocktailId) {
    fetch(`https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=${cocktailId}`)
    .then(response => response.json())
    .then(data => {
        const cocktail = data.drinks[0];
        const cocktailInfoContainer = document.getElementById('cocktailInfo');
        cocktailInfoContainer.innerHTML = `
            <h2>${cocktail.strDrink}</h2>
            <img src="${cocktail.strDrinkThumb}" alt="Cocktail Image">
            <h3>Ingredients:</h3>
            <ul>${renderIngredients(cocktail)}</ul>
            <h3>Instructions:</h3>
            <p>${cocktail.strInstructions}</p>
        `;
        fetchAverageRating(cocktailId);
    })
    .catch(error => {
        console.error('Error:', error);
    });
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

function fetchAverageRating(cocktailId) {
    fetch(`/average-rating/${cocktailId}`)
    .then(response => response.json())
    .then(avgData => {
        const cocktailInfoContainer = document.getElementById('cocktailInfo');
        const avgRatingDisplay = document.createElement('p');
        const ratingText = avgData.averageRating !== 'Not rated'
            ? `Rating: ${avgData.averageRating}/5 (Rated ${avgData.ratingCount} times)`
            : 'Not rated';
        avgRatingDisplay.textContent = ratingText;
        cocktailInfoContainer.insertBefore(avgRatingDisplay, cocktailInfoContainer.children[1]);
    })
    .catch(error => console.error('Error fetching average rating:', error));
}

function submitCocktailRating(cocktailId, ratedCocktails) {
    const rating = document.querySelector('input[name="rating"]:checked').value;
    const today = new Date().toISOString().slice(0, 10);

    // Prevent duplicate ratings in the same session
    if (ratedCocktails.includes(cocktailId)) {
        alert('You have already rated this cocktail in this session.');
        return;
    }

    fetch('/submit-rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: cocktailId,
            rating: rating,
            date: today,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert('Rating submitted successfully!');
            ratedCocktails.push(cocktailId);
            sessionStorage.setItem('ratedCocktails', JSON.stringify(ratedCocktails));
            // Optionally, refresh the average rating
            fetchAverageRating(cocktailId);
            // Reload the page
            location.reload();
        } else {
            alert(data.warning || 'Unexpected response from the server.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
