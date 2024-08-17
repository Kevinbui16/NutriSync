import pandas as pd
from collections import defaultdict
import time
import threading
from PIL import Image
import time
from datetime import datetime, timedelta
from health import generate_report

# Load the CSV file
file_path_csv = '8g. AUSNUT 2011-13 AHS Dietary Supplement Nutrient Database.csv'
data = pd.read_csv(file_path_csv, delimiter=';')

# Convert numeric columns to proper format
numeric_columns = [
    "Protein (g)", "Iron (Fe) (mg)", "Magnesium (Mg) (mg)", "Potassium (K) (mg)", 
    "Thiamin (B1) (mg)", "Vitamin B12  (µg)", "Vitamin C (mg)", "Zinc (Zn) (mg)", 
    "Calcium (Ca) (mg)", "Folic acid  (µg)", "Dietary folate equivalents  (µg)"
]

# Convert columns to numeric, replacing commas and coercing errors
for column in numeric_columns:
    data[column] = pd.to_numeric(data[column].str.replace(',', '.'), errors='coerce')

class EnhancedSupplementRecommender:
    def __init__(self, supplement_data, symptom_deficiency_data):
        self.supplement_data = supplement_data
        self.symptom_deficiency_map = symptom_deficiency_data

        self.deficiency_nutrient_map = {
            "Vitamin A": ["Preformed vitamin A (retinol) (µg)", "Beta-carotene (µg)", "Provitamin A (b-carotene equivalents) (µg)", "Vitamin A retinol equivalents (µg)"],
            "Vitamin B1": ["Thiamin (B1) (mg)"],
            "Vitamin B2": ["Riboflavin (B2) (mg)"],
            "Vitamin B3": ["Niacin (B3) (mg)", "Niacin derived equivalents (mg)"],
            "Folate": ["Folic acid  (µg)", "Dietary folate equivalents  (µg)"],
            "Vitamin B6": ["Vitamin B6 (mg)"],
            "Vitamin B12": ["Vitamin B12  (µg)"],
            "Vitamin C": ["Vitamin C (mg)"],
            "Vitamin E": ["Vitamin E (mg)"],
            "Calcium": ["Calcium (Ca) (mg)"],
            "Iodine": ["Iodine (I) (µg)"],
            "Iron": ["Iron (Fe) (mg)"],
            "Magnesium": ["Magnesium (Mg) (mg)"],
            "Phosphorus": ["Phosphorus (P) (mg)"],
            "Potassium": ["Potassium (K) (mg)"],
            "Selenium": ["Selenium (Se) (µg)"],
            "Zinc": ["Zinc (Zn) (mg)"],
            "Protein": ["Protein (g)"],
            "Dietary Fiber": ["Dietary fibre (g)"],
            "Omega-3 Fatty Acids": ["Total long chain omega 3 fatty acids (mg)"]
        }
        self.age_groups = {
            "child": (0, 12),
            "teen": (13, 17),
            "adult": (18, 120)
        }
        self.categorize_supplements()

    def categorize_supplements(self):
        self.categorized_supplements = {
            "child": [],
            "teen": [],
            "women": [],
            "men": [],
            "pregnancy": []
        }
        for _, supplement in self.supplement_data.iterrows():
            name = supplement["Dietary supplement name"].lower()
            if "children" in name or "kids" in name:
                self.categorized_supplements["child"].append(supplement)
            elif "teen" in name:
                self.categorized_supplements["teen"].append(supplement)
            elif "women" in name or "woman" in name:
                self.categorized_supplements["women"].append(supplement)
            elif "men" in name or "man" in name:
                self.categorized_supplements["men"].append(supplement)
            elif "pregnancy" in name or "prenatal" in name:
                self.categorized_supplements["pregnancy"].append(supplement)
            else:
                # Add to both men and women if not specific
                self.categorized_supplements["women"].append(supplement)
                self.categorized_supplements["men"].append(supplement)

    def get_relevant_supplements(self, age, gender, pregnant):
        relevant_supplements = []
        age_group = self.get_age_group(age)
        
        if age_group == "child":
            relevant_supplements.extend(self.categorized_supplements["child"])
        elif age_group == "teen":
            relevant_supplements.extend(self.categorized_supplements["teen"])
        elif age_group == "adult":
            if gender == "female":
                relevant_supplements.extend(self.categorized_supplements["women"])
                if pregnant:
                    relevant_supplements.extend(self.categorized_supplements["pregnancy"])
            else:
                relevant_supplements.extend(self.categorized_supplements["men"])
        
        return relevant_supplements

    def get_age_group(self, age):
        for group, (min_age, max_age) in self.age_groups.items():
            if min_age <= age <= max_age:
                return group
        return "adult" 

    def get_rdi(self, age, gender, pregnant=False):
        # Base RDI for all age groups
        rdi = {
            "Protein (g)": 50,
            "Iron (Fe) (mg)": 18,
            "Magnesium (Mg) (mg)": 400,
            "Potassium (K) (mg)": 3500,
            "Thiamin (B1) (mg)": 1.2,
            "Vitamin B12  (µg)": 2.4,
            "Vitamin C (mg)": 90,
            "Zinc (Zn) (mg)": 11,
            "Calcium (Ca) (mg)": 1000,
            "Folic acid  (µg)": 400,
            "Dietary folate equivalents  (µg)": 400,
            "Vitamin A retinol equivalents (µg)": 900,
            "Vitamin B2 (mg)": 1.3,
            "Vitamin B3 (mg)": 16,
            "Vitamin B6 (mg)": 1.3,
            "Vitamin E (mg)": 15,
            "Iodine (I) (µg)": 150,
            "Phosphorus (P) (mg)": 700,
            "Selenium (Se) (µg)": 55,
            "Dietary fibre (g)": 30,
            "Total long chain omega 3 fatty acids (mg)": 250
        }

        # Adjust based on age, gender, and pregnancy status
        if age < 9:
            rdi.update({
                "Protein (g)": 19,
                "Iron (Fe) (mg)": 10,
                "Magnesium (Mg) (mg)": 130,
                "Potassium (K) (mg)": 2300,
                "Thiamin (B1) (mg)": 0.6,
                "Vitamin B12  (µg)": 1.2,
                "Vitamin C (mg)": 25,
                "Zinc (Zn) (mg)": 5,
                "Calcium (Ca) (mg)": 700,
                "Folic acid  (µg)": 200,
                "Dietary folate equivalents  (µg)": 200
            })
        elif pregnant:
            rdi.update({
                "Protein (g)": 71,
                "Iron (Fe) (mg)": 27,
                "Magnesium (Mg) (mg)": 350,
                "Potassium (K) (mg)": 2900,
                "Thiamin (B1) (mg)": 1.4,
                "Vitamin B12  (µg)": 2.6,
                "Vitamin C (mg)": 85,
                "Zinc (Zn) (mg)": 11,
                "Calcium (Ca) (mg)": 1000,
                "Folic acid  (µg)": 600,
                "Dietary folate equivalents  (µg)": 600
            })
        elif age >= 51:
            rdi.update({
                "Calcium (Ca) (mg)": 1200,
                "Vitamin D (µg)": 15 if age < 70 else 20
            })
        
        if gender == "female" and 19 <= age <= 50:
            rdi["Iron (Fe) (mg)"] = 18
        elif gender == "male" and age > 50:
            rdi["Zinc (Zn) (mg)"] = 11

        return rdi

    def analyze_symptoms(self, symptoms):
        deficiency_count = {}
        for symptom in symptoms:
            if symptom in self.symptom_deficiency_map:
                for deficiency in self.symptom_deficiency_map[symptom]:
                    deficiency_count[deficiency] = deficiency_count.get(deficiency, 0) + 1
        sorted_deficiencies = sorted(deficiency_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_deficiencies

    def get_recommendation(self, deficiencies):
        if not deficiencies:
            return "No specific deficiencies identified based on the given symptoms."
        
        recommendations = []
        for deficiency, _ in deficiencies:
            if deficiency == "Protein":
                recommendations.append("Consider increasing protein intake. Consult a nutritionist for a balanced diet plan.")
            elif deficiency == "Iron":
                recommendations.append("Iron supplementation may be beneficial. Consider iron-rich foods like lean meats, beans, and leafy greens.")
            elif deficiency == "Zinc":
                recommendations.append("Increase zinc intake through foods like oysters, beef, and pumpkin seeds, or consider zinc supplements.")
            elif deficiency == "Folate":
                recommendations.append("Increase folate intake. Good sources include leafy greens, legumes, and fortified cereals.")
            elif deficiency == "Vitamin B12":
                recommendations.append("Increase Vitamin B12 intake. Consider fortified cereals and B12 supplementation, especially for vegetarians/vegans.")
            elif deficiency == "Calcium":
                recommendations.append("Ensure adequate calcium intake. Consider dairy products and fortified plant milks.")
            elif deficiency == "Vitamin D":
                recommendations.append("Ensure adequate Vitamin D intake. Consider fortified foods and safe sun exposure.")
            elif deficiency == "Vitamin A":
                recommendations.append("Increase Vitamin A intake. Consider foods like carrots, sweet potatoes, and leafy greens.")
            elif deficiency == "Omega-3 Fatty Acids":
                recommendations.append("Consider increasing intake of omega-3 fatty acids through foods like fatty fish, flaxseeds, and walnuts.")
            elif deficiency == "Vitamin C":
                recommendations.append("Increase Vitamin C intake. Consider citrus fruits, strawberries, and bell peppers.")
            elif deficiency == "Vitamin B3":
                recommendations.append("Increase Vitamin B3 intake. Consider foods like chicken, tuna, and whole grains.")
            elif deficiency == "Vitamin B2":
                recommendations.append("Increase Vitamin B2 intake. Consider foods like eggs, almonds, and dairy products.")
            elif deficiency == "Vitamin B1":
                recommendations.append("Increase Vitamin B1 intake. Consider foods like whole grains, pork, and legumes.")
            elif deficiency == "Magnesium":
                recommendations.append("Increase magnesium intake. Good sources include nuts, seeds, and leafy greens.")
            elif deficiency == "Selenium":
                recommendations.append("Ensure adequate selenium intake. Brazil nuts, fish, and poultry are good sources.")
            elif deficiency == "Iodine":
                recommendations.append("Consider iodine-rich foods like seaweed, fish, and iodized salt.")
            elif deficiency == "Dietary Fiber":
                recommendations.append("Increase fiber intake through whole grains, fruits, vegetables, and legumes.")
            else:
                recommendations.append(f"Address potential {deficiency} deficiency. Consult a healthcare professional for specific dietary advice or supplementation.")
        
        return " ".join(recommendations)

    def adjust_for_demographics(self, deficiency_scores, age, gender, pregnant=False):
        if gender == "female":
            if 12 < age < 51:
                # Increase Iron for menstruating women
                deficiency_scores["Iron"] = deficiency_scores.get("Iron", 0) * 1.5
            
            if pregnant:
                # Increase specific nutrients during pregnancy
                deficiency_scores["Iron"] = deficiency_scores.get("Iron", 0) * 1.8
                deficiency_scores["Folate"] = deficiency_scores.get("Folate", 0) * 1.6
                deficiency_scores["Calcium"] = deficiency_scores.get("Calcium", 0) * 1.2
                deficiency_scores["Vitamin D"] = deficiency_scores.get("Vitamin D", 0) * 1.2
                deficiency_scores["Omega-3 Fatty Acids"] = deficiency_scores.get("Omega-3 Fatty Acids", 0) * 1.3

        if age < 9:
            # Adjust for children under 9
            deficiency_scores["Calcium"] = deficiency_scores.get("Calcium", 0) * 1.2
            deficiency_scores["Iron"] = deficiency_scores.get("Iron", 0) * 1.1
            deficiency_scores["Vitamin D"] = deficiency_scores.get("Vitamin D", 0) * 1.3

        elif 9 <= age <= 18:
            # Adjust for teenagers
            deficiency_scores["Calcium"] = deficiency_scores.get("Calcium", 0) * 1.5
            deficiency_scores["Iron"] = deficiency_scores.get("Iron", 0) * 1.2
            deficiency_scores["Vitamin D"] = deficiency_scores.get("Vitamin D", 0) * 1.4
            deficiency_scores["Magnesium"] = deficiency_scores.get("Magnesium", 0) * 1.1

        if age > 50:
            # Adjust for older adults
            deficiency_scores["Calcium"] = deficiency_scores.get("Calcium", 0) * 1.2
            deficiency_scores["Vitamin B12"] = deficiency_scores.get("Vitamin B12", 0) * 1.3
            deficiency_scores["Vitamin D"] = deficiency_scores.get("Vitamin D", 0) * 1.2
            deficiency_scores["Omega-3 Fatty Acids"] = deficiency_scores.get("Omega-3 Fatty Acids", 0) * 1.2

        if age > 70:
            # Further adjustment for elderly
            deficiency_scores["Calcium"] = deficiency_scores.get("Calcium", 0) * 1.3
            deficiency_scores["Vitamin D"] = deficiency_scores.get("Vitamin D", 0) * 1.5
            deficiency_scores["Vitamin B12"] = deficiency_scores.get("Vitamin B12", 0) * 1.4

        if gender == "male" and age > 50:
            # Increase Zinc for older men
            deficiency_scores["Zinc"] = deficiency_scores.get("Zinc", 0) * 1.1

        return deficiency_scores



    def get_top_supplements(self, deficiency_scores, rdi, age, gender, pregnant, n=2):
        relevant_supplements = self.get_relevant_supplements(age, gender, pregnant)
        supplement_scores = defaultdict(float)
        supplement_links = {}
        supplement_images = {}
        supplement_prices = {}

        for supplement in relevant_supplements:
            score = 0
            for deficiency, def_score in deficiency_scores.items():
                nutrient_columns = self.deficiency_nutrient_map.get(deficiency, [])
                for nutrient in nutrient_columns:
                    if nutrient in supplement and pd.notna(supplement[nutrient]):
                        # Ensure the supplement nutrient value is a string before replacing
                        nutrient_value_str = str(supplement[nutrient]).replace(',', '.')
                        try:
                            nutrient_value = float(nutrient_value_str)
                            if nutrient_value > 0:
                                if nutrient in rdi:
                                    nutrient_score = (nutrient_value / rdi[nutrient]) * def_score
                                    score += nutrient_score
                        except ValueError:
                            continue  # 

            # Apply demographic-specific boosts
            if gender == "female" and "women" in supplement["Dietary supplement name"].lower():
                score *= 1.15
            elif gender == "male" and "men" in supplement["Dietary supplement name"].lower():
                score *= 1.15
            elif pregnant and "pregnancy" in supplement["Dietary supplement name"].lower():
                score *= 1.3


            supplement_name = supplement["Dietary supplement name"]
            supplement_scores[supplement["Dietary supplement name"]] = score
            supplement_links[supplement_name] = supplement.get("Purchase Link", "")
            supplement_images[supplement_name] = supplement.get("Image Link", "")
            supplement_prices[supplement_name] = supplement.get("Price","")

        # Normalize scores
        max_score = max(supplement_scores.values()) if supplement_scores else 1
        normalized_scores = {k: (v / max_score) * 100 for k, v in supplement_scores.items()}

        # Filter out supplements with very low scores
        filtered_scores = {k: v for k, v in normalized_scores.items() if v > 10}

        # Sort supplements by score and then by name to ensure consistent ordering
        top_supplements = sorted(filtered_scores.items(), key=lambda x: (-x[1], x[0]))[:n]

        # Return top supplements along with their purchase links and image links
        return [(supplement, score, supplement_links[supplement], supplement_images[supplement], supplement_prices[supplement]) for supplement, score in top_supplements]


    def recommend(self, symptoms, age, gender, pregnant=False):
        deficiencies = self.analyze_symptoms(symptoms)
        general_recommendation = self.get_recommendation(deficiencies)
        
        deficiency_scores = {deficiency: score for deficiency, score in deficiencies}
        adjusted_scores = self.adjust_for_demographics(deficiency_scores, age, gender)
        rdi = self.get_rdi(age, gender, pregnant)
        top_supplements = self.get_top_supplements(adjusted_scores, rdi, age, gender, pregnant)
        
        specific_recommendations = self.interpret_scores_and_recommend(top_supplements, symptoms, age, gender, pregnant)
        
        return general_recommendation, top_supplements, specific_recommendations
    
    def interpret_scores_and_recommend(self, top_supplements, symptoms, age, gender, pregnant):
        recommendations = []
        why_this_product = []
        age_group = self.get_age_group(age)

                # Dictionary mapping each supplement to its "Why This Product?" explanation
        why_this_product_map = {
            "GNC Magnesium 500": """High-potency (500mg per serving)
        Supports bone and muscle health
        Aids nerve function and energy
        May improve sleep quality""",

            "Pfeiffer Calcium & Magnesium": """Balanced calcium and magnesium combo
        Promotes bone density and strength
        Supports muscle and nerve function
        Cost-effective for dual mineral needs"""
        }

        if not top_supplements:
            recommendations.append("Based on the provided information, no specific supplements are recommended. Please consult with a healthcare professional for personalized advice.")
            return recommendations, why_this_product

        top_supplement, top_score, link, image_link, price = top_supplements[0]

        # Create loop to add definition for each product
        for i, (top_supplement, top_score, link, image_link, price) in enumerate(top_supplements):
            if top_score >= 90:
                recommendations.append(f"Highly Recommended: {top_supplement} is an excellent match for your needs.")

            # Add "Why This Product?" explanation
            if top_supplement in why_this_product_map:
                why_this_product.append(f"{top_supplement}: {why_this_product_map[top_supplement]}")

        # Add age-specific advice
        if age_group == "child":
            recommendations.append("For children, it's crucial to focus on supplements that support growth and development.")
        elif age_group == "teen":
            recommendations.append("Teens may benefit from supplements that support bone health, energy, and overall growth.")
        elif age_group == "adult":
            if gender == "female":
                if pregnant:
                    recommendations.append("During pregnancy, focus on prenatal supplements that provide essential nutrients for both mother and baby.")
                else:
                    recommendations.append("Adult women should consider supplements that support bone health, iron levels, and overall wellness.")
            else:
                recommendations.append("Adult men may benefit from supplements that support heart health, muscle function, and overall vitality.")

        # Add symptom-specific advice
        symptom_recommendations = {
            "Fatigue": "To address fatigue, look for supplements rich in iron, vitamin B12, vitamin B6, and magnesium.",
            "Weakened immune system": "To support your immune system, consider supplements with vitamin C, zinc, vitamin D, and selenium.",
            "Muscle weakness": "For muscle strength, ensure adequate intake of vitamin D, magnesium, and potassium.",
            "Poor night vision": "To support eye health, look for supplements containing vitamin A.",
            "Brittle hair and nails": "For healthier hair and nails, consider supplements with biotin, iron, and zinc.",
            # "Bone pain": "To support bone health, look for supplements rich in vitamin D, calcium, magnesium, and phosphorus.",
            "Dry skin": "For skin health, consider supplements with vitamin E and omega-3 fatty acids.",
            "Poor wound healing": "To improve wound healing, ensure adequate intake of vitamin C, zinc, and protein.",
            "Irregular heartbeats": "For heart health, consider supplements with magnesium and potassium, but consult a doctor first.",
            "Brain fog": "To improve cognitive function, look for supplements containing vitamin B12, iron, and omega-3 fatty acids."
        }

        for symptom in symptoms:
            if symptom in symptom_recommendations:
                recommendations.append(symptom_recommendations[symptom])

        if len(top_supplements) > 1:
            top_supplement, top_score, _, _, _ = top_supplements[0]
            second_supplement, second_score, _, _, _ = top_supplements[1]

            if top_supplement != second_supplement:
                if top_score - second_score < 10:
                    recommendations.append(f"Consider alternating between {top_supplement} and {second_supplement}, as they are both well-suited to your needs.")
                else:
                    recommendations.append(f"While {top_supplement} is the top recommendation, {second_supplement} could be an alternative option to consider.")

            # Add general recommendation
            recommendations.append(
                "Remember to maintain a balanced diet alongside any supplementation. Always consult with a healthcare professional before starting any new supplement regimen, especially if you have existing health conditions or are taking medications."
            )

        return recommendations, why_this_product

    def get_available_symptoms(self):
        return list(self.symptom_deficiency_map.keys())

# Primary symptom-deficiency map (Australian scope)
primary_symptom_deficiency_map = {
    "Fatigue": ["Iron", "Vitamin B12", "Vitamin B6", "Magnesium"],
    "Weakened immune system": ["Vitamin C", "Zinc", "Vitamin D", "Selenium"],
    "Muscle weakness": ["Vitamin D", "Magnesium", "Potassium"],
    "Poor night vision": ["Vitamin A"],
    "Brittle hair and nails": ["Biotin", "Iron", "Zinc"],
    "Bone pain": ["Vitamin D", "Calcium", "Magnesium"],
    "Dry skin": ["Vitamin E", "Omega-3 fatty acids"],
    "Poor wound healing": ["Vitamin C", "Zinc", "Protein"],
    "Irregular heartbeats": ["Magnesium", "Potassium"],
    "Brain fog": ["Vitamin B12", "Iron", "Omega-3 fatty acids"]
}

# Initialize the recommender
recommender = EnhancedSupplementRecommender(data, primary_symptom_deficiency_map)

def get_user_symptoms(available_symptoms):
    print("\nAvailable symptoms:")
    for i, symptom in enumerate(available_symptoms, 1):
        print(f"{i}. {symptom}")
    
    while True:
        try:
            choices = input("\nEnter the numbers of your symptoms (separated by commas): ")
            symptom_indices = [int(choice.strip()) - 1 for choice in choices.split(',')]
            user_symptoms = [available_symptoms[i] for i in symptom_indices if 0 <= i < len(available_symptoms)]
            if user_symptoms:
                return user_symptoms
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")

def get_user_info():
    while True:
        try:
            age = int(input("Enter your age: "))
            if age < 0 or age > 100:
                raise ValueError
            break
        except ValueError:
            print("Invalid age. Please enter a number between 0 and 100.")

    while True:
        gender = input("Enter your gender (male/female): ").lower()
        if gender in ['male', 'female']:
            break
        else:
            print("Invalid input. Please enter 'male' or 'female'.")

    pregnant = False
    if gender == 'female':
        while True:
            pregnant_input = input("Are you pregnant? (yes/no): ").lower()
            if pregnant_input in ['yes', 'no']:
                pregnant = (pregnant_input == 'yes')
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    return age, gender, pregnant

def analyze_wearable_data(self, wearable_data):
    avg_sleep = wearable_data['Sleep Analysis [In Bed] (hr)'].mean()
    avg_steps = wearable_data['Step Count (steps)'].mean()
    avg_active_minutes = wearable_data['Apple Exercise Time (min)'].mean()
    avg_vitamin_c = wearable_data['Vitamin C (mg)'].mean()

    report = generate_report(wearable_data, avg_sleep, avg_steps, avg_active_minutes, avg_vitamin_c)

    recommendations = []
    if avg_sleep < 9:
        recommendations.append("Increase sleep duration to reach 9-10 hours per night.")
    if avg_steps < 10000 or avg_active_minutes < 60:
        recommendations.append("Increase daily activity to reach 10,000 steps and 60 active minutes.")
    if avg_vitamin_c < 45:
        recommendations.append("Increase Vitamin C intake through diet or supplements.")

    return report, recommendations

def print_welcome():
    print("""
    🌟 Welcome to NutriSync! 🌟

    Feeling under the weather? We've got your back!
    
    Tell us your symptoms or let your wearable spill the beans,
    and we'll cook up a custom supplement cocktail just for you.

    Ready to boost your health? Let's dive in!
    """)

def get_user_choice():
    while True:
        choice = input("\nWould you like to (1) enter symptoms manually or (2) analyze your wearable data? Enter 1 or 2: ")
        if choice in ['1', '2']:
            return int(choice)
        else:
            print("Invalid input. Please enter 1 or 2.")

def display_tommy_analysis():
    print("Tommy's Health Analysis Report")
    print("\n1. Sleep")
    print("   Average sleep duration: 9.46 hours")
    print("   Recommended: 9-10 hours for children aged 6-13")
    print("   Status: Within recommended range")

    print("\n2. Physical Activity")
    print("   Average daily steps: 8,064")
    print("   Recommended: 10,000-12,000 steps for children")
    print("   Status: Below recommended")

    print("   Average active minutes: 54 minutes")
    print("   Recommended: At least 60 minutes of moderate to vigorous physical activity daily")
    print("   Status: Below recommended")

    print("\n3. Nutrition")
    print("   Average Vitamin C intake: 38.74 mg")
    print("   Recommended: 45 mg/day for children aged 6-8")
    print("   Status: Below recommended")

    print("\nRecommendations:")
    print("1. Sleep: Maintain current sleep schedule.")
    print("2. Physical Activity: Increase daily activity to reach 10,000 steps and 60 active minutes.")
    print("3. Nutrition: Increase Vitamin C intake through diet or supplements.")
    print("4. Hydration: Ensure adequate water intake throughout the day.")
    print(
        "5. Wound Healing: Monitor wound healing progress and maintain good nutrition and sleep habits to support healing.")

def show_health_dashboard():
    image_path = "health_dashboard.png"
    image = Image.open(image_path)
    image.show()

def remind_to_drink_water():
    while True:
        # Remind every 1hr
        time.sleep(3600)
        print("🔔 Reminder: Have you drunk enough water today? Stay hydrated!")

def remind_to_exercise():
    while True:
        # Remind every hour
        time.sleep(3600)
        print("🔔 Reminder: Make sure to get some exercise today! Aim for at least 30 minutes of activity.")

def remind_to_stand_up():
    while True:
        # Remind every 30 minutes
        time.sleep(1800)
        print("🔔 Reminder: Time to stand up and move around! Aim to stand for at least 12 hours today.")

def remind_to_sleep():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=21, minute=45, second=0, microsecond=0)  # 9:45 PM
        
        if now > target_time:
            # If it's past 9:45 PM, set target for next day
            target_time += timedelta(days=1)
        
        time_until_reminder = (target_time - now).total_seconds()
        time.sleep(time_until_reminder)
        
        print("🔔 Reminder: It's almost 10 PM. Time to wind down and prepare for sleep. Aim for 7-8 hours of rest.")
        
        # Wait for 15 minutes before checking again
        time.sleep(900)


def print_goodbye():
    goodbye_message = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║       Thank you for syncing your health with NutriSync!       ║
    ║                                                               ║
    ║   Your personalized nutrition journey is just beginning.      ║
    ║   Remember, small steps lead to big transformations.          ║
    ║                                                               ║
    ║   Stay nourished, stay synced, and thrive with NutriSync!     ║
    ║                                                               ║
    ║              We look forward to your next visit.              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(goodbye_message)

def main():
    print_welcome()
    
    while True:
        user_choice = get_user_choice()

        if user_choice == 1:
            process_manual_entry()
            run_reminders()
        elif user_choice == 2:
            process_wearable_data()
            run_reminders()
        
        continue_choice = input("\nWould you like to continue using NutriSync? (yes/no): ").lower()
        if continue_choice != 'yes':
            break
    
    print_goodbye()

def process_manual_entry():
    print("Manual symptom entry selected.")
    available_symptoms = recommender.get_available_symptoms()

    user_symptoms = get_user_symptoms(available_symptoms)
    user_age, user_gender, user_pregnant = get_user_info()

    general_recommendation, top_supplements, _ = recommender.recommend(
        user_symptoms, user_age, user_gender, user_pregnant)

    print(f"\nGeneral Recommendation for a {user_age}-year-old {user_gender} {'(pregnant) ' if user_pregnant else ''}with symptoms: {', '.join(user_symptoms)}")
    print(general_recommendation)

    print("\nTop recommended supplements:")
    for i, (supplement, score, link, image_link, price) in enumerate(top_supplements):
        if score >= 70:
            rank = f"Top {i + 1}"
            print(f"- {rank}: {supplement} - Price: {price}. Purchase here: {link}")
            print(f"  Image: {image_link}")

    specific_recommendations, why_this_product = recommender.interpret_scores_and_recommend(
        top_supplements, user_symptoms, user_age, user_gender, user_pregnant
    )
    
    print("\nWhy This Product?")
    for explanation in why_this_product:
        print(f"- {explanation}")

    print("\nSpecific Recommendations:")
    for recommendation in specific_recommendations:
        print(f"- {recommendation}")


def process_wearable_data():
    print("We help you get connected... Hang tight while we convince the server to stop taking a coffee break!")
    time.sleep(4)
    display_tommy_analysis()
    show_health_dashboard()

def run_reminders():
    print("\nSetting up your personalized health reminders...")
    
    # Start reminder threads
    water_thread = threading.Thread(target=remind_to_drink_water, daemon=True)
    exercise_thread = threading.Thread(target=remind_to_exercise, daemon=True)
    standup_thread = threading.Thread(target=remind_to_stand_up, daemon=True)
    sleep_thread = threading.Thread(target=remind_to_sleep, daemon=True)

    # Start all threads
    water_thread.start()
    exercise_thread.start()
    standup_thread.start()
    sleep_thread.start()
    
    print("Reminders set! You'll receive notifications to help you stay on track with your health goals.")
    
    # Simulate some reminders (you can adjust or remove this if you want)
    time.sleep(2)  # Wait for 2 seconds
    print("\n🔔 Reminder: Don't forget to stay hydrated throughout the day!")
    time.sleep(1)  # Wait for 1 second
    print("🔔 Reminder: Take a moment to stand up and stretch!")


if __name__ == "__main__":
    main()