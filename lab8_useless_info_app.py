import requests
import random
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# =============================================
# Groq API Configuration
# =============================================
GROQ_API_KEY = "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"  
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama3-8b-8192"           # Free model on Groq

# =============================================
# Helper: call Groq
# =============================================
def ask_groq(category: str) -> dict:
    category_prompts = {
        "random":  "Give me one completely random, weird, and useless but true fact.",
        "animal":  "Give me one bizarre, funny, and true fact about any animal.",
        "food":    "Give me one surprising, weird, and true fact about any food.",
        "space":   "Give me one mind-blowing and true fact about space or the universe.",
        "history": "Give me one strange and true historical fact that most people don't know.",
        "science": "Give me one weird and true science fact that sounds unbelievable."
    }

    prompt = category_prompts.get(category, category_prompts["random"])

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
                    "You are a fun trivia expert. Reply in this exact JSON format ONLY, no extra text:\n"
                    '{"fact":"your fact here","wow_level":"1-10","source_hint":"brief source or context"}'
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 300
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# =============================================
# Full Dynamic HTML Template (Lab 8)
# =============================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Useless Info Hub — Groq AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', 'Comic Sans MS', cursive, sans-serif;
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            max-width: 820px;
            width: 100%;
            background: rgba(255, 255, 255, 0.97);
            border-radius: 40px;
            padding: 40px;
            box-shadow: 0 30px 70px rgba(0,0,0,0.3);
        }

        h1 {
            text-align: center;
            color: #FF6B6B;
            font-size: 2.5em;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 0.95em;
        }

        .groq-badge {
            background: linear-gradient(90deg, #7c3aed, #4f46e5);
            color: white;
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.8em;
            display: inline-block;
            margin: 0 auto 20px auto;
            display: block;
            width: fit-content;
            margin: 0 auto 25px auto;
        }

        .info-box {
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            padding: 40px 30px;
            border-radius: 30px;
            margin: 20px 0;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            border: 3px dashed rgba(255,255,255,0.8);
            transition: opacity 0.3s;
            position: relative;
        }

        .emoji-large {
            font-size: 4.5em;
            margin-bottom: 15px;
            animation: bounce 2.5s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50%       { transform: translateY(-15px); }
        }

        .info-text {
            font-size: 1.25em;
            line-height: 1.7;
            color: #333;
            margin: 10px 0;
            font-weight: 500;
        }

        .meta-row {
            display: flex;
            gap: 12px;
            margin-top: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .badge {
            padding: 7px 20px;
            border-radius: 30px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }

        .badge-category { background: #4ECDC4; }
        .badge-wow      { background: #FF6B6B; }
        .badge-source   { background: #A8D8EA; color: #333; }

        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 14px;
            margin: 28px 0;
        }

        .btn {
            padding: 18px 10px;
            border: none;
            border-radius: 18px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.25s;
            color: white;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }

        .btn:hover:not(:disabled) {
            transform: translateY(-5px);
            box-shadow: 0 12px 28px rgba(0,0,0,0.25);
        }

        .btn:disabled { opacity: 0.6; cursor: not-allowed; }

        .btn-random  { background: #FF6B6B; }
        .btn-animal  { background: #4ECDC4; }
        .btn-food    { background: #FDA085; }
        .btn-space   { background: #6C63FF; }
        .btn-history { background: #AA96DA; }
        .btn-science { background: #43AA8B; }

        /* Loading overlay inside info-box */
        .loading-overlay {
            display: none;
            position: absolute;
            inset: 0;
            background: rgba(255,255,255,0.85);
            border-radius: 27px;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-size: 1.1em;
            color: #555;
        }

        .loading-overlay.show { display: flex; }

        .spinner {
            width: 52px; height: 52px;
            border: 6px solid #f3f3f3;
            border-top: 6px solid #FF6B6B;
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
            margin-bottom: 12px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .counter-bar {
            background: linear-gradient(90deg, #FF6B6B, #fda085);
            color: white;
            padding: 12px 20px;
            border-radius: 20px;
            text-align: center;
            font-size: 1em;
            margin-bottom: 20px;
        }

        .history-section h3 {
            color: #555;
            margin-bottom: 10px;
            font-size: 1em;
        }

        .history-list {
            list-style: none;
            max-height: 150px;
            overflow-y: auto;
        }

        .history-list li {
            background: #f9f9f9;
            padding: 8px 14px;
            border-radius: 10px;
            margin: 5px 0;
            font-size: 0.85em;
            color: #444;
            border-left: 4px solid #4ECDC4;
        }

        .error-msg {
            color: #e74c3c;
            background: #fdecea;
            padding: 12px 20px;
            border-radius: 12px;
            text-align: center;
            font-size: 0.95em;
            margin: 10px 0;
        }

        .footer {
            text-align: center;
            color: #aaa;
            margin-top: 25px;
            font-size: 0.85em;
            line-height: 1.8;
        }
    </style>
</head>
<body>
<div class="container">

    <h1>🤪 Useless Info Hub</h1>
    <p class="subtitle">Powered by real AI — every fact is freshly generated!</p>
    <span class="groq-badge">⚡ Groq API · llama3-8b-8192 · Live Requests</span>

    <!-- Info Box -->
    <div class="info-box" id="infoBox">
        <div class="loading-overlay" id="loading">
            <div class="spinner"></div>
            <span>Asking Groq AI...</span>
        </div>

        <div class="emoji-large" id="emoji">🤔</div>
        <div class="info-text" id="infoText">Click any button to get a real AI-generated useless fact!</div>

        <div class="meta-row" id="metaRow" style="display:none">
            <span class="badge badge-category" id="badgeCategory">Category</span>
            <span class="badge badge-wow"      id="badgeWow">Wow: ?/10</span>
            <span class="badge badge-source"   id="badgeSource">Source</span>
        </div>
    </div>

    <div id="errorMsg" class="error-msg" style="display:none"></div>

    <!-- Buttons -->
    <div class="button-grid">
        <button class="btn btn-random"  onclick="getFact('random')" >🎲 Random</button>
        <button class="btn btn-animal"  onclick="getFact('animal')" >🐶 Animal</button>
        <button class="btn btn-food"    onclick="getFact('food')"   >🍕 Food</button>
        <button class="btn btn-space"   onclick="getFact('space')"  >🚀 Space</button>
        <button class="btn btn-history" onclick="getFact('history')">📜 History</button>
        <button class="btn btn-science" onclick="getFact('science')">🔬 Science</button>
    </div>

    <!-- Counter -->
    <div class="counter-bar">
        🤯 AI Facts Generated This Session: <strong id="factCount">0</strong>
    </div>

    <!-- History -->
    <div class="history-section">
        <h3>📝 Previously generated facts:</h3>
        <ul class="history-list" id="historyList">
            <li>Your fact history will appear here...</li>
        </ul>
    </div>

    <div class="footer">
        <p>⚡ Groq API &nbsp;•&nbsp; Flask Backend &nbsp;•&nbsp; Real AI Responses</p>
        <p>Lab 8 — Back-end + Front-end with Groq Integration</p>
    </div>
</div>

<script>
    const emojis = {
        random: '🤔', animal: '🐶', food: '🍕',
        space: '🚀', history: '📜', science: '🔬'
    };

    let factCount = 0;
    let history   = [];

    function setButtons(disabled) {
        document.querySelectorAll('.btn').forEach(b => b.disabled = disabled);
    }

    async function getFact(category) {
        // Show loading
        document.getElementById('loading').classList.add('show');
        document.getElementById('infoBox').style.opacity = '0.7';
        document.getElementById('errorMsg').style.display = 'none';
        document.getElementById('metaRow').style.display = 'none';
        setButtons(true);

        try {
            const res  = await fetch(`/api/fact?category=${category}`);
            const data = await res.json();

            if (data.error) {
                showError(data.error);
                return;
            }

            // Update UI
            document.getElementById('emoji').textContent     = emojis[category] || '🤔';
            document.getElementById('infoText').textContent  = data.fact;
            document.getElementById('badgeCategory').textContent = category.charAt(0).toUpperCase() + category.slice(1) + ' Fact';
            document.getElementById('badgeWow').textContent      = `Wow: ${data.wow_level || '?'}/10`;
            document.getElementById('badgeSource').textContent   = data.source_hint || 'Groq AI';
            document.getElementById('metaRow').style.display     = 'flex';

            // Counter
            factCount++;
            document.getElementById('factCount').textContent = factCount;

            // History (keep last 5)
            history.unshift(data.fact);
            if (history.length > 5) history.pop();
            renderHistory();

        } catch (err) {
            showError('Network error — is Flask running? ' + err.message);
        } finally {
            document.getElementById('loading').classList.remove('show');
            document.getElementById('infoBox').style.opacity = '1';
            setButtons(false);
        }
    }

    function showError(msg) {
        const el = document.getElementById('errorMsg');
        el.textContent = '⚠️ ' + msg;
        el.style.display = 'block';
    }

    function renderHistory() {
        const ul = document.getElementById('historyList');
        ul.innerHTML = history.map(f => `<li>${f}</li>`).join('');
    }

    // Load one fact on page start
    window.onload = () => getFact('random');
</script>
</body>
</html>
"""

# =============================================
# Routes
# =============================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/fact')
def get_fact():
    """Main route — calls Groq API and returns a fact."""
    category = request.args.get('category', 'random').strip().lower()
    valid = ["random", "animal", "food", "space", "history", "science"]
    if category not in valid:
        category = "random"

    try:
        raw = ask_groq(category)

        # Parse JSON from Groq response
        import json, re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            # Fallback: return raw text as fact
            result = {"fact": raw.strip(), "wow_level": "?", "source_hint": "Groq AI"}

        result["category"] = category
        return jsonify(result)

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else 500
        if status == 401:
            return jsonify({"error": "Invalid Groq API key. Set it in the GROQ_API_KEY variable."}), 401
        return jsonify({"error": f"Groq API returned {status}: {str(e)}"}), status

    except requests.exceptions.Timeout:
        return jsonify({"error": "Groq API timed out. Try again."}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/categories')
def list_categories():
    """Bonus: return available categories."""
    return jsonify({
        "categories": ["random", "animal", "food", "space", "history", "science"],
        "model": GROQ_MODEL,
        "provider": "Groq"
    })


# =============================================
# Run
# =============================================
if __name__ == '__main__':
    print("=" * 55)
    print("  Lab 8 — Useless Info Hub  |  Groq API")
    print("=" * 55)
    print("  Open: http://127.0.0.1:5000")
    print()
    print("  API Endpoints:")
    print("  GET /api/fact?category=random")
    print("  GET /api/fact?category=animal")
    print("  GET /api/fact?category=food")
    print("  GET /api/fact?category=space")
    print("  GET /api/fact?category=history")
    print("  GET /api/fact?category=science")
    print("  GET /api/categories")
    print("=" * 55)
    print("  ⚠  Set your Groq key at line 13 in this file!")
    print("     Get free key: https://console.groq.com")
    print("=" * 55)
    app.run(debug=True)
