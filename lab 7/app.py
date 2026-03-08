import requests
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Free API from TheMealDB (no API key needed)
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Recipe App</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #fff5e6; padding: 20px; border-radius: 10px; }
        .recipe-card { 
            background: white; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .recipe-title { font-size: 1.5em; color: #ff6b35; }
        .recipe-image { max-width: 200px; border-radius: 5px; }
        .ingredients { background: #f9f9f9; padding: 10px; border-radius: 5px; }
        input, button { padding: 10px; margin: 5px; }
        .search-box { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍳 Recipe Finder</h1>
        
        <div class="search-box">
            <input type="text" id="ingredient" placeholder="Enter ingredient (e.g., chicken)">
            <button onclick="searchRecipes()">Search Recipes</button>
            <button onclick="getRandomRecipe()">Random Recipe</button>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        async function searchRecipes() {
            const ingredient = document.getElementById('ingredient').value;
            if (!ingredient) {
                alert('Please enter an ingredient');
                return;
            }
            
            const response = await fetch(`/recipes?ingredient=${ingredient}`);
            const data = await response.json();
            displayRecipes(data);
        }
        
        async function getRandomRecipe() {
            const response = await fetch('/random-recipe');
            const data = await response.json();
            displayRecipes(data);
        }
        
        function displayRecipes(data) {
            let html = '';
            
            if (data.error) {
                html = `<p>Error: ${data.error}</p>`;
            } else if (data.meals) {
                data.meals.forEach(recipe => {
                    html += `
                        <div class="recipe-card">
                            <h2 class="recipe-title">${recipe.name}</h2>
                            <img src="${recipe.image}" class="recipe-image">
                            <p><strong>Category:</strong> ${recipe.category}</p>
                            <p><strong>Area:</strong> ${recipe.area}</p>
                            
                            <div class="ingredients">
                                <h3>Ingredients:</h3>
                                <ul>
                                    ${recipe.ingredients.map(ing => `<li>${ing}</li>`).join('')}
                                </ul>
                            </div>
                            
                            <h3>Instructions:</h3>
                            <p>${recipe.instructions}</p>
                            
                            <a href="${recipe.source}" target="_blank">View Full Recipe</a>
                        </div>
                    `;
                });
            } else {
                html = '<p>No recipes found</p>';
            }
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/recipes')
def search_recipes():
    ingredient = request.args.get('ingredient')
    
    if not ingredient:
        return jsonify({'error': 'Please provide an ingredient'})
    
    try:
        # Search recipes by ingredient
        url = f"{BASE_URL}/filter.php?i={ingredient}"
        response = requests.get(url)
        data = response.json()
        
        if data.get('meals'):
            recipes = []
            # Get details for first 5 recipes
            for meal in data['meals'][:5]:
                detail_url = f"{BASE_URL}/lookup.php?i={meal['idMeal']}"
                detail_response = requests.get(detail_url)
                detail_data = detail_response.json()
                
                if detail_data.get('meals'):
                    meal_detail = detail_data['meals'][0]
                    
                    # Extract ingredients
                    ingredients = []
                    for i in range(1, 21):
                        ing = meal_detail.get(f'strIngredient{i}')
                        measure = meal_detail.get(f'strMeasure{i}')
                        if ing and ing.strip():
                            ingredients.append(f"{measure} {ing}".strip())
                    
                    recipes.append({
                        'name': meal_detail['strMeal'],
                        'category': meal_detail['strCategory'],
                        'area': meal_detail['strArea'],
                        'instructions': meal_detail['strInstructions'][:300] + '...',
                        'image': meal_detail['strMealThumb'],
                        'source': meal_detail['strSource'] or '#',
                        'ingredients': ingredients[:10]  # Limit to 10 ingredients
                    })
            
            return jsonify({'meals': recipes})
        else:
            return jsonify({'error': 'No recipes found'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/random-recipe')
def random_recipe():
    try:
        url = f"{BASE_URL}/random.php"
        response = requests.get(url)
        data = response.json()
        
        if data.get('meals'):
            meal = data['meals'][0]
            
            # Extract ingredients
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f'strIngredient{i}')
                measure = meal.get(f'strMeasure{i}')
                if ing and ing.strip():
                    ingredients.append(f"{measure} {ing}".strip())
            
            recipe = [{
                'name': meal['strMeal'],
                'category': meal['strCategory'],
                'area': meal['strArea'],
                'instructions': meal['strInstructions'][:500] + '...',
                'image': meal['strMealThumb'],
                'source': meal['strSource'] or '#',
                'ingredients': ingredients[:15]
            }]
            
            return jsonify({'meals': recipe})
        else:
            return jsonify({'error': 'Failed to get random recipe'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)