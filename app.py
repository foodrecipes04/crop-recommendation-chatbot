import pandas as pd
import joblib
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Load dataset (ensure it includes Soil_Type, Crop_Type, Fertilizer)
df = pd.read_csv("f2.csv")

# Encode categorical columns
label_encoders = {}
categorical_cols = ["Soil_Type", "Crop_Type", "Fertilizer"]
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Train models
X = df.drop(columns=["Crop_Type", "Fertilizer"])
y_crop = df["Crop_Type"]
y_fert = df["Fertilizer"]

X_train, X_test, y_crop_train, y_crop_test = train_test_split(X, y_crop, test_size=0.2, random_state=42)
crop_model = RandomForestClassifier(n_estimators=100, random_state=42)
crop_model.fit(X_train, y_crop_train)

fert_model = RandomForestClassifier(n_estimators=100, random_state=42)
fert_model.fit(X_train, y_fert)

# Also train model for next crop
X_next_crop = df.drop(columns=["Crop_Type", "Fertilizer"])
y_next_crop = df["Crop_Type"]
next_crop_model = RandomForestClassifier(n_estimators=100, random_state=42)
next_crop_model.fit(X_next_crop, y_next_crop)

# Save models and encoders (optional if you want to reuse without retraining)
joblib.dump(crop_model, "crop_model.pkl")
joblib.dump(fert_model, "fertilizer_model.pkl")
joblib.dump(next_crop_model, "next_crop_model.pkl")
for col, le in label_encoders.items():
    joblib.dump(le, f"{col}_encoder.pkl")

# Load models and encoders
crop_model = joblib.load("crop_model.pkl")
fert_model = joblib.load("fertilizer_model.pkl")
next_crop_model = joblib.load("next_crop_model.pkl")
label_encoders = {col: joblib.load(f"{col}_encoder.pkl") for col in categorical_cols}

# Crop rotation rules
heavy_feeders = {"Wheat", "Rice", "Corn", "Sugarcane"}
light_feeders = {"Carrot", "Onion", "Garlic"}
nitrogen_fixers = {"Peas", "Lentils", "Soybean"}

def apply_crop_rotation_rules(first_crop):
    if first_crop in heavy_feeders:
        return "Peas"
    elif first_crop in nitrogen_fixers:
        return "Carrot"
    elif first_crop in light_feeders:
        return "Wheat"
    return first_crop

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Required inputs
        nitrogen = data["N"]
        phosphorus = data["P"]
        potassium = data["K"]
        temperature = data["temperature"]
        humidity = data["humidity"]
        moisture = data["moisture"]
        soil_type = data["soil_type"]  # String like "Loamy"

        # Encode soil
        soil_encoded = label_encoders["Soil_Type"].transform([soil_type])[0]

        # Prepare input
        input_df = pd.DataFrame([{
            "Temparature": temperature,
            "Humidity": humidity,
            "Moisture": moisture,
            "Soil_Type": soil_encoded,
            "Nitrogen": nitrogen,
            "Potassium": potassium,
            "Phosphorous": phosphorus
        }])

        # Predict crop and fertilizer
        crop_encoded = crop_model.predict(input_df)[0]
        fert_encoded = fert_model.predict(input_df)[0]

        crop = label_encoders["Crop_Type"].inverse_transform([crop_encoded])[0]
        fertilizer = label_encoders["Fertilizer"].inverse_transform([fert_encoded])[0]

        # Predict next crop
        next_crop_encoded = next_crop_model.predict(input_df)[0]
        next_crop_ml = label_encoders["Crop_Type"].inverse_transform([next_crop_encoded])[0]

        # Apply crop rotation logic
        next_crop_final = apply_crop_rotation_rules(crop)

        # Predict fertilizer for next crop
        next_crop_encoded_adjusted = label_encoders["Crop_Type"].transform([next_crop_final])[0]
        input_df_next_fert = input_df.copy()
        input_df_next_fert["Crop_Type"] = next_crop_encoded_adjusted

        next_fert_encoded = fert_model.predict(input_df_next_fert)[0]
        next_fertilizer = label_encoders["Fertilizer"].inverse_transform([next_fert_encoded])[0]

        return jsonify({
            "recommended_crop": crop,
            "recommended_fertilizer": fertilizer,
            "next_crop_for_soil_health": next_crop_final,
            "recommended_fertilizer_for_next_crop": next_fertilizer
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
