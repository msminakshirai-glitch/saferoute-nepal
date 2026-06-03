import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "roads.csv")

df = pd.read_csv(CSV_PATH)

print("=== SafeRoute Nepal - Road Risk Report ===\n")
print(f"Loaded {len(df)} roads from database.\n")

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

for index, road in df.iterrows():
    risk = calculate_risk(road)

    if risk == "HIGH":
        symbol = "[!!!]"
    elif risk == "MEDIUM":
        symbol = "[ ! ]"
    else:
        symbol = "[ OK]"

    print(f"{symbol} {road['road_name']}")
    print(f"       Risk Level : {risk}")
    print(f"       Rainfall   : {road['rainfall_mm']} mm")
    print(f"       Slope      : {road['slope_degrees']} degrees")
    print(f"       Past Events: {road['landslide_history']} landslides, {road['flood_history']} floods")
    print()

print("=== End of Report ===")
