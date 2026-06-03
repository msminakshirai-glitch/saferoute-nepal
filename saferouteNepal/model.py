import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "historical_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "risk_model.pkl")

# Create models folder if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)

def train_model():
    # Load historical data
    df = pd.read_csv(DATA_PATH)

    # X = the input features (what the model learns from)
    # y = the answer we want the model to predict
    X = df[["rainfall_mm", "slope_degrees", "landslide_history", "flood_history"]]
    y = df["risk_level"]

    # Split data into training and testing
    # 80% trains the model, 20% tests how accurate it is
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create and train the Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Test accuracy
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model accuracy: {round(accuracy * 100, 1)}%")

    # Save the trained model to a file
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print("Model saved successfully!")

def predict_risk(rainfall, slope, landslide_history, flood_history):
    """
    Use the trained model to predict risk level.
    Returns: "LOW", "MEDIUM", or "HIGH"
    """
    # Load the saved model
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    # Make prediction
    prediction = model.predict([[rainfall, slope, landslide_history, flood_history]])

    # Convert number back to text
    risk_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    return risk_map[prediction[0]]

# Train the model when this file is run directly
if __name__ == "__main__":
    print("Training model...")
    train_model()

    # Test it with a sample road
    result = predict_risk(75, 35, 5, 2)
    print(f"Test prediction for high risk road: {result}")

    result = predict_risk(10, 10, 0, 0)
    print(f"Test prediction for safe road: {result}")