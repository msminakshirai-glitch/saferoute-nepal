import pandas as pd
import folium
import os
import time
from flask import Flask, render_template
from weather import get_rainfall_forecast
from model import predict_risk
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "roads.csv")

app = Flask(__name__)

cache = {}
CACHE_DURATION = 3600

def get_color(risk):
    if risk == "HIGH":
        return "red"
    elif risk == "MEDIUM":
        return "orange"
    else:
        return "green"

road_coordinates = {
    "Dharan-Dhankuta Highway":    [26.8127, 87.2816],
    "Kathmandu-Pokhara Highway":  [27.9881, 84.0000],
    "Sindhuli Road":              [27.2500, 85.9700],
    "Prithvi Highway":            [27.8000, 84.9800],
    "Tribhuvan Highway":          [27.6000, 85.1900],
    "Koshi Highway":              [26.9000, 86.7000],
    "Araniko Highway":            [27.7500, 85.6000],
    "Salleri-Phaplu Road":        [27.5000, 86.6000],
    "Bhimphedi-Hetauda Road":     [27.4167, 85.0333],
    "Banepa-Bardibas Road":       [27.6300, 85.5200],
    "Lamosangu-Jiri Road":        [27.6500, 85.9000],
    "Dumre-Besisahar Road":       [27.9500, 84.4000],
    "Baglung-Beni Road":          [28.2700, 83.6000],
    "Dolpa-Juphal Road":          [29.0000, 82.8000],
    "Humla-Simikot Road":         [29.9700, 81.8200],
    "Taplejung-Phidim Road":      [27.3500, 87.6700],
    "Ilam-Phidim Road":           [26.9100, 87.9200],
    "Diktel-Khotang Road":        [27.2200, 86.7900],
    "Salyan-Musikot Road":        [28.3700, 82.1600],
    "Jumla-Manma Road":           [29.2700, 82.1800],
}

def fetch_forecast_for_road(road_name):
    """Fetch forecast for one road - runs in parallel with others"""
    coords = road_coordinates[road_name]
    key = f"{coords[0]},{coords[1]}"
    now = time.time()

    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < CACHE_DURATION:
            return road_name, data

    data = get_rainfall_forecast(coords[0], coords[1])
    cache[key] = (data, now)
    return road_name, data

@app.route("/")
def home():
    df = pd.read_csv(CSV_PATH)
    nepal_map = folium.Map(location=[28.3949, 84.1240], zoom_start=7)
    road_list = []

    # Fetch all roads at the same time instead of one by one
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = dict(executor.map(
            fetch_forecast_for_road,
            df["road_name"].tolist()
        ))

    for index, road in df.iterrows():
        forecast = results[road["road_name"]]

        rain_today    = forecast[0]
        rain_tomorrow = forecast[1]
        rain_day3     = forecast[2]

        risk_today    = predict_risk(rain_today,    road["slope_degrees"], road["landslide_history"], road["flood_history"])
        risk_tomorrow = predict_risk(rain_tomorrow, road["slope_degrees"], road["landslide_history"], road["flood_history"])
        risk_day3     = predict_risk(rain_day3,     road["slope_degrees"], road["landslide_history"], road["flood_history"])

        coords = road_coordinates[road["road_name"]]
        color = get_color(risk_today)

        popup_text = (
            "<b>" + road["road_name"] + "</b><br><br>"
            + "<b>Today:</b> " + risk_today + " (" + str(rain_today) + " mm)<br>"
            + "<b>Tomorrow:</b> " + risk_tomorrow + " (" + str(rain_tomorrow) + " mm)<br>"
            + "<b>Day 3:</b> " + risk_day3 + " (" + str(rain_day3) + " mm)"
        )

        folium.CircleMarker(
            location=coords,
            radius=15,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=220)
        ).add_to(nepal_map)

        road_list.append({
            "name": road["road_name"],
            "risk_today": risk_today,
            "risk_tomorrow": risk_tomorrow,
            "risk_day3": risk_day3,
            "rain_today": rain_today,
            "rain_tomorrow": rain_tomorrow,
            "rain_day3": rain_day3,
        })

    map_html = nepal_map._repr_html_()
    return render_template("index.html", map_html=map_html, roads=road_list)

if __name__ == "__main__":
    app.run(debug=True)