import pandas as pd
import folium
import os

# Build file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "roads.csv")
MAP_PATH = os.path.join(BASE_DIR, "maps", "risk_map.html")

# Load road data
df = pd.read_csv(CSV_PATH)

# Risk calculation (same as main.py)
def calculate_risk(road):
    score = 0

    if road["rainfall_mm"] >= 70:
        score += 3
    elif road["rainfall_mm"] >= 40:
        score += 2
    elif road["rainfall_mm"] >= 15:
        score += 1

    if road["slope_degrees"] >= 35:
        score += 3
    elif road["slope_degrees"] >= 25:
        score += 2
    elif road["slope_degrees"] >= 15:
        score += 1

    total_history = road["landslide_history"] + road["flood_history"]
    if total_history >= 5:
        score += 3
    elif total_history >= 2:
        score += 2
    elif total_history >= 1:
        score += 1

    if score >= 7:
        return "HIGH"
    elif score >= 4:
        return "MEDIUM"
    else:
        return "LOW"

# Color for each risk level
def get_color(risk):
    if risk == "HIGH":
        return "red"
    elif risk == "MEDIUM":
        return "orange"
    else:
        return "green"

# These are the real GPS coordinates of each road in Nepal
road_coordinates = {
    "Dharan-Dhankuta Highway":    [26.8127, 87.2816],
    "Kathmandu-Pokhara Highway":  [27.9881, 84.0000],
    "Sindhuli Road":              [27.2500, 85.9700],
    "Prithvi Highway":            [27.8000, 84.9800],
    "Tribhuvan Highway":          [27.6000, 85.1900],
}

# Create the map centered on Nepal
nepal_map = folium.Map(location=[28.3949, 84.1240], zoom_start=7)

# Add a marker for each road
for index, road in df.iterrows():
    risk = calculate_risk(road)
    color = get_color(risk)
    coords = road_coordinates[road["road_name"]]

    # This creates the popup text you see when you click a marker
    popup_text = f"""
    <b>{road['road_name']}</b><br>
    Risk Level: {risk}<br>
    Rainfall: {road['rainfall_mm']} mm<br>
    Slope: {road['slope_degrees']} degrees<br>
    Landslides: {road['landslide_history']}<br>
    Floods: {road['flood_history']}
    """

    folium.CircleMarker(
        location=coords,
        radius=15,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=200)
    ).add_to(nepal_map)

# Save the map as an HTML file
nepal_map.save(MAP_PATH)
print("Map saved! Open maps/risk_map.html in your browser.")