document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('searchButton').addEventListener('click', function() {
        const searchValue = document.getElementById('searchInput').value;
        fetch(`https://www.thecocktaildb.com/api/json/v1/1/search.php?s=${searchValue}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = ''; // Clear previous results
            
            const ul = document.createElement('ul'); // Creating unordered list
            
            data.drinks.forEach(drink => {
                const li = document.createElement('li'); // Creating list 
                
                // Create anchor tag with the cocktail information page URL
                const anchor = document.createElement('a');
                anchor.href = `cocktail_info.html?id=${drink.idDrink}`;
                anchor.innerHTML = `<h3>${drink.strDrink}</h3>
                                    <img src="${drink.strDrinkThumb}" alt="Drink Image" style="max-width:100%;">`;
                
                // Append anchor tag to list item
                li.appendChild(anchor);
                ul.appendChild(li); // Append list item to unordered list
            });
            
            resultsContainer.appendChild(ul); // Append unordered list to results container
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});