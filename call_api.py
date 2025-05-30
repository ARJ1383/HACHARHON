import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import os
import json
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Haversine function to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Get nearest restaurants
def get_nearest_restaurants(csv_path, your_lat, your_lng, top_n=100):
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['lat', 'lng'])
    df['distance_km'] = df.apply(
        lambda row: haversine(your_lat, your_lng, row['lat'], row['lng']), axis=1)
    nearest_df = df.sort_values('distance_km').head(top_n)
    return nearest_df

# Build menu dictionary
def build_filtered_menu_dict(menu_csv_path, restaurant_ids):
    menu_df = pd.read_csv(menu_csv_path)
    menu_df.columns = [col.strip() for col in menu_df.columns]
    menu_df = menu_df[menu_df['restaurant_id'].isin(restaurant_ids)]
    menu_dict = {}

    for _, row in menu_df.iterrows():
        rid = row['restaurant_id']
        item = {
            "id": row['restaurant_id'],
            "category": row['category'],
            "name": row['name'],
            "price": row['price']
        }
        menu_dict.setdefault(rid, []).append(item)

    return menu_dict

# Initialize OpenAI client
def init_openai_client():
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "tpsg-3AOhPdrYC4mTjcwxnsJ3RvYUqEPW9CY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.metisai.ir/openai/v1")
    )

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Get data from frontend
        data = request.json
        your_lat = float(data['location']['latitude'])
        your_lng = float(data['location']['longitude'])
        
        # Get other preferences
        request_data = {
            "dietType": data['dietType'],
            "activityLevel": data['activityLevel'],
            "allergies": data['allergies'],
            "bodyMetrics": data['bodyMetrics'],
            "price": data['price'],
            "dislikes": data['dislikes'],
            "comments": data['comments']
        }
        
        # Paths to CSV files
        restaurant_csv_path = 'restaurants.csv'
        menu_csv_path = 'restaurant_menus.csv'
        
        # Get nearest restaurants
        nearest_df = get_nearest_restaurants(restaurant_csv_path, your_lat, your_lng)
        nearest_ids = set(nearest_df['id'])
        
        # Get menus for those restaurants
        nearest_menus = build_filtered_menu_dict(menu_csv_path, nearest_ids)
        
        # Merge restaurants with their menus
        result = {}
        for _, row in nearest_df.iterrows():
            rid = row['id']
            result[rid] = {
                "name": row['name'],
                "category": row['category'],
                "address": row['full_address'],
                "lat": row['lat'],
                "lng": row['lng'],
                "distance_km": row['distance_km'],
            }
        
        # Build prompt for OpenAI
        prompt = f"""User Request: {json.dumps(request_data, indent=2)}
Nearby restaurants: {json.dumps(list(nearest_menus.values()), indent=2)}

Recommend exactly five unique restaurants with specific dishes that match the user's preferences. 
For each, output a JSON object with:
- "id": restaurant ID
- "dish": recommended dish name
- "reason": why it matches user's preferences

Return a JSON array of five objects. Example:
[
  {{
    "id": "resto123",
    "dish": "Grilled Tofu Bowl",
    "reason": "High-protein, gluten-free, no nuts or dairy"
  }}
]"""
        
        # Query OpenAI
        client = init_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful dietitian and restaurant recommender."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        # Parse response
        response_content = response.choices[0].message.content
        recommendations = json.loads(response_content).get('recommendations', [])
        
        # Add restaurant details to recommendations
        for rec in recommendations:
            rid = rec['id']
            if rid in result:
                rec.update(result[rid])
        
        return jsonify(recommendations)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)