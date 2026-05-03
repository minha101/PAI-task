import requests
from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

# =============================================
# Groq API Configuration
# =============================================
GROQ_API_KEY = "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"   
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.1-8b-instant"           # Free model on Groq

# =============================================
# Helper: call Groq
# =============================================
def ask_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional chef and recipe expert. "
                    "When asked for a recipe, reply in this exact JSON format only — no extra text:\n"
                    '{"name":"...","ingredients":["...","..."],"steps":["...","..."],'
                    '"cook_time":"...","servings":"...","fun_fact":"..."}'
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# =============================================
# Simple HTML for testing (Lab 7 — minimal UI)
# =============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Lab 7 — Recipe App (Groq API)</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; background:#f5f5f5; }
        h1   { color: #ff6b35; }
        input, button { padding: 10px; margin: 5px; font-size: 1em; }
        button { background: #ff6b35; color: white; border: none; border-radius: 6px; cursor: pointer; }
        pre  { background: #fff; padding: 20px; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; }
        .note { background: #fff3cd; padding: 10px; border-radius: 6px; font-size: 0.85em; }
    </style>
</head>
<body>
    <h1>🍳 Recipe Finder — Lab 7 (Groq API)</h1>
    <p class="note">⚡ Powered by Groq AI (llama3-8b-8192) — real API calls!</p>

    <div>
        <input id="ingredient" placeholder="Enter ingredient e.g. chicken" style="width:280px">
        <button onclick="search()">Search Recipe</button>
        <button onclick="random()">Random Recipe</button>
    </div>

    <pre id="output">Results will appear here...</pre>

    <script>
        async function search() {
            const val = document.getElementById('ingredient').value;
            document.getElementById('output').textContent = 'Loading from Groq API...';
            const r = await fetch('/api/recipe?ingredient=' + encodeURIComponent(val));
            const d = await r.json();
            document.getElementById('output').textContent = JSON.stringify(d, null, 2);
        }
        async function random() {
            document.getElementById('output').textContent = 'Loading from Groq API...';
            const r = await fetch('/api/random');
            const d = await r.json();
            document.getElementById('output').textContent = JSON.stringify(d, null, 2);
        }
    </script>
</body>
</html>
"""

# =============================================
# Routes
# =============================================

@app.route('/')
def home():
    return render_template_string(HTML)


@app.route('/api/recipe')
def get_recipe():
    """Search a recipe by ingredient using Groq API."""
    ingredient = request.args.get('ingredient', '').strip()
    if not ingredient:
        return jsonify({"error": "Please provide an ingredient parameter"}), 400

    try:
        prompt = f"Give me a complete recipe that uses {ingredient} as the main ingredient."
        raw = ask_groq(prompt)

        # Try to parse JSON from Groq response
        import json, re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            recipe = json.loads(match.group())
        else:
            recipe = {"raw_response": raw}

        return jsonify({"status": "success", "ingredient": ingredient, "recipe": recipe})

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Groq API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/random')
def random_recipe():
    """Get a random recipe from Groq API."""
    cuisines = ["Italian", "Pakistani", "Mexican", "Japanese", "Indian", "French", "Chinese"]
    import random
    cuisine = random.choice(cuisines)

    try:
        prompt = f"Give me a popular traditional {cuisine} recipe."
        raw = ask_groq(prompt)

        import json, re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            recipe = json.loads(match.group())
        else:
            recipe = {"raw_response": raw}

        return jsonify({"status": "success", "cuisine": cuisine, "recipe": recipe})

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Groq API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/nutrition')
def nutrition_info():
    """Bonus: Ask Groq for nutrition facts about a dish."""
    dish = request.args.get('dish', '').strip()
    if not dish:
        return jsonify({"error": "Please provide a dish parameter"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a nutrition expert. Reply in this JSON format only:\n"
                        '{"dish":"...","calories_per_serving":"...","protein":"...",'
                        '"carbs":"...","fats":"...","health_tip":"..."}'
                    )
                },
                {"role": "user", "content": f"Give me nutrition facts for {dish}"}
            ],
            "max_tokens": 512
        }
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]

        import json, re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group()) if match else {"raw_response": raw}

        return jsonify({"status": "success", "nutrition": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================
# Run
# =============================================
if __name__ == '__main__':
    print("=" * 55)
    print("  Lab 7 — Recipe App  |  Groq API (llama-3.1-8b-instant)")
    print("=" * 55)
    print("  Open: http://127.0.0.1:5000")
    print()
    print("  API Endpoints:")
    print("  GET /api/recipe?ingredient=chicken")
    print("  GET /api/random")
    print("  GET /api/nutrition?dish=biryani")
    print("=" * 55)
    print("  ⚠  Set your Groq key at line 12 in this file!")
    print("     Get free key: https://console.groq.com")
    print("=" * 55)
    app.run(debug=True)
