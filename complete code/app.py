from flask import Flask, render_template, request, jsonify
import random
import math

app = Flask(__name__)

# ── Age calibration values ──────────────────────────────────────────────────
AGE_CALIBRATION = {
    "child":   -8,
    "teen":    -4,
    "adult":    0,
    "elderly":  7
}

# ── Meal offset values ──────────────────────────────────────────────────────
MEAL_OFFSET = {
    "fasting": -15,
    "2hr":       0,
    "30min":    25,
    "just":     40
}

# ── Symptom modifier ────────────────────────────────────────────────────────
SYMPTOM_MOD = {
    "great":   0,
    "tired":   5,
    "thirsty": 18,
    "shaky":  -12
}

# ── Acetone base by meal ────────────────────────────────────────────────────
ACETONE_BASE = {
    "fasting": 0.42,
    "2hr":     0.88,
    "30min":   1.28,
    "just":    1.68
}


def simulate_sensors(age, meal, symptoms):
    """
    Simulates what the physical MOS nano-sensors would detect.
    In real hardware, these values come from the sensor array automatically.
    The user NEVER inputs these — the device detects them.
    """
    age_mod     = {
        "child": -0.15, "teen": -0.05,
        "adult": 0.0,   "elderly": 0.20
    }.get(age, 0)

    symptom_mod = {
        "great": 0.0, "tired": 0.18,
        "thirsty": 0.52, "shaky": -0.22
    }.get(symptoms, 0)

    base_acetone = ACETONE_BASE.get(meal, 0.88)

    acetone  = round(max(0.3, min(3.0,
                   base_acetone + age_mod + symptom_mod +
                   (random.random() - 0.5) * 0.18)), 2)

    humidity = round(68 + random.random() * 22, 1)
    co2      = round(3.8 + random.random() * 0.8, 2)

    return acetone, humidity, co2


def predict_glucose(acetone, humidity, co2, age, meal, symptoms):
    """
    TinyML-style AI model:
    Maps acetone + corrections → blood glucose estimate (mg/dL)
    """
    # Base prediction from acetone (primary biomarker)
    glucose = 70 + (acetone - 0.3) * 95

    # Humidity correction (high humidity dilutes VOC signal)
    glucose += (humidity - 72) * (-0.2)

    # CO2 correction
    glucose += (co2 - 4.2) * 3.5

    # Age group calibration
    glucose += AGE_CALIBRATION.get(age, 0)

    # Meal timing offset
    glucose += MEAL_OFFSET.get(meal, 0)

    # Symptom modifier
    glucose += SYMPTOM_MOD.get(symptoms, 0)

    # Realistic noise (simulates sensor variance)
    glucose += (random.random() - 0.5) * 7

    return int(max(58, min(390, round(glucose))))


def get_confidence(acetone, humidity):
    """
    Calculates AI model confidence based on signal quality.
    """
    conf = 91
    if humidity > 90: conf -= 8
    if humidity < 50: conf -= 4
    if acetone < 0.5: conf -= 5
    conf += round((random.random() - 0.5) * 4)
    return max(79, min(97, conf))


def classify_glucose(glucose):
    """
    Classifies glucose reading and returns status + recommendation.
    """
    if glucose < 70:
        return {
            "label":  "LOW",
            "color":  "#EF4444",
            "rec":    "Low blood sugar detected. Eat something sweet immediately "
                      "and rest. If symptoms persist, seek medical help."
        }
    elif glucose < 100:
        return {
            "label":  "NORMAL",
            "color":  "#10B981",
            "rec":    "Your blood glucose is in the healthy fasting range. "
                      "Keep up your current diet and activity levels. ✅"
        }
    elif glucose < 126:
        return {
            "label":  "BORDERLINE",
            "color":  "#F59E0B",
            "rec":    "Slightly above normal. Reduce sugary foods and increase "
                      "physical activity. Monitor regularly."
        }
    elif glucose < 200:
        return {
            "label":  "ELEVATED",
            "color":  "#F59E0B",
            "rec":    "Pre-diabetic range detected. Please consult a healthcare "
                      "provider for further evaluation."
        }
    else:
        return {
            "label":  "HIGH",
            "color":  "#EF4444",
            "rec":    "High blood sugar detected. Please seek medical advice "
                      "promptly. Avoid carbohydrate-heavy foods."
        }


# ── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    """
    Receives user's 3 answers → runs AI model → returns glucose result.
    All sensor simulation happens here on the server (represents device firmware).
    """
    data     = request.get_json()
    age      = data.get("age",      "adult")
    meal     = data.get("meal",     "2hr")
    symptoms = data.get("symptoms", "great")

    # Step 1: Simulate sensor readings (auto-detected by device hardware)
    acetone, humidity, co2 = simulate_sensors(age, meal, symptoms)

    # Step 2: Run AI glucose prediction
    glucose = predict_glucose(acetone, humidity, co2, age, meal, symptoms)

    # Step 3: Get AI confidence score
    confidence = get_confidence(acetone, humidity)

    # Step 4: Classify and get recommendation
    status = classify_glucose(glucose)

    # Return full result to frontend
    return jsonify({
        "glucose":    glucose,
        "acetone":    acetone,
        "humidity":   humidity,
        "co2":        co2,
        "confidence": confidence,
        "label":      status["label"],
        "color":      status["color"],
        "rec":        status["rec"]
    })

if __name__ == "__main__":
    app.run(debug=True)