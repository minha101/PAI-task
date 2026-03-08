import requests
import random
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Useless Info Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Comic Sans MS', cursive, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 40px;
            padding: 40px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #FF6B6B;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .info-box {
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            padding: 40px;
            border-radius: 30px;
            margin: 20px 0;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            border: 3px dashed white;
        }
        
        .info-text {
            font-size: 1.3em;
            line-height: 1.6;
            color: #333;
            margin: 20px 0;
        }
        
        .info-category {
            background: #4ECDC4;
            color: white;
            padding: 10px 30px;
            border-radius: 40px;
            font-size: 1em;
            margin: 10px 0;
            display: inline-block;
        }
        
        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        
        .btn {
            padding: 20px;
            border: none;
            border-radius: 20px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s;
            background: #4ECDC4;
            color: white;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(78, 205, 196, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(78, 205, 196, 0.5);
        }
        
        .btn.orange { background: #FF6B6B; }
        .btn.purple { background: #A8D8EA; color: #333; }
        .btn.green { background: #AA96DA; }
        .btn.yellow { background: #FCBAD3; color: #333; }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 6px solid #f3f3f3;
            border-top: 6px solid #FF6B6B;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .emoji-large {
            font-size: 5em;
            margin: 10px;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 30px;
            font-size: 0.9em;
        }
        
        .fact-counter {
            background: #FF6B6B;
            color: white;
            padding: 10px;
            border-radius: 30px;
            margin: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤪 Useless Info Hub</h1>
        
        <div class="info-box" id="infoBox">
            <div class="emoji-large" id="emoji">🤔</div>
            <div class="info-text" id="infoText">Click any button to get useless information!</div>
            <div class="info-category" id="infoCategory">Random Fact</div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Loading useless info...</p>
        </div>
        
        <div class="button-grid">
            <button class="btn orange" onclick="getFact('random')">🎲 Random Fact</button>
            <button class="btn" onclick="getFact('animal')">🐶 Animal Facts</button>
            <button class="btn purple" onclick="getFact('food')">🍕 Food Facts</button>
            <button class="btn green" onclick="getFact('space')">🚀 Space Facts</button>
            <button class="btn yellow" onclick="getFact('history')">📜 History Facts</button>
            <button class="btn orange" onclick="getFact('science')">🔬 Science Facts</button>
        </div>
        
        <div class="fact-counter" id="counter">
            🤯 Today's useless facts viewed: <span id="factCount">0</span>
        </div>
        
        <div class="footer">
            <p>⚡ 100% Useless • No API Key Required • Pure Fun</p>
            <p style="font-size: 0.8em; margin-top: 10px;">Did you know? These facts are 100% true... probably! 😉</p>
        </div>
    </div>
    
    <script>
        let factCounter = 0;
        
        // Database of useless facts (no API needed!)
        const factDatabase = {
            random: [
                "A cloud weighs around a million tonnes.",
                "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs!",
                "Octopuses have three hearts and blue blood.",
                "Bananas are technically berries, but strawberries aren't!",
                "A day on Venus is longer than a year on Venus.",
                "The Eiffel Tower can be 15 cm taller during summer.",
                "Your brain is constantly eating itself.",
                "Cows have best friends and get stressed when separated.",
                "The dot over 'i' is called a tittle.",
                "A group of flamingos is called a 'flamboyance'."
            ],
            animal: [
                "Penguins propose to their mates with a pebble.",
                "An octopus has nine brains - one central and eight in arms!",
                "Cows have almost 360-degree panoramic vision.",
                "A sloth takes two weeks to digest its food.",
                "Dolphins have names for each other.",
                "A hummingbird weighs less than a penny.",
                "Sea otters hold hands while sleeping to not drift apart.",
                "A cat's nose print is unique like human fingerprint."
            ],
            food: [
                "Peanuts aren't nuts - they're legumes!",
                "Honey is the only food that never spoils.",
                "Potatoes were the first vegetable grown in space.",
                "Chocolate was once used as currency by Aztecs.",
                "Ketchup was sold as medicine in 1830s.",
                "Carrots were originally purple, not orange.",
                "Cucumbers are 96% water.",
                "Pound cake got its name from its recipe - a pound each of flour, butter, eggs, and sugar."
            ],
            space: [
                "There's a planet made of diamonds (55 Cancri e).",
                "A day on Mercury is longer than its year.",
                "Space is completely silent because there's no atmosphere.",
                "The Sun makes up 99.86% of our solar system's mass.",
                "There are more stars than grains of sand on Earth.",
                "One day on Venus is longer than one year on Venus.",
                "Neptune has only completed one orbit around the sun since discovered."
            ],
            history: [
                "Cleopatra lived closer to the moon landing than to pyramid construction.",
                "The shortest war in history lasted 38 minutes (Britain vs Zanzibar, 1896).",
                "Napoleon was once attacked by a horde of rabbits.",
                "Ancient Egyptians used to use dead mice for toothaches.",
                "The first known computer bug was an actual moth in 1947.",
                "Vikings never wore horned helmets - that's a myth."
            ],
            science: [
                "Your body produces enough heat in 30 minutes to boil half a gallon of water.",
                "Bananas are slightly radioactive.",
                "It would take 1.2 million mosquitoes to drain all your blood.",
                "Your stomach acid can dissolve razor blades.",
                "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
                "The human nose can detect over 1 trillion smells."
            ]
        };
        
        const emojis = {
            random: '🤔',
            animal: '🐶',
            food: '🍕',
            space: '🚀',
            history: '📜',
            science: '🔬'
        };
        
        function getFact(category) {
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('infoBox').style.opacity = '0.5';
            
            setTimeout(() => {
                // Get random fact from selected category
                const facts = factDatabase[category] || factDatabase.random;
                const randomFact = facts[Math.floor(Math.random() * facts.length)];
                
                // Update display
                document.getElementById('infoText').textContent = randomFact;
                document.getElementById('infoCategory').textContent = 
                    category.charAt(0).toUpperCase() + category.slice(1) + ' Fact';
                document.getElementById('emoji').textContent = emojis[category] || '🤔';
                
                // Update counter
                factCounter++;
                document.getElementById('factCount').textContent = factCounter;
                
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                document.getElementById('infoBox').style.opacity = '1';
            }, 500); // Small delay for effect
        }
        
        // Get random fact on page load
        window.onload = () => getFact('random');
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("="*50)
    print("🤪 USELESS INFO APP STARTED!")
    print("="*50)
    print("📱 Open this URL:")
    print("👉 http://127.0.0.1:5000")
    print("\n✅ Features:")
    print("   • No API Key needed")
    print("   • 50+ useless facts")
    print("   • 6 different categories")
    print("   • Fun animations")
    print("="*50)
    app.run(debug=True)