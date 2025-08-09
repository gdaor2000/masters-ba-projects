document.addEventListener('DOMContentLoaded', function() {
    // Check if the 'cocktailOfTheDay' is already set in sessionStorage
    const savedDrink = sessionStorage.getItem('cocktailOfTheDay');

    if (savedDrink) {
        const drink = JSON.parse(savedDrink);
        displayCocktail(drink);
    } else {
        fetchCocktailOfTheDay();
    }

    function fetchCocktailOfTheDay() {
        fetch('/top-rated-cocktail')
        .then(response => response.json())
        .then(data => {
            const drink = data;
            sessionStorage.setItem('cocktailOfTheDay', JSON.stringify(drink));
            displayCocktail(drink);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('cocktailOfTheDay').innerHTML = `<p>Failed to load the top-rated cocktail. Please try again later.</p>`;
        });
    }

    function displayCocktail(drink) {
        // Call fetchAverageRating and wait for it to complete before setting innerHTML
        fetchAverageRating(drink.idDrink).then(avgData => {
            const container = document.getElementById('cocktailOfTheDay');
            let ingredientsList = '<ul>';
            for (let i = 1; i <= 15; i++) {
                const ingredient = drink[`strIngredient${i}`];
                if (ingredient) {
                    ingredientsList += `<li>${ingredient}: ${drink[`strMeasure${i}`] || ''}</li>`;
                }
            }
            ingredientsList += '</ul>';
    
            const ratingText = avgData.averageRating !== 'Not rated'
                ? `Average Rating: ${avgData.averageRating} (${avgData.ratingCount} ratings)`
                : 'Not yet rated';
    
            container.innerHTML = `
                <h3><a href='cocktail_info.html?id=${drink.idDrink}'style="text-decoration: none; color: inherit;">${drink.strDrink}</a></h3>
                <p>${ratingText}</p>
                <img src="${drink.strDrinkThumb}" alt="${drink.strDrink}" style="width:100%; height:auto;">
                <h4>Ingredients:</h4>
                ${ingredientsList}
                <h4>Instructions:</h4>
                <p>${drink.strInstructions}</p>
            `;
        })
        .catch(error => {
            console.error('Error fetching average rating:', error);
        });
    }
    
    function fetchAverageRating(cocktailId) {
        // Changed the function to return a promise that resolves to the avgData
        return fetch(`/average-rating/${cocktailId}`)
        .then(response => response.json())
        .then(avgData => {
            if (!avgData || avgData.error) {
                throw new Error('Failed to fetch average rating');
            }
            return avgData;
        })
        .catch(error => {
            console.error('Error fetching average rating:', error);
            // Return a fallback object to prevent further errors
            return { averageRating: 'Not rated', ratingCount: 0 };
        });
    }

    // Function to fetch and display cocktails by first letter
    function fetchCocktailsByLetter(letter) {
        fetch(`https://www.thecocktaildb.com/api/json/v1/1/search.php?f=${letter}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('listOfCocktails');
            if(data.drinks) {
                let htmlContent = `<ul>`;
                data.drinks.forEach(drink => {
                    htmlContent += `<li>${drink.strDrink}</li>`;
                });
                htmlContent += `</ul>`;
                container.innerHTML = htmlContent;
            } else {
                container.innerHTML = `<p>No cocktails found starting with '${letter}'.</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('listOfCocktails').innerHTML = `<p>Failed to load the list of cocktails. Please try again later.</p>`;
        });
    }

    // Generate clickable letters A-Z and add them to the DOM
    const lettersContainer = document.getElementById('letters');
    const letters = Array.from(Array(26)).map((e, i) => String.fromCharCode(i + 65));
    let lettersHTML = `<div>`;
    letters.forEach(letter => {
        lettersHTML += `<button class="letter-button">${letter}</button>`;
    });
    lettersHTML += `</div>`;
    lettersContainer.innerHTML = lettersHTML;

    // Attach event listeners to the letter buttons after they are added to the DOM
    const letterButtons = document.querySelectorAll('.letter-button');
    letterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const letter = button.textContent;
            fetchCocktailsByLetter(letter);
        });
    });
});