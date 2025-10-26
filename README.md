# 🤖 AI Diet-Aware Restaurant Recommender

🏆 **Project for the Sharif University of Technology "LLM Hackathon"**

This project is an intelligent agent designed to bridge the gap between complex dietary needs and local restaurant options. It acts as a personal dietitian and food-finder, taking a user's detailed health profile and location, and returning a curated list of specific, recommended dishes from nearby restaurants.

## 📝 Overview

Finding a restaurant is easy. Finding a restaurant that serves a specific dish matching your diet (e.g., "high-protein, low-carb, no peanuts"), your fitness goals, and your personal taste is incredibly difficult.

This agent solves that problem. It ingests a user's complete profile—including:
* **Dietary Preferences:** (e.g., Vegan, Keto, Paleo, Vegetarian)
* **Health Goals:** (e.g., High-Protein, Low-Calorie, based on `activityLevel` and `bodyMetrics`)
* **Allergies & Dislikes:** (e.g., `allergies: ["peanuts"]`, `dislikes: ["cilantro"]`)
* **Budget:** (e.g., `price: "moderate"`)
* **Location:** (Latitude and Longitude)

It then scans a database of local restaurants and their *full menus*, using an LLM to reason like a dietitian and recommend *exactly five specific dishes* that perfectly match the user's needs.

## ✨ Key Features

* **Hyper-Personalized:** Moves beyond simple tags like "vegan." The AI analyzes activity levels, body metrics, and dislikes for truly tailored suggestions.
* **Location-Aware:** Uses the **Haversine formula** to calculate the distance to all restaurants and prioritizes the top 100 closest options.
* **Dish-Specific:** Doesn't just recommend a restaurant; it recommends a *specific dish* from its menu.
* **LLM-Powered Reasoning:** Leverages a `gpt-4o-mini` model to analyze the user's preferences against menu items and provide a clear **reason** for each recommendation.
* **Scalable Backend:** Built with a lightweight **Flask** API to handle requests and serve JSON responses, making it easy to connect to any frontend application.

---

## ⚙️ System Architecture (How It Works)

The application operates as a single-endpoint data processing pipeline:

1.  **Receive Request:** The Flask server listens for a `POST` request on `/recommend`. The request body must contain the user's `location` (lat/lng) and their preference data (diet, allergies, etc.).
2.  **Filter by Location:** The `get_nearest_restaurants` function reads `restaurants.csv` and uses the Haversine formula to calculate the distance to every restaurant, sorting them to find the **Top 100 nearest**.
3.  **Build Context:** The `build_filtered_menu_dict` function reads `restaurant_menus.csv` and creates a in-memory JSON-like dictionary of *only* the menus for the 100 restaurants identified in step 2.
4.  **Construct Prompt:** A detailed prompt is dynamically generated for the LLM. This prompt includes:
    * The user's entire preference JSON.
    * The complete menu data for all nearby restaurants.
    * A strict instruction to return *exactly five* unique restaurant/dish recommendations in a specific JSON format.
5.  **Query LLM Agent:** The prompt is sent to the `gpt-4o-mini` model. The LLM acts as the "dietitian" agent, analyzing the two large blocks of data to find the best matches.
6.  **Hydrate & Respond:** The LLM's response (containing `id`, `dish`, `reason`) is parsed. The application then merges this with the full restaurant details (name, address, distance) and returns the final, enriched JSON array to the user.

---

## 🛠️ Tech Stack

* **Backend:** Flask
* **Data Processing:** Pandas
* **LLM Agent:** OpenAI API (`gpt-4o-mini`)
* **Core Language:** Python
* **Geospatial:** `math` library (for Haversine distance)

---

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.7+
* `restaurants.csv` and `restaurant_menus.csv` data files in the root directory.

### 2. Clone the Repository

```bash
git clone [YOUR_REPOSITORY_LINK]
cd [YOUR_PROJECT_DIRECTORY]
