# ============================================================
# app.py
# Flask REST API — Rice Crop Decision Support System
# ============================================================

from flask import Flask, request, jsonify, send_from_directory
import joblib
import numpy as np
import os
from advisory_engine import get_complete_advisory

app = Flask(__name__, static_folder='static', static_url_path='')

print("Loading models...")

fertility_model = joblib.load('models/xgboost_fertility.pkl')
label_encoder = joblib.load('models/label_encoder_fertility.pkl')

print("Fertility model loaded successfully!")
print("Using rule-based advisory engine for recommendations and yield estimates")


def predict_fertility(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    input_array = np.array([[nitrogen, phosphorus, potassium,
                              temperature, humidity, ph, rainfall]])
    prediction_encoded = fertility_model.predict(input_array)
    fertility_class = label_encoder.inverse_transform(prediction_encoded)[0]
    return fertility_class


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug print

        nitrogen     = float(data['nitrogen'])
        phosphorus   = float(data['phosphorus'])
        potassium    = float(data['potassium'])
        temperature  = float(data['temperature'])
        humidity     = float(data['humidity'])
        ph           = float(data['ph'])
        rainfall     = float(data['rainfall'])
        growth_stage = int(data['growth_stage'])
        fym_available = float(data.get('fym_available', 0))
        
        print(f"FYM Available: {fym_available}")  # Debug print

        ml_fertility = predict_fertility(nitrogen, phosphorus, potassium,
                                          temperature, humidity, ph, rainfall)

        advisory = get_complete_advisory(
            nitrogen, phosphorus, potassium,
            temperature, humidity, ph,
            rainfall, growth_stage, fym_available
        )

        response = {
            'success': True,
            'ml_fertility': ml_fertility,
            'fertility': advisory['fertility'],
            'fertility_color': advisory['fertility_color'],
            'fertility_score': advisory['fertility_score'],
            'deficiency': advisory['deficiency'],
            'fertilizer': advisory['fertilizer'],
            'irrigation': advisory['irrigation'],
            'disease_risk': advisory['disease_risk'],
            'yield_impact': advisory['yield_impact'],
            'soil_amendments': advisory['soil_amendments'],
            'economics': advisory['economics'],
            'inputs': {
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall,
                'growth_stage': growth_stage,
                'fym_available': fym_available
            }
        }
        
        response['ml_economics'] = {
            'potential_revenue_inr': advisory['economics']['potential_revenue_inr'],
            'expected_revenue_inr': advisory['economics']['expected_revenue_inr'],
            'economic_loss_inr': advisory['economics']['revenue_loss_inr'],
            'price_per_quintal_inr': 2300
        }

        return jsonify(response)

    except KeyError as e:
        return jsonify({'success': False, 'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        print(f"Error: {e}")  # Debug print
        return jsonify({'success': False, 'error': str(e)}), 500





@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'fertility_model': 'xgboost_fertility.pkl',
        'advisory_engine': 'rule-based (Bihar agronomic standards)'
    })

@app.route('/leaf')
def leaf():
    return send_from_directory('static', 'leaf.html')

@app.route('/predict_leaf', methods=['POST'])
def predict_leaf():
    try:
        if 'leaf' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['leaf']
        
        # Save temporarily
        import tempfile
        temp_path = os.path.join(tempfile.gettempdir(), 'uploaded_leaf.jpg')
        file.save(temp_path)
        
        # Extract features
        from leaf_features import extract_all_features_improved
        features_dict = extract_all_features_improved(temp_path)
        
        if features_dict is None:
            os.remove(temp_path)
            return jsonify({'success': False, 'error': 'Could not process image'}), 400
        
        # Load model and components
        knn = joblib.load('models/knn_leaf_model.pkl')
        scaler = joblib.load('models/knn_scaler.pkl')
        feature_cols = joblib.load('models/knn_feature_columns.pkl')
        
        # Convert features to array in correct order
        features_list = []
        for col in feature_cols:
            features_list.append(features_dict.get(col, 0))
        features_array = np.array(features_list).reshape(1, -1)
        
        # Scale and predict
        features_scaled = scaler.transform(features_array)
        prediction = knn.predict(features_scaled)[0]
        probabilities = knn.predict_proba(features_scaled)[0]
        confidence = max(probabilities) * 100
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'confidence': round(confidence, 1)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Rice Crop Decision Support System")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/predict")
    print("Health check: http://localhost:5000/health")
    print("="*50)
    print("\nArchitecture:")
    print("   - Fertility Classification: XGBoost ML Model")
    print("   - Recommendations & Yield: Rule-Based Advisory Engine")
    print("="*50 + "\n")
    app.run(debug=True)


