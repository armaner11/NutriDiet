from flask import Flask, request, render_template, send_file
import pandas as pd
from fpdf import FPDF


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# Load dataset
df = pd.read_csv("datasetfornutridiet.csv")

def filter_foods(goal, diet_type):
    if goal == "Weight Loss":
        foods = df[df['energy_kcal'] < 300]
    elif goal == "Muscle Gain":
        foods = df[df['protein_g'] > 10]
    else:  # Maintain
        foods = df[(df['energy_kcal'] >= 300) & (df['energy_kcal'] <= 500)]
    return foods

def generate_plan(days, goal, diet_type):
    foods = filter_foods(goal, diet_type)
    plan = {}
    for day in range(1, days+1):
        plan[f"Day {day}"] = {
            "Breakfast": foods.sample(1).iloc[0]['food_name'],
            "Lunch": foods.sample(1).iloc[0]['food_name'],
            "Dinner": foods.sample(1).iloc[0]['food_name'],
            "Snacks": foods.sample(1).iloc[0]['food_name']
        }
    return plan


def is_nonveg(food_name):
    nonveg_keywords = ["chicken", "mutton", "fish", "egg", "prawn", "beef", "meat"]
    return any(word.lower() in food_name.lower() for word in nonveg_keywords)

def filter_foods(goal, diet_type):
    # Goal based filter
    if goal == "Weight Loss":
        foods = df[df['energy_kcal'] < 300]
    elif goal == "Muscle Gain":
        foods = df[df['protein_g'] > 10]
    else:
        foods = df[(df['energy_kcal'] >= 300) & (df['energy_kcal'] <= 500)]

    # Veg/Non-Veg filter
    if diet_type == "Veg":
        foods = foods[~foods['food_name'].apply(is_nonveg)]
    else:
        foods = foods[foods['food_name'].apply(is_nonveg)]

    return foods


def save_plan_pdf(plan, filename="diet_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Your Diet Plan", ln=True, align="C")
    for day, meals in plan.items():
        pdf.cell(200, 10, txt=day, ln=True)
        for meal, food in meals.items():
            pdf.cell(200, 10, txt=f"{meal}: {food}", ln=True)
    pdf.output(filename)
    return filename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/diet", methods=["POST"])
def diet_plan():
    diet_type = request.form["diet_type"]
    age = request.form["age"]
    weight = request.form["weight"]
    height = request.form["height"]
    goal = request.form["goal"]
    workout_days = request.form["workout_days"]

    plan = generate_plan(7, goal, diet_type)  # Default 7-day plan
    filename = save_plan_pdf(plan)
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
