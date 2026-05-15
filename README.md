# Agricultural Decision Support System

A hybrid ML and rule-based advisory system for rice farmers in Bihar, India.

## Features

- **Soil Analysis** - XGBoost model (98.7% accuracy)
- **Leaf Diagnosis** - KNN model with 17 visual features (81% accuracy)
- **Fertilizer Recommendations** - NPK quantities based on Bihar standards
- **Disease Risk Assessment** - Weather-based predictions
- **Economic Impact** - Revenue and loss calculations

## Tech Stack

- Python 3.11
- Flask
- XGBoost
- scikit-learn
- OpenCV
- HTML, CSS, JavaScript

## Quick Start

1. Clone the repository
2. Run: pip install -r requirements.txt
3. Run: python app.py
4. Open: http://localhost:5000

## Project Structure

- app.py - Flask backend
- advisory_engine.py - Rule-based advisory logic
- leaf_features.py - Feature extraction for leaf images
- models/ - Trained ML models
- static/ - CSS, JS, HTML files
- MAIN/models/ - Screenshots

## Model Performance

- XGBoost: Soil Fertility - 98.7% accuracy
- KNN: Leaf Deficiency - 81.0% accuracy

## Screenshots

Soil Analysis: MAIN/models/soil_screenshot.png
Leaf Diagnosis: MAIN/models/leaf_screenshot.png

