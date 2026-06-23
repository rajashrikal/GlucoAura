💨 GlucoAura — AI-Powered Breath-Based Glucose Monitor
No Needles. No Patches. No Pain. Just Breathe.

Presented at Cognizant® Technoverse Hackathon 2026 | 22,000+ Innovators

📌 Problem Statement


537 million adults worldwide live with diabetes. Every single day, they must prick their fingers multiple times just to know their blood sugar level.



Current SolutionProblem💉 Finger-prick testsPainful, invasive, biohazard waste📱 CGM Patches₹500+ per patch, skin irritation⌚ SmartwatchesNot FDA-cleared, inaccurate across skin tones❌ Universal non-invasive deviceDoes not exist yet


💡 Our Solution — GlucoAura

GlucoAura is a Flask + Python AI-powered web application that simulates a handheld breath-based glucose monitor.

The user answers 3 simple questions — the Python backend automatically simulates what hardware sensors would detect (acetone, humidity, CO₂) and runs an AI model to predict blood glucose.

User answers 3 questions
        ↓
Flask backend receives data (/scan route)
        ↓
Python AI simulates MOS sensor readings (acetone, humidity, CO₂)
        ↓
TinyML-style Neural Network predicts glucose (mg/dL)
        ↓
Result shown on interactive device screen in browser


🔬 The Science

When blood sugar rises, the body burns fat → produces acetone → exhaled in breath.

ConditionBreath AcetoneBlood Glucose🟢 Healthy0.3 – 0.9 ppm70 – 99 mg/dL🟡 Pre-Diabetic0.9 – 1.8 ppm100 – 125 mg/dL🔴 Diabetic> 1.8 ppm126+ mg/dL
