from flask import Flask, request, render_template
import pickle
import pandas as pd
import os
import random

app = Flask(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load recommender system data
medicines_dict_path = os.path.join(BASE_DIR, 'medicine_dict.pkl')
similarity_path = os.path.join(BASE_DIR, 'similarity.pkl')

with open(medicines_dict_path, 'rb') as f:
    medicines_dict = pickle.load(f)

medicines = pd.DataFrame(medicines_dict)

with open(similarity_path, 'rb') as f:
    similarity = pickle.load(f)

# --- Price Generation Logic ---

# Function to generate base price
def base_price(name):
    name = name.lower()
    if 'paracetamol' in name:
        return round(random.uniform(10, 50), 2)
    elif 'dolo' in name or 'fever' in name:
        return round(random.uniform(20, 60), 2)
    elif 'azithromycin' in name or 'antibiotic' in name:
        return round(random.uniform(50, 150), 2)
    elif 'cetrizine' in name or 'allergy' in name:
        return round(random.uniform(10, 40), 2)
    else:
        return round(random.uniform(15, 200), 2)

# Slight price variation per source
def price_variation(price):
    return round(price * random.uniform(0.95, 1.10), 2)  # ±5–10%

# Create a price table for all medicines
def generate_prices(medicine_list):
    price_data = []
    for med in medicine_list:
        base = base_price(med)
        price_data.append({
            "Drug_Name": med,
            "PharmEasy": price_variation(base),
            "1mg": price_variation(base),
            "Netmeds": price_variation(base)
        })
    return price_data

# --- Recommendation Function ---
def recommend(medicine):
    medicine_index = medicines[medicines['Drug_Name'] == medicine].index[0]
    distances = similarity[medicine_index]
    medicines_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_medicines = []
    for i in medicines_list:
        recommended_medicines.append(medicines.iloc[i[0]].Drug_Name)
    return recommended_medicines

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    prices = []
    selected_medicine_name = None

    if request.method == 'POST':
        selected_medicine_name = request.form['medicine']
        recommendations = recommend(selected_medicine_name)
        # Include the selected medicine itself for price comparison
        all_meds = [selected_medicine_name] + recommendations
        prices = generate_prices(all_meds)

    return render_template(
        'index.html',
        medicines=medicines['Drug_Name'].values,
        recommendations=recommendations,
        prices=prices,
        selected_medicine_name=selected_medicine_name
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
