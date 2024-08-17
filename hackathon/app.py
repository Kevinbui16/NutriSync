from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "WRGJEIWFEREGIKFWEMRFWSMKFSNVJ43562MFKMGM"


@app.route('/')
def main_page():
    return render_template("index.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_name = request.form["name"]
        password = request.form["password"]
        if user_name and password:
            session["user"] = user_name
            return redirect(url_for("hello_user_page"))
    return render_template("login.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        session["user"] = username
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/user', methods=["POST", "GET"])
def hello_user_page():
    if "user" in session:
        name = session["user"]
        welcome_message = """
        🌟 Welcome to NutriSync! 🌟

        Feeling under the weather? We've got your back!

        Tell us your symptoms or let your wearable spill the beans,
        and we'll cook up a custom supplement cocktail just for you.

        Ready to boost your health? Let's dive in!

        """
        if request.method == "POST":
            choice = request.form.get("choice")
            if choice == "1":
                return redirect(url_for("loading_page", next_page="manual_symptom_entry"))
            elif choice == "2":
                return redirect(url_for("loading_page", next_page="analyze_wearable_data"))
        return render_template("user_choose_case.html", name=name, message=welcome_message)
    else:
        return redirect(url_for("login"))


@app.route('/loading')
def loading_page():
    next_page = request.args.get('next_page')
    return render_template("loading.html", next_page=next_page)


@app.route('/manual', methods=["POST", "GET"])
def manual_symptom_entry():
    symptoms = [
        "Fatigue", "Weakened immune system", "Muscle weakness", "Poor night vision",
        "Brittle hair and nails", "Bone pain", "Dry skin", "Poor wound healing",
        "Irregular heartbeats", "Brain fog"
    ]

    if request.method == "POST":
        selected_symptoms = request.form.get("symptoms")
        age = request.form.get("age")
        gender = request.form.get("gender")
        pregnant = request.form.get("pregnant", None)

        # Backend logic for recommendations would go here
        recommendation = {
            "general": "Ensure adequate Vitamin D intake. Consider fortified foods and safe sun exposure. Ensure adequate calcium intake.\n Consider dairy products and fortified plant milks. Increase magnesium intake. Good sources include nuts, seeds, and leafy greens.\n",
            "products": [
                {
                    "name": "GNC Magnesium 500",
                    "price": "86.55AUD",
                    "link": "https://www.ebay.com.au/itm/175268074445",
                    "image": "https://i.ibb.co/cvT8Bqd/Screenshot-2024-08-16-at-17-50-20-removebg-preview.png",
                    "why": "• High-potency (500mg per serving) \n• Supports bone and muscle health \n• Aids nerve function and energy\n• May improve sleep quality"
                },
                {
                    "name": "Pfeiffer Calcium & Magnesium",
                    "price": "25.72AUD",
                    "link": "https://au.iherb.com/pr/now-foods-calcium-magnesium-8-oz-227-g/455",
                    "image": "https://i.ibb.co/p324tLY/Screenshot-2024-08-16-at-17-41-20-removebg-preview.png",
                    "why": "• Balanced calcium and magnesium combo\n • Promotes bone density and strength\n • Supports muscle and nerve function\n • Cost-effective for dual mineral needs"
                }
            ]
        }

        return render_template("recommendation.html", recommendation=recommendation)

    return render_template("manual.html", symptoms=symptoms)


@app.route('/analyze_wearable_data')
def analyze_wearable_data():
    health_report = {
        "sleep": {
            "average": "9.46 hours",
            "recommended": "9-10 hours for children aged 6-13",
            "status": "Within recommended range"
        },
        "activity": {
            "steps": "8,064",
            "recommended_steps": "10,000-12,000 steps for children",
            "steps_status": "Below recommended",
            "active_minutes": "54 minutes",
            "recommended_minutes": "At least 60 minutes of moderate to vigorous physical activity daily",
            "minutes_status": "Below recommended"
        },
        "nutrition": {
            "vitamin_c": "38.74 mg",
            "recommended_vitamin_c": "45 mg/day for children aged 6-8",
            "vitamin_c_status": "Below recommended"
        },
        "recommendations": [
            "Sleep: Maintain current sleep schedule.",
            "Physical Activity: Increase daily activity to reach 10,000 steps and 60 active minutes.",
            "Nutrition: Increase Vitamin C intake through diet or supplements.",
            "Hydration: Ensure adequate water intake throughout the day.",
            "Wound Healing: Monitor wound healing progress and maintain good nutrition and sleep habits to support healing."
        ]
    }

    return render_template("wearable_analysis.html", health_report=health_report)


if __name__ == '__main__':
    app.run(debug=True)
