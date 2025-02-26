

# Import necessary libraries
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Initialize Flask app
app = Flask(__name__)

# Load dataset
df = pd.read_csv("crop_recommendation.csv")

# Prepare features (X) and target (y)
X = df.drop(columns=["label"])
y = df["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, "crop_recommendation_model.pkl")

print("✅ Model trained and saved successfully!")

# Load trained model
model = joblib.load("crop_recommendation_model.pkl")

# Define prediction route
@app.route("/predict", methods=["POST"])
def predict():

    try:
        # Get JSON data from request
        data = request.get_json()

        # Extract values from input JSON
        N = data["N"]
        P = data["P"]
        K = data["K"]
        temperature = data["temperature"]
        humidity = data["humidity"]
        ph = data["ph"]
        rainfall = data["rainfall"]

        # Prepare input for model
        input_data = [[N, P, K, temperature, humidity, ph, rainfall]]

        # Make prediction
        predicted_crop = model.predict(input_data)[0]

        # Return prediction result
        return jsonify({"recommended_crop": predicted_crop})

    except Exception as e:
        return jsonify({"error": str(e)})

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
