# ============================================================
# advisory_engine.py - Bihar Rice Crop Decision Support System
# Rule-based advisory engine using Bihar agronomic standards
# ============================================================

import math
from datetime import datetime


# -----------------------------------------------------------------------------
# SECTION 1 - Fertility Scoring with NPK Deficiency & Toxicity Detection
# Bihar Government Standards: N=120, P=60, K=60 kg/ha
# -----------------------------------------------------------------------------
def assign_fertility_with_deficiency(nitrogen, phosphorus, potassium,
                                      temperature, humidity, ph, rainfall):
    score = 0
    deficiency = {}
    
    # Define optimal ranges and toxic thresholds
    ranges = {
        'Nitrogen': {
            'optimal_low': 80,
            'optimal': 120,
            'optimal_high': 150,
            'toxic': 200,
            'max_points': 3,
            # Urea: Rs. 266 per 50kg bag, 46% N = 23kg N per bag
            # Cost per kg N = 266 / 23 = 11.57
            'price_per_kg': 11.57
        },
        'Phosphorus': {
            'optimal_low': 40,
            'optimal': 60,
            'optimal_high': 80,
            'toxic': 120,
            'max_points': 3,
            # DAP: Rs. 1,350 per 50kg bag, 46% P2O5 = 20% elemental P = 10kg P per bag
            # Cost per kg P = 1,350 / 10 = 135.00
            'price_per_kg': 135.00
        },
        'Potassium': {
            'optimal_low': 40,
            'optimal': 60,
            'optimal_high': 80,
            'toxic': 120,
            'max_points': 3,
            # MOP: Rs. 1,700 per 50kg bag, 60% K2O = 50% elemental K = 25kg K per bag
            # Cost per kg K = 1,700 / 25 = 68.00
            'price_per_kg': 68.00
        }
    }
    
    # ----- NITROGEN -----
    n = nitrogen
    n_range = ranges['Nitrogen']
    
    if n < n_range['optimal_low']:
        if n >= 60:
            score += 2
            deficit = n_range['optimal'] - n
            status = 'Slightly Low'
            severity = 'deficiency'
        elif n >= 40:
            score += 1
            deficit = n_range['optimal'] - n
            status = 'Deficient'
            severity = 'deficiency'
        else:
            deficit = n_range['optimal'] - n
            status = 'Severely Deficient'
            severity = 'deficiency'
            
        deficiency['Nitrogen'] = {
            'status': status,
            'deficit': round(deficit, 1),
            'deficit_pct': round(deficit / n_range['optimal'] * 100, 1),
            'severity': severity,
            'value': n,
            'optimal_target': n_range['optimal']
        }
        
    elif n > n_range['optimal_high']:
        excess = n - n_range['optimal']
        excess_pct = round(excess / n_range['optimal'] * 100, 1)
        
        if n >= n_range['toxic']:
            status = 'TOXIC - Severe Excess'
            score -= 5
            severity = 'toxic'
        elif n >= n_range['optimal_high'] * 1.5:
            status = 'Excessive - Reduce Application'
            score -= 3
            severity = 'excess_high'
        else:
            status = 'Above Optimal - Slight Excess'
            score -= 1
            severity = 'excess_low'
            
        deficiency['Nitrogen'] = {
            'status': status,
            'excess': round(excess, 1),
            'excess_pct': excess_pct,
            'severity': severity,
            'value': n,
            'optimal_target': n_range['optimal'],
            'warning': f'Excess Nitrogen ({excess} kg/ha above requirement) can cause lodging, pest attraction, and environmental pollution.'
        }
        
    else:
        score += n_range['max_points']
        deficiency['Nitrogen'] = {
            'status': 'Optimal',
            'deficit': 0,
            'deficit_pct': 0,
            'severity': 'optimal',
            'value': n,
            'optimal_target': n_range['optimal']
        }
    
    # ----- PHOSPHORUS -----
    p = phosphorus
    p_range = ranges['Phosphorus']
    
    if p < p_range['optimal_low']:
        if p >= 30:
            score += 2
            deficit = p_range['optimal'] - p
            status = 'Slightly Low'
        elif p >= 20:
            score += 1
            deficit = p_range['optimal'] - p
            status = 'Deficient'
        else:
            deficit = p_range['optimal'] - p
            status = 'Severely Deficient'
            
        deficiency['Phosphorus'] = {
            'status': status,
            'deficit': round(deficit, 1),
            'deficit_pct': round(deficit / p_range['optimal'] * 100, 1),
            'severity': 'deficiency',
            'value': p,
            'optimal_target': p_range['optimal']
        }
        
    elif p > p_range['optimal_high']:
        excess = p - p_range['optimal']
        
        if p >= p_range['toxic']:
            status = 'TOXIC - Severe Excess'
            score -= 5
            severity = 'toxic'
        elif p >= p_range['optimal_high'] * 1.5:
            status = 'Excessive - Reduce Application'
            score -= 3
            severity = 'excess_high'
        else:
            status = 'Above Optimal - Slight Excess'
            score -= 1
            severity = 'excess_low'
            
        deficiency['Phosphorus'] = {
            'status': status,
            'excess': round(excess, 1),
            'excess_pct': round(excess / p_range['optimal'] * 100, 1),
            'severity': severity,
            'value': p,
            'optimal_target': p_range['optimal'],
            'warning': f'Excess Phosphorus ({excess} kg/ha) reduces zinc/iron availability and causes algal blooms.'
        }
        
    else:
        score += p_range['max_points']
        deficiency['Phosphorus'] = {
            'status': 'Optimal',
            'deficit': 0,
            'deficit_pct': 0,
            'severity': 'optimal',
            'value': p,
            'optimal_target': p_range['optimal']
        }
    
    # ----- POTASSIUM -----
    k = potassium
    k_range = ranges['Potassium']
    
    if k < k_range['optimal_low']:
        if k >= 30:
            score += 2
            deficit = k_range['optimal'] - k
            status = 'Slightly Low'
            severity = 'deficiency'
        elif k >= 20:
            score += 1
            deficit = k_range['optimal'] - k
            status = 'Deficient'
            severity = 'deficiency'
        else:
            deficit = k_range['optimal'] - k
            status = 'Severely Deficient'
            severity = 'deficiency'
            
        deficiency['Potassium'] = {
            'status': status,
            'deficit': round(deficit, 1),
            'deficit_pct': round(deficit / k_range['optimal'] * 100, 1),
            'severity': severity,
            'value': k,
            'optimal_target': k_range['optimal']
        }
        
    elif k > k_range['optimal_high']:
        excess = k - k_range['optimal']
        excess_pct = round(excess / k_range['optimal'] * 100, 1)
        
        if k >= k_range['toxic']:
            status = 'TOXIC - Severe Excess'
            score -= 5
            severity = 'toxic'
        elif k >= k_range['optimal_high'] * 1.5:
            status = 'Excessive - Reduce Application'
            score -= 3
            severity = 'excess_high'
        else:
            status = 'Above Optimal - Slight Excess'
            score -= 1
            severity = 'excess_low'
            
        deficiency['Potassium'] = {
            'status': status,
            'excess': round(excess, 1),
            'excess_pct': excess_pct,
            'severity': severity,
            'value': k,
            'optimal_target': k_range['optimal'],
            'warning': f'Excess Potassium ({excess} kg/ha) can cause magnesium deficiency and salt stress.'
        }
        
    else:
        score += k_range['max_points']
        deficiency['Potassium'] = {
            'status': 'Optimal',
            'deficit': 0,
            'deficit_pct': 0,
            'severity': 'optimal',
            'value': k,
            'optimal_target': k_range['optimal']
        }
    
    # ----- pH -----
    if 5.5 <= ph <= 7.0:
        score += 2
        deficiency['pH'] = {'status': 'Optimal', 'severity': 'optimal'}
    elif 5.0 <= ph <= 7.5:
        score += 1
        deficiency['pH'] = {'status': 'Acceptable - Monitor', 'severity': 'warning'}
    elif ph < 4.5 or ph > 8.5:
        score -= 3
        deficiency['pH'] = {
            'status': 'Critical - Amendment Required',
            'severity': 'critical',
            'warning': 'Extreme pH locks up nutrients. Plants cannot access NPK even if present.'
        }
    elif ph < 5.0 or ph > 7.5:
        score -= 1
        deficiency['pH'] = {
            'status': 'Suboptimal - Amendment Recommended',
            'severity': 'warning',
            'warning': 'pH outside optimal range reduces nutrient availability by 15-30%.'
        }
    else:
        deficiency['pH'] = {'status': 'Acceptable', 'severity': 'good'}
    
    # ----- RAINFALL -----
    if 100 <= rainfall <= 300:
        score += 2
        deficiency['Rainfall'] = {'status': 'Optimal', 'severity': 'optimal'}
    elif 50 <= rainfall <= 350:
        score += 1
        deficiency['Rainfall'] = {'status': 'Adequate', 'severity': 'good'}
    elif rainfall > 400:
        score -= 2
        deficiency['Rainfall'] = {
            'status': 'Excessive - Waterlogging Risk',
            'severity': 'high_risk',
            'warning': 'High rainfall may cause flooding, nutrient leaching, and root diseases.'
        }
    elif rainfall < 30:
        score -= 1
        deficiency['Rainfall'] = {
            'status': 'Severe Drought Risk',
            'severity': 'critical',
            'warning': 'Extremely low rainfall - emergency irrigation needed.'
        }
    else:
        deficiency['Rainfall'] = {'status': 'Acceptable', 'severity': 'good'}
    
    # ----- TEMPERATURE -----
    if 20 <= temperature <= 35:
        score += 1
        deficiency['Temperature'] = {'status': 'Optimal', 'severity': 'optimal'}
    elif temperature > 40:
        score -= 2
        deficiency['Temperature'] = {
            'status': 'Heat Stress Risk',
            'severity': 'high_risk',
            'warning': 'High temperatures cause spikelet sterility and reduced grain filling.'
        }
    elif temperature < 15:
        score -= 1
        deficiency['Temperature'] = {
            'status': 'Cold Stress Risk',
            'severity': 'warning',
            'warning': 'Low temperatures slow growth and delay maturation.'
        }
    else:
        deficiency['Temperature'] = {'status': 'Acceptable', 'severity': 'good'}
    
    # ----- HUMIDITY -----
    if 40 <= humidity <= 80:
        score += 1
        deficiency['Humidity'] = {'status': 'Optimal', 'severity': 'optimal'}
    elif humidity > 85:
        score -= 2
        deficiency['Humidity'] = {
            'status': 'Very High - Severe Disease Risk',
            'severity': 'high_risk',
            'warning': 'High humidity (>85%) strongly promotes fungal diseases like blast and sheath blight.'
        }
    elif humidity > 80:
        score -= 1
        deficiency['Humidity'] = {
            'status': 'High - Disease Risk',
            'severity': 'warning',
            'warning': 'Elevated humidity increases disease pressure. Monitor for blast and sheath blight.'
        }
    elif humidity < 30:
        score -= 1
        deficiency['Humidity'] = {
            'status': 'Very Low - Moisture Stress',
            'severity': 'warning',
            'warning': 'Low humidity increases water demand and causes stress.'
        }
    else:
        deficiency['Humidity'] = {'status': 'Acceptable', 'severity': 'good'}
    
    # Fertility classification based on score (max 15 points)
    if score >= 10:
        fertility = 'High'
        fertility_color = 'green'
    elif score >= 6:
        fertility = 'Medium'
        fertility_color = 'yellow'
    elif score >= 2:
        fertility = 'Low'
        fertility_color = 'orange'
    elif score >= -5:
        fertility = 'Very Low - Critical Issues'
        fertility_color = 'red'
    else:
        fertility = 'Severe Problems - Expert Consultation Needed'
        fertility_color = 'darkred'
    
    # Toxicity summary for excess nutrients
    toxicity_summary = []
    excess_cost = 0
    for nutrient, data in deficiency.items():
        if nutrient in ['Nitrogen', 'Phosphorus', 'Potassium'] and data.get('severity') in ['excess_low', 'excess_high', 'toxic']:
            toxicity_summary.append(f"{nutrient}: {data['status']}")
            if 'excess' in data:
                price = ranges[nutrient]['price_per_kg']
                excess_cost += data['excess'] * price
    
    if toxicity_summary:
        deficiency['_toxicity_warning'] = {
            'message': 'EXCESS NUTRIENTS DETECTED - Reduce fertilizer application.',
            'details': toxicity_summary,
            'recommendation': 'Skip fertilizer this season. Focus on leaching/irrigation to reduce salt buildup.',
            'wasted_cost': round(excess_cost, 2)
        }
    
    return fertility, deficiency, fertility_color, score


# -----------------------------------------------------------------------------
# SECTION 2 - Disease Risk Prediction
# -----------------------------------------------------------------------------
def predict_disease_risk(temperature, humidity, growth_stage, rainfall, nitrogen, phosphorus, potassium):
    
    diseases = []
    overall_risk = 'Low'
    risk_factors = []
    recommendations = []
    
    # Check environmental conditions
    high_humidity = humidity >= 85
    moderate_humidity = humidity >= 75
    warm_temp = 24 <= temperature <= 32
    hot_temp = temperature > 35
    heavy_rain = rainfall > 150
    flowering_stage = growth_stage == 3
    
    # Fungal disease conditions
    if warm_temp and high_humidity:
        overall_risk = 'High' if humidity >= 90 else 'Medium'
        risk_factors.append(f'High humidity ({humidity}%) with warm temperature ({temperature}degC)')
        recommendations.append('Monitor field daily for disease symptoms')
        if humidity >= 90:
            recommendations.append('Consider preventive fungicide application')
    elif warm_temp and moderate_humidity:
        if overall_risk == 'Low':
            overall_risk = 'Low-Medium'
        risk_factors.append(f'Elevated humidity ({humidity}%)')
        recommendations.append('Monitor field regularly')
    
    # Bacterial disease conditions
    if warm_temp and humidity >= 80 and heavy_rain:
        if overall_risk in ['Low', 'Low-Medium']:
            overall_risk = 'High'
        risk_factors.append(f'Heavy rainfall ({rainfall}mm) combined with high humidity')
        recommendations.append('Ensure proper field drainage')
        recommendations.append('Avoid excess nitrogen application')
    elif warm_temp and humidity >= 80 and rainfall > 80:
        if overall_risk == 'Low':
            overall_risk = 'Medium'
        risk_factors.append(f'Moderate rainfall ({rainfall}mm) with high humidity')
        recommendations.append('Maintain good drainage')
    
    # Flowering stage vulnerability
    if flowering_stage and high_humidity:
        if overall_risk in ['Low', 'Low-Medium']:
            overall_risk = 'High' if humidity >= 90 else 'Medium'
        risk_factors.append('Critical flowering stage with high humidity')
        recommendations.append('This is the most vulnerable stage - monitor twice daily')
    
    # Heat stress
    if hot_temp:
        risk_factors.append(f'Heat stress risk at {temperature}degC')
        recommendations.append('Maintain standing water at 10cm depth')
        if overall_risk == 'Low':
            overall_risk = 'Medium'
    
    # NPK-related risk
    high_n = nitrogen > 150
    high_p = phosphorus > 80
    high_k = potassium > 80
    
    if high_n:
        risk_factors.append('Excess nitrogen increases disease susceptibility')
        recommendations.append('Reduce nitrogen fertilizer application')
        if overall_risk == 'Low':
            overall_risk = 'Medium'
        elif overall_risk == 'Medium':
            overall_risk = 'High'
    
    if high_p:
        risk_factors.append('Excess phosphorus indicates nutrient imbalance')
        
    if high_k:
        risk_factors.append('Excess potassium may cause salt stress')
    
    # Build consolidated advisory
    if overall_risk == 'High':
        advisory = 'HIGH DISEASE RISK - Take immediate preventive action.'
    elif overall_risk == 'Medium':
        advisory = 'MEDIUM DISEASE RISK - Monitor closely and prepare preventive measures.'
    elif overall_risk == 'Low-Medium':
        advisory = 'LOW-MEDIUM DISEASE RISK - Regular monitoring recommended.'
    else:
        advisory = 'LOW DISEASE RISK - Continue normal field management.'
    
    # Build weather note
    weather_note = ""
    if high_humidity:
        weather_note += " High humidity conditions favor fungal diseases."
    if heavy_rain:
        weather_note += " Wet conditions increase bacterial disease risk."
    if hot_temp:
        weather_note += " Heat stress may weaken plant resistance."
    
    return {
        'overall_risk': overall_risk,
        'risk_factors': risk_factors,
        'recommendations': recommendations,
        'advisory': advisory,
        'weather_note': weather_note.strip()
    }


# -----------------------------------------------------------------------------
# SECTION 3 - Yield Impact Estimation (in Quintals per Hectare)
# -----------------------------------------------------------------------------
def estimate_yield_impact(deficiency, disease_risk, temperature, ph, rainfall):
    
    # Bihar average rice yield: 25 quintals/ha (2024-25 estimate)
    base_yield = 25.0  # quintals per hectare
    
    loss_percentage = 0
    loss_factors = []
    
    # Nutrient impact on yield
    for nutrient in ['Nitrogen', 'Phosphorus', 'Potassium']:
        if nutrient in deficiency:
            data = deficiency[nutrient]
            severity = data.get('severity', '')
            
            if severity == 'toxic':
                loss_percentage += 25
                loss_factors.append(f"{nutrient} toxicity: 25% loss")
            elif severity == 'excess_high':
                loss_percentage += 15
                loss_factors.append(f"{nutrient} excess: 15% loss")
            elif severity == 'deficiency':
                deficit_pct = data.get('deficit_pct', 0)
                if deficit_pct > 50:
                    loss = 20
                elif deficit_pct > 30:
                    loss = 15
                else:
                    loss = 10
                loss_percentage += loss
                loss_factors.append(f"{nutrient} deficiency: {loss}% loss")
    
    # pH impact on yield
    if 'pH' in deficiency:
        ph_status = deficiency['pH'].get('status', '')
        if 'Critical' in ph_status:
            loss_percentage += 30
            loss_factors.append("Extreme pH: 30% loss (nutrient lockout)")
        elif 'Suboptimal' in ph_status:
            loss_percentage += 15
            loss_factors.append("Suboptimal pH: 15% loss (reduced nutrient availability)")
    
    # Temperature impact on yield
    if 'Temperature' in deficiency:
        temp_status = deficiency['Temperature'].get('status', '')
        if 'Heat Stress' in temp_status:
            loss_percentage += 20
            loss_factors.append("Heat stress: 20% loss")
        elif 'Cold Stress' in temp_status:
            loss_percentage += 15
            loss_factors.append("Cold stress: 15% loss")
    
    # Disease impact on yield
    if disease_risk['overall_risk'] == 'High':
        loss_percentage += 40
        loss_factors.append("High disease risk: 40% loss potential")
    elif disease_risk['overall_risk'] == 'Medium':
        loss_percentage += 20
        loss_factors.append("Medium disease risk: 20% loss potential")
    
    # Water impact on yield
    if 'Rainfall' in deficiency:
        rain_status = deficiency['Rainfall'].get('status', '')
        if 'Waterlogging' in rain_status:
            loss_percentage += 25
            loss_factors.append("Waterlogging risk: 25% loss")
        elif 'Drought' in rain_status:
            loss_percentage += 35
            loss_factors.append("Drought risk: 35% loss")
    
    # Humidity impact (disease amplification)
    if 'Humidity' in deficiency:
        hum_status = deficiency['Humidity'].get('status', '')
        if 'Severe Disease Risk' in hum_status:
            loss_percentage += 15
            loss_factors.append("Extreme humidity: Disease amplification")
    
    loss_percentage = min(loss_percentage, 90)  # Cap at 90% loss
    expected_yield = base_yield * (1 - loss_percentage / 100)
    # Rice price: Rs. 2,300 per quintal (MSP for common paddy)
    price_per_quintal = 2300
    economic_loss = (base_yield - expected_yield) * price_per_quintal
    
    return {
        'potential_yield_quintals': round(base_yield, 1),
        'expected_yield_quintals': round(expected_yield, 1),
        'loss_percentage': round(loss_percentage, 1),
        'loss_factors': loss_factors,
        'economic_loss_inr': round(economic_loss, 0),
        'revenue_at_risk': round(base_yield * price_per_quintal, 0),
        'baseline_note': 'Based on Bihar average rice yield (25 quintals/ha, 2024-25)'
    }


# -----------------------------------------------------------------------------
# SECTION 4 - Soil Amendment Recommendations
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# SECTION 4 - Soil Amendment Recommendations
# -----------------------------------------------------------------------------
def soil_amendment_recommendations(ph, deficiency, growth_stage, fym_available=0):
    
    amendments = []
    
    # Define stage-based rules for amendments
    stage_rules = {
        'lime': {
            1: {'allowed': True, 'note': 'Apply 3-4 months before planting. Incorporate into top 15cm soil.'},
            2: {'allowed': False, 'note': 'Cannot apply lime during growing season. Plan for next season after harvest.'},
            3: {'allowed': False, 'note': 'Cannot apply lime during growing season. Plan for next season after harvest.'},
            4: {'allowed': False, 'note': 'Cannot apply lime now. Apply after harvest for next season.'}
        },
        'sulfur': {
            1: {'allowed': True, 'note': 'Apply 2-3 months before planting. Water thoroughly after application.'},
            2: {'allowed': False, 'note': 'Cannot apply sulfur during growing season. Plan for next season.'},
            3: {'allowed': False, 'note': 'Cannot apply sulfur during growing season. Plan for next season.'},
            4: {'allowed': False, 'note': 'Cannot apply sulfur now. Apply after harvest for next season.'}
        },
        'fym': {
            1: {'allowed': True, 'note': 'Apply 2-3 weeks before planting. Incorporate into soil.'},
            2: {'allowed': False, 'note': 'Cannot apply FYM during growing season. Plan for next season.'},
            3: {'allowed': False, 'note': 'Cannot apply FYM during growing season. Plan for next season.'},
            4: {'allowed': False, 'note': 'Cannot apply FYM now. Apply after harvest for next season.'}
        }
    }
    
    # pH-based amendments (Lime/Sulfur)
    if 'pH' in deficiency:
        ph_status = deficiency['pH'].get('status', '')
        
        if ph < 5.0:
            lime_required = round((5.5 - ph) * 2000, 0)
            rule = stage_rules['lime'][growth_stage]
            
            if rule['allowed']:
                amendments.append({
                    'type': 'Agricultural Lime (CaCO3)',
                    'purpose': 'Correct soil acidity',
                    'issue': f'Soil too acidic (pH={ph}) - Nutrients are locked up',
                    'amount_kg_per_ha': lime_required,
                    'bags_50kg': math.ceil(lime_required / 50),
                    'cost_inr': math.ceil(lime_required / 50) * 250,
                    'application': rule['note'],
                    'benefit': 'Increases phosphorus availability by 30-40%. Improves nitrogen fixation.',
                    'note': 'Lime takes 3-6 months to react fully. Benefits last 2-3 seasons.',
                    'fertilizer_impact': 'Reduces DAP requirement by 30%, Urea by 15%',
                    'timing_allowed': True
                })
            else:
                amendments.append({
                    'type': 'Agricultural Lime (CaCO3) - PLAN FOR NEXT SEASON',
                    'purpose': 'Correct soil acidity',
                    'issue': f'Soil too acidic (pH={ph}) - Nutrients are locked up',
                    'amount_kg_per_ha': lime_required,
                    'bags_50kg': math.ceil(lime_required / 50),
                    'cost_inr': math.ceil(lime_required / 50) * 250,
                    'application': rule['note'],
                    'benefit': 'Increases phosphorus availability by 30-40%. Improves nitrogen fixation.',
                    'note': 'Lime takes 3-6 months to react fully. Benefits last 2-3 seasons.',
                    'fertilizer_impact': 'Reduces DAP requirement by 30%, Urea by 15%',
                    'timing_allowed': False,
                    'warning': f"Cannot apply lime at current growth stage. {rule['note']}"
                })
                
        elif ph > 7.5:
            sulfur_required = round((ph - 7.0) * 200, 0)
            rule = stage_rules['sulfur'][growth_stage]
            
            if rule['allowed']:
                amendments.append({
                    'type': 'Elemental Sulfur',
                    'purpose': 'Correct soil alkalinity',
                    'issue': f'Soil too alkaline (pH={ph}) - Micronutrients unavailable',
                    'amount_kg_per_ha': sulfur_required,
                    'bags_50kg': math.ceil(sulfur_required / 50),
                    'cost_inr': math.ceil(sulfur_required / 50) * 800,
                    'application': rule['note'],
                    'benefit': 'Improves availability of phosphorus, iron, zinc, and manganese.',
                    'note': 'Sulfur works slowly. Use gypsum for immediate effect but slower pH change.',
                    'fertilizer_impact': 'Improves micronutrient uptake',
                    'timing_allowed': True
                })
            else:
                amendments.append({
                    'type': 'Elemental Sulfur - PLAN FOR NEXT SEASON',
                    'purpose': 'Correct soil alkalinity',
                    'issue': f'Soil too alkaline (pH={ph}) - Micronutrients unavailable',
                    'amount_kg_per_ha': sulfur_required,
                    'bags_50kg': math.ceil(sulfur_required / 50),
                    'cost_inr': math.ceil(sulfur_required / 50) * 800,
                    'application': rule['note'],
                    'benefit': 'Improves availability of phosphorus, iron, zinc, and manganese.',
                    'note': 'Sulfur works slowly. Use gypsum for immediate effect but slower pH change.',
                    'fertilizer_impact': 'Improves micronutrient uptake',
                    'timing_allowed': False,
                    'warning': f"Cannot apply sulfur at current growth stage. {rule['note']}"
                })
    
    # FYM recommendation with availability logic
    rule = stage_rules['fym'][growth_stage]

    # Stage-specific application notes
    stage_notes = {
        1: 'Apply 2-3 weeks before planting. Incorporate into top 15cm soil.',
        2: 'Cannot apply during growing season. Plan to apply after harvest, before next planting.',
        3: 'Cannot apply during growing season. Plan to apply after harvest, before next planting.',
        4: 'Cannot apply now. Plan to apply after harvest, before next planting.'
    }
    application_text = stage_notes.get(growth_stage, rule['note'])

    ideal_fym = 5.0
    nursery_area = 0.1
    nursery_fym_needed = ideal_fym * nursery_area  # 0.5 tons
    abundant_fym = 10.0

    if fym_available >= abundant_fym:
        # Abundant FYM available (>10 tons)
        if rule['allowed']:
            amendments.append({
                'type': 'Farm Yard Manure (FYM) - ABUNDANT',
                'purpose': 'Improve soil health across all fields',
                'issue': f'You have {fym_available} tons FYM available (excellent supply)',
                'amount_kg_per_ha': 5000,
                'tons': 5,
                'cost_inr': 5000,
                'application': f'Apply 5 tons/ha to main field. Use remaining {fym_available - 5} tons for nursery and other crops.',
                'benefit': 'Abundant FYM allows comprehensive soil improvement across your entire farm.',
                'note': f'Main field: 5 tons. Nursery: 0.5 tons. Remaining: {fym_available - 5.5} tons for vegetables or neighboring fields.',
                'fertilizer_impact': 'Reduces Urea by 10%, DAP by 15%, MOP by 10%',
                'timing_allowed': True,
                'fym_status': 'abundant'
            })
        else:
            amendments.append({
                'type': 'Farm Yard Manure (FYM) - PLAN ABUNDANT APPLICATION',
                'purpose': 'Improve soil health across all fields',
                'issue': f'You have {fym_available} tons FYM available',
                'amount_kg_per_ha': 5000,
                'tons': 5,
                'cost_inr': 5000,
                'application': f'After harvest, apply 5 tons/ha to main field. Reserve remaining for nursery and other crops.',
                'benefit': 'Abundant FYM allows comprehensive soil improvement.',
                'note': f'Total: {fym_available} tons. Main field: 5 tons. Nursery: 0.5 tons.',
                'fertilizer_impact': 'Reduces fertilizer needs across all fields',
                'timing_allowed': False,
                'fym_status': 'abundant',
                'warning': f"Cannot apply FYM at current growth stage. {application_text}"
            })

    elif fym_available >= ideal_fym:
        # Sufficient FYM (5.0 to 9.9 tons)
        if rule['allowed']:
            amendments.append({
                'type': 'Farm Yard Manure (FYM) or Compost',
                'purpose': 'Improve soil health',
                'issue': f'You have {fym_available} tons FYM (sufficient for main field)',
                'amount_kg_per_ha': 5000,
                'tons': 5,
                'cost_inr': 5000,
                'application': application_text,
                'benefit': 'Provides slow-release NPK (approx: 25kg N, 5kg P, 12kg K). Improves water holding capacity and soil structure.',
                'note': f'Apply 5 tons/ha to main field. Remaining {fym_available - 5} tons can be used for nursery or saved.',
                'fertilizer_impact': 'Reduces Urea by 10%, DAP by 15%, MOP by 10%',
                'timing_allowed': True,
                'fym_status': 'sufficient'
            })
        else:
            amendments.append({
                'type': 'Farm Yard Manure (FYM) - PLAN FOR NEXT SEASON',
                'purpose': 'Improve soil health',
                'issue': f'You have {fym_available} tons FYM available',
                'amount_kg_per_ha': 5000,
                'tons': 5,
                'cost_inr': 5000,
                'application': application_text,
                'benefit': 'Provides slow-release NPK. Improves water holding capacity and soil structure.',
                'note': 'Benefits last 2-3 seasons.',
                'fertilizer_impact': 'Reduces Urea by 10%, DAP by 15%, MOP by 10%',
                'timing_allowed': False,
                'fym_status': 'sufficient',
                'warning': f"Cannot apply FYM at current growth stage. {application_text}"
            })

    elif fym_available >= nursery_fym_needed:
        # Limited FYM (0.5 to 4.9 tons)
        if rule['allowed']:
            amendments.append({
                'type': 'Farm Yard Manure (FYM) - NURSERY APPLICATION ONLY',
                'purpose': 'Concentrate limited FYM where it matters most',
                'issue': f'Only {fym_available} tons FYM available (insufficient for full field)',
                'amount_kg_per_ha': fym_available * 1000,
                'tons': fym_available,
                'cost_inr': round(fym_available * 1000),
                'application': f'Apply all {fym_available} tons to nursery area (1/10th hectare) before sowing seedlings.',
                'benefit': 'Concentrated FYM produces stronger, healthier seedlings that transplant better.',
                'note': f'Nursery requires only {nursery_fym_needed} tons. Your {fym_available} tons is sufficient for excellent nursery results.',
                'fertilizer_impact': 'Stronger seedlings establish faster and tolerate stress better.',
                'timing_allowed': True,
                'fym_status': 'nursery_only',
                'warning': 'Do NOT spread thinly across whole field - benefit would be negligible.'
            })
        else:
            amendments.append({
                'type': 'Farm Yard Manure (FYM) - PLAN NURSERY APPLICATION',
                'purpose': 'Concentrate limited FYM where it matters most',
                'issue': f'Only {fym_available} tons FYM available',
                'amount_kg_per_ha': fym_available * 1000,
                'tons': fym_available,
                'cost_inr': round(fym_available * 1000),
                'application': f'After harvest, plan to apply all {fym_available} tons to nursery area next season.',
                'benefit': 'Concentrated FYM produces stronger seedlings.',
                'note': f'Nursery requires only {nursery_fym_needed} tons.',
                'fertilizer_impact': 'Stronger seedlings establish faster.',
                'timing_allowed': False,
                'fym_status': 'nursery_only',
                'warning': f"Cannot apply FYM at current growth stage. {application_text}"
            })

    else:
        # Very limited or no FYM (<0.5 tons)
        if rule['allowed']:
            amendments.append({
                'type': 'Dhaincha (Sesbania) Green Manure - RECOMMENDED',
                'purpose': 'In-situ organic matter and nitrogen source',
                'issue': f'Only {fym_available} tons FYM available (insufficient even for nursery)',
                'amount_kg_per_ha': 40,
                'seeds_kg_per_ha': 40,
                'cost_inr': 800,
                'application': 'Sow Dhaincha seeds in mid-May to late June. Allow to grow for 45-60 days. Plow into soil before transplanting rice.',
                'benefit': 'Provides 80-100 kg nitrogen equivalent per hectare. Improves soil organic matter. Suppresses weeds naturally.',
                'note': 'Dhaincha is superior to limited FYM. One season can replace 50-60% of nitrogen fertilizer.',
                'fertilizer_impact': 'Reduces urea requirement by 50-60% for the rice crop.',
                'timing_allowed': True,
                'fym_status': 'insufficient',
                'warning': f'With only {fym_available} tons FYM, skip FYM entirely. Dhaincha provides far more benefit.'
            })
        else:
            amendments.append({
                'type': 'Dhaincha (Sesbania) Green Manure - PLAN FOR NEXT SEASON',
                'purpose': 'In-situ organic matter and nitrogen source',
                'issue': f'Only {fym_available} tons FYM available',
                'amount_kg_per_ha': 40,
                'seeds_kg_per_ha': 40,
                'cost_inr': 800,
                'application': 'Before next rice season: Sow Dhaincha in mid-May to late June, incorporate after 45-60 days.',
                'benefit': 'Provides 80-100 kg nitrogen equivalent per hectare.',
                'note': 'Plan this for your next rice crop. Dhaincha is low-cost and highly effective.',
                'fertilizer_impact': 'Reduces urea requirement by 50-60% for the next rice crop.',
                'timing_allowed': False,
                'fym_status': 'insufficient',
                'warning': f'Plan Dhaincha green manure for next season. It provides far more benefit than limited FYM.'
            })

    return amendments



# -----------------------------------------------------------------------------
# SECTION 5 - Fertilizer Adjustment Based on Amendments
# -----------------------------------------------------------------------------
def adjust_fertilizer_for_amendments(fertilizer_recs, amendments, ph):
    adjusted = {}
    for key, value in fertilizer_recs.items():
        if isinstance(value, dict):
            adjusted[key] = value.copy()
        else:
            adjusted[key] = value
    
    has_lime = any('Lime' in a.get('type', '') for a in amendments)
    has_fym = any('FYM' in a.get('type', '') or 'Compost' in a.get('type', '') for a in amendments)
    ph_needs_lime = ph < 5.5
    
    if has_lime and ph_needs_lime:
        if 'DAP' in adjusted and adjusted['DAP'].get('bags_50kg', 0) > 0:
            original_bags = adjusted['DAP']['bags_50kg']
            adjusted_bags = max(0, math.ceil(original_bags * 0.7))
            adjusted['DAP']['bags_50kg'] = adjusted_bags
            adjusted['DAP']['fertilizer_kg_per_ha'] = adjusted_bags * 50
            adjusted['DAP']['cost_inr'] = adjusted_bags * 1350
            adjusted['DAP']['adjustment_note'] = 'Reduced 30% - Lime improves P availability'
        
        if 'Urea' in adjusted and adjusted['Urea'].get('bags_50kg', 0) > 0:
            original_bags = adjusted['Urea']['bags_50kg']
            adjusted_bags = max(0, math.ceil(original_bags * 0.85))
            adjusted['Urea']['bags_50kg'] = adjusted_bags
            adjusted['Urea']['fertilizer_kg_per_ha'] = adjusted_bags * 50
            adjusted['Urea']['cost_inr'] = adjusted_bags * 266
            adjusted['Urea']['adjustment_note'] = 'Reduced 15% - Lime improves N availability'
    
    if has_fym:
        for fert, reduction, note in [
            ('Urea', 0.90, 'Reduced 10% - FYM provides slow-release N'),
            ('DAP', 0.85, 'Reduced 15% - FYM provides P'),
            ('MOP', 0.90, 'Reduced 10% - FYM provides K')
        ]:
            if fert in adjusted and adjusted[fert].get('bags_50kg', 0) > 0:
                original_bags = adjusted[fert]['bags_50kg']
                adjusted_bags = max(0, math.ceil(original_bags * reduction))
                adjusted[fert]['bags_50kg'] = adjusted_bags
                adjusted[fert]['fertilizer_kg_per_ha'] = adjusted_bags * 50
                price_map = {'Urea': 266, 'DAP': 1350, 'MOP': 1700}
                adjusted[fert]['cost_inr'] = adjusted_bags * price_map[fert]
                adjusted[fert]['adjustment_note'] = note
    
    adjusted['total_cost_inr'] = sum(
        adjusted.get(fert, {}).get('cost_inr', 0) 
        for fert in ['Urea', 'DAP', 'MOP']
    )
    
    return adjusted


# -----------------------------------------------------------------------------
# SECTION 6 - Fertilizer Recommendation
# -----------------------------------------------------------------------------
def fertilizer_recommendation(deficiency, growth_stage):
    
    prices = {
        'Urea': 266,
        'DAP': 1350,
        'MOP': 1700
    }
    
    recommendations = {}
    total_savings = 0
    
    stage_rules = {
        'Urea': {
            1: {'allowed': True, 'note': 'Apply as small basal dose only'},
            2: {'allowed': True, 'note': 'Main application window - split into 2-3 doses'},
            3: {'allowed': False, 'note': 'Not recommended - may delay maturity and increase disease risk'},
            4: {'allowed': False, 'note': 'Do not apply - too late for any benefit'}
        },
        'DAP': {
            1: {'allowed': True, 'note': 'Apply as basal dose before or at planting'},
            2: {'allowed': False, 'note': 'Not effective at this stage - should be applied at planting'},
            3: {'allowed': False, 'note': 'Not effective - phosphorus needed early for root development'},
            4: {'allowed': False, 'note': 'Do not apply - plan for next season'}
        },
        'MOP': {
            1: {'allowed': True, 'note': 'Apply as basal dose before or at planting'},
            2: {'allowed': True, 'note': 'Can be applied if deficiency is severe'},
            3: {'allowed': False, 'note': 'Not recommended - may affect grain quality'},
            4: {'allowed': False, 'note': 'Do not apply - too late for benefit'}
        }
    }
    
    def is_excess(nutrient):
        if nutrient in deficiency:
            data = deficiency[nutrient]
            severity = data.get('severity', '')
            has_excess = 'excess' in data and data['excess'] > 0
            return severity in ['excess_low', 'excess_high', 'toxic'] or has_excess
        return False
    
    # UREA
    if is_excess('Nitrogen'):
        excess_kg = deficiency['Nitrogen'].get('excess', 0)
        savings = excess_kg * 11.57
        total_savings += savings
        recommendations['Urea'] = {
            'nutrient': 'Nitrogen',
            'status': deficiency['Nitrogen']['status'],
            'deficit_kg': 0,
            'fertilizer_kg_per_ha': 0,
            'bags_50kg': 0,
            'cost_inr': 0,
            'saved_inr': round(savings, 0),
            'warning': 'DO NOT APPLY UREA - Nitrogen levels are already excessive.',
            'timing_note': None
        }
    else:
        n_deficit = deficiency['Nitrogen'].get('deficit', 0)
        rule = stage_rules['Urea'][growth_stage]
        
        if n_deficit > 0 and rule['allowed']:
            urea_kg = round(n_deficit / 0.46, 1)
            urea_bags = math.ceil(urea_kg / 50)
            recommendations['Urea'] = {
                'nutrient': 'Nitrogen',
                'status': deficiency['Nitrogen']['status'],
                'deficit_kg': n_deficit,
                'fertilizer_kg_per_ha': urea_kg,
                'bags_50kg': urea_bags,
                'cost_inr': urea_bags * prices['Urea'],
                'timing_note': rule['note']
            }
        elif n_deficit > 0 and not rule['allowed']:
            recommendations['Urea'] = {
                'nutrient': 'Nitrogen',
                'status': deficiency['Nitrogen']['status'],
                'deficit_kg': n_deficit,
                'fertilizer_kg_per_ha': 0,
                'bags_50kg': 0,
                'cost_inr': 0,
                'warning': f"Cannot apply urea at current growth stage. {rule['note']}",
                'timing_note': rule['note']
            }
        else:
            recommendations['Urea'] = {
                'nutrient': 'Nitrogen',
                'status': 'Optimal - No urea needed',
                'deficit_kg': 0,
                'fertilizer_kg_per_ha': 0,
                'bags_50kg': 0,
                'cost_inr': 0,
                'timing_note': None
            }
    
    # DAP
    if is_excess('Phosphorus'):
        excess_kg = deficiency['Phosphorus'].get('excess', 0)
        savings = excess_kg * 135.00
        total_savings += savings
        recommendations['DAP'] = {
            'nutrient': 'Phosphorus',
            'status': deficiency['Phosphorus']['status'],
            'deficit_kg': 0,
            'fertilizer_kg_per_ha': 0,
            'bags_50kg': 0,
            'cost_inr': 0,
            'saved_inr': round(savings, 0),
            'warning': 'DO NOT APPLY DAP - Phosphorus levels are already excessive.',
            'timing_note': None
        }
    else:
        p_deficit = deficiency['Phosphorus'].get('deficit', 0)
        rule = stage_rules['DAP'][growth_stage]
        
        if p_deficit > 0 and rule['allowed']:
            dap_kg = round(p_deficit / 0.46, 1)
            dap_bags = math.ceil(dap_kg / 50)
            recommendations['DAP'] = {
                'nutrient': 'Phosphorus',
                'status': deficiency['Phosphorus']['status'],
                'deficit_kg': p_deficit,
                'fertilizer_kg_per_ha': dap_kg,
                'bags_50kg': dap_bags,
                'cost_inr': dap_bags * prices['DAP'],
                'timing_note': rule['note']
            }
        elif p_deficit > 0 and not rule['allowed']:
            recommendations['DAP'] = {
                'nutrient': 'Phosphorus',
                'status': deficiency['Phosphorus']['status'],
                'deficit_kg': p_deficit,
                'fertilizer_kg_per_ha': 0,
                'bags_50kg': 0,
                'cost_inr': 0,
                'warning': f"Cannot apply DAP at current growth stage. {rule['note']}",
                'timing_note': rule['note']
            }
        else:
            recommendations['DAP'] = {
                'nutrient': 'Phosphorus',
                'status': 'Optimal - No DAP needed',
                'deficit_kg': 0,
                'fertilizer_kg_per_ha': 0,
                'bags_50kg': 0,
                'cost_inr': 0,
                'timing_note': None
            }
    
    # MOP
    if is_excess('Potassium'):
        excess_kg = deficiency['Potassium'].get('excess', 0)
        savings = excess_kg * 68.00
        total_savings += savings
        recommendations['MOP'] = {
            'nutrient': 'Potassium',
            'status': deficiency['Potassium']['status'],
            'deficit_kg': 0,
            'fertilizer_kg_per_ha': 0,
            'bags_50kg': 0,
            'cost_inr': 0,
            'saved_inr': round(savings, 0),
            'warning': 'DO NOT APPLY MOP - Potassium levels are already excessive.',
            'timing_note': None
        }
    else:
        k_deficit = deficiency['Potassium'].get('deficit', 0)
        rule = stage_rules['MOP'][growth_stage]
        
        if k_deficit > 0 and rule['allowed']:
            mop_kg = round(k_deficit / 0.60, 1)
            mop_bags = math.ceil(mop_kg / 50)
            recommendations['MOP'] = {
                'nutrient': 'Potassium',
                'status': deficiency['Potassium']['status'],
                'deficit_kg': k_deficit,
                'fertilizer_kg_per_ha': mop_kg,
                'bags_50kg': mop_bags,
                'cost_inr': mop_bags * prices['MOP'],
                'timing_note': rule['note']
            }
        elif k_deficit > 0 and not rule['allowed']:
            recommendations['MOP'] = {
                'nutrient': 'Potassium',
                'status': deficiency['Potassium']['status'],
                'deficit_kg': k_deficit,
                'fertilizer_kg_per_ha': 0,
                'bags_50kg': 0,
                'cost_inr': 0,
                'warning': f"Cannot apply MOP at current growth stage. {rule['note']}",
                'timing_note': rule['note']
            }
        else:
            recommendations['MOP'] = {
                'nutrient': 'Potassium',
                'status': 'Optimal - No MOP needed',
                'deficit_kg': 0,
                'fertilizer_kg_per_ha': 0,
                'bags_50kg': 0,
                'cost_inr': 0,
                'timing_note': None
            }
    
    total_cost = sum(r.get('cost_inr', 0) for r in recommendations.values() if isinstance(r, dict))
    recommendations['total_cost_inr'] = total_cost
    recommendations['total_saved_inr'] = round(total_savings, 0)
    
    excess_exists = any(is_excess(n) for n in ['Nitrogen', 'Phosphorus', 'Potassium'])
    if excess_exists:
        recommendations['_global_warning'] = {
            'message': 'SOIL HAS EXCESS NUTRIENTS',
            'advice': 'DO NOT apply any fertilizer this season. Focus on:',
            'actions': [
                'Apply more irrigation water to leach excess salts',
                'Consider growing a cover crop to utilize excess nutrients',
                'Test soil again next season before fertilizing',
                'Reduce fertilizer application rates by 50-70% in the next season'
            ],
            'total_savings': round(total_savings, 0)
        }
    
    return recommendations


# -----------------------------------------------------------------------------
# SECTION 7 - Irrigation Advisory
# -----------------------------------------------------------------------------
def irrigation_advisory(rainfall, growth_stage):
    
    stage_info = {
        1: {'name': 'Seedling', 'ideal_depth': '8-10 cm', 'monthly_need': 160,
            'note': 'Seedling stage needs the most water. Keep field well flooded.'},
        2: {'name': 'Tillering', 'ideal_depth': '5-10 cm', 'monthly_need': 140,
            'note': 'Active growth stage. Do not let field dry out.'},
        3: {'name': 'Flowering', 'ideal_depth': '5-8 cm', 'monthly_need': 120,
            'note': 'Most critical stage. Water stress reduces yield significantly.'},
        4: {'name': 'Maturity', 'ideal_depth': '2-5 cm', 'monthly_need': 80,
            'note': 'Gradually reduce water. Drain completely 2 weeks before harvest.'}
    }
    
    if growth_stage not in stage_info:
        return {'error': 'Invalid growth stage. Enter 1, 2, 3, or 4.'}
    
    info = stage_info[growth_stage]
    deficit = info['monthly_need'] - rainfall
    
    if deficit <= 0:
        if rainfall > 400:
            urgency = 'WATERLOGGING RISK'
            urgency_color = 'red'
            advice = f"EXCESSIVE RAINFALL ({rainfall}mm) - Create drainage channels immediately."
        else:
            urgency = 'LOW'
            urgency_color = 'green'
            advice = f"Rainfall sufficient. Maintain {info['ideal_depth']} standing water."
    elif deficit <= 40:
        urgency = 'MEDIUM'
        urgency_color = 'yellow'
        advice = f"Flood field once this month. Maintain {info['ideal_depth']} water."
    elif deficit <= 80:
        urgency = 'MEDIUM'
        urgency_color = 'orange'
        advice = f"Flood field twice this month. Keep {info['ideal_depth']} water."
    else:
        urgency = 'HIGH'
        urgency_color = 'red'
        advice = f"LOW RAINFALL ({rainfall}mm). Flood immediately. Maintain {info['ideal_depth']} water."
    
    return {
        'growth_stage': info['name'],
        'ideal_depth': info['ideal_depth'],
        'urgency': urgency,
        'urgency_color': urgency_color,
        'advice': advice,
        'stage_note': info['note'],
        'rainfall_mm': rainfall,
        'deficit_mm': max(0, deficit)
    }


# -----------------------------------------------------------------------------
# SECTION 8 - Complete Advisory Function (Main Entry Point)
# -----------------------------------------------------------------------------
def get_complete_advisory(nitrogen, phosphorus, potassium,
                           temperature, humidity, ph,
                           rainfall, growth_stage, fym_available=0):
    
    fertility, deficiency, fertility_color, fertility_score = assign_fertility_with_deficiency(
        nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall
    )
    
    disease_risk = predict_disease_risk(temperature, humidity, growth_stage, rainfall,
                                         nitrogen, phosphorus, potassium)
    
    yield_impact = estimate_yield_impact(deficiency, disease_risk, temperature, ph, rainfall)
    
    amendments = soil_amendment_recommendations(ph, deficiency, growth_stage, fym_available)
    
    fertilizer = fertilizer_recommendation(deficiency, growth_stage)
    
    fym_is_sufficient = any(a.get('fym_status') == 'sufficient' for a in amendments if 'FYM' in a.get('type', ''))
    if fym_is_sufficient:
        fertilizer = adjust_fertilizer_for_amendments(fertilizer, amendments, ph)
    
    irrigation = irrigation_advisory(rainfall, growth_stage)
    
    price_per_quintal = 2300
    total_fertilizer_cost = fertilizer.get('total_cost_inr', 0)
    total_fertilizer_savings = fertilizer.get('total_saved_inr', 0)
    total_amendment_cost = sum(a.get('cost_inr', 0) for a in amendments if a.get('timing_allowed', True))
    total_input_cost = total_fertilizer_cost + total_amendment_cost
    
    expected_revenue = yield_impact['expected_yield_quintals'] * price_per_quintal
    potential_revenue = yield_impact['potential_yield_quintals'] * price_per_quintal
    
    yield_impact['economic_loss_inr'] = round((yield_impact['potential_yield_quintals'] - yield_impact['expected_yield_quintals']) * price_per_quintal, 0)
    yield_impact['revenue_at_risk'] = round(yield_impact['potential_yield_quintals'] * price_per_quintal, 0)
    
    has_amendments = len(amendments) > 0
    multi_season_note = None
    if has_amendments:
        multi_season_note = 'Amendment benefits last 2-3 seasons. Per-season cost is approximately 30-50% of shown amount.'
    
        # Add calculation formulas for transparency
    formulas = {
        'fertility_score': {
            'formula': 'N(0-3) + P(0-3) + K(0-3) + pH(0-2) + Rainfall(0-2) + Temp(0-1) + Humidity(0-1)',
            'your_score': f"{fertility_score}/15"
        },
        'yield_loss': {
            'formula': 'Sum of: N loss% + P loss% + K loss% + pH stress% + Disease risk% + Water stress%',
            'your_loss': f"{yield_impact['loss_percentage']}%"
        },
        'expected_yield': {
            'formula': f"25 qt/ha × (1 - {yield_impact['loss_percentage']}/100)",
            'result': f"{yield_impact['expected_yield_quintals']} quintals/ha"
        },
        'fertilizer_urea': {
            'formula': 'N deficit (kg) ÷ 0.46 (urea N content) ÷ 50 = bags',
            'note': 'Urea contains 46% N. Each 50kg bag provides 23kg N.'
        },
        'fertilizer_dap': {
            'formula': 'P deficit (kg) ÷ 0.46 (DAP P2O5) ÷ 50 = bags',
            'note': 'DAP contains 46% P2O5 = 20% elemental P. 50kg bag provides 10kg P.'
        },
        'fertilizer_mop': {
            'formula': 'K deficit (kg) ÷ 0.60 (MOP K2O) ÷ 50 = bags',
            'note': 'MOP contains 60% K2O = 50% elemental K. 50kg bag provides 25kg K.'
        },
        'lime': {
            'formula': '(5.5 - pH) × 2000 = kg lime/ha',
            'note': 'Target pH is 5.5-7.0 for optimal rice growth.'
        },
        'sulfur': {
            'formula': '(pH - 7.0) × 200 = kg sulfur/ha',
            'note': 'For alkaline soils above pH 7.5.'
        },
        'economic_loss': {
            'formula': f"(25 - {yield_impact['expected_yield_quintals']}) qt/ha × Rs. 2,300/qt",
            'result': f"Rs. {yield_impact['economic_loss_inr']}"
        },
        'revenue_potential': {
            'formula': f"25 qt/ha × Rs. 2,300/qt",
            'result': f"Rs. {yield_impact['revenue_at_risk']}"
        },
        'revenue_expected': {
            'formula': f"{yield_impact['expected_yield_quintals']} qt/ha × Rs. 2,300/qt",
            'result': f"Rs. {expected_revenue}"
        },
        'input_cost': {
            'formula': 'Fertilizer cost + Amendment cost',
            'fertilizer': f"Rs. {total_fertilizer_cost}",
            'amendments': f"Rs. {total_amendment_cost}",
            'total': f"Rs. {total_input_cost}"
        },
        'assumptions': {
            'rice_price': 'Rs. 2,300/quintal (MSP 2024-25)',
            'base_yield': '25 quintals/ha (Bihar average 2024-25)',
            'npk_standards': 'N=120, P=60, K=60 kg/ha (Bihar Dept of Agriculture)'
        }
    }
    
    return {
        'fertility': fertility,
        'fertility_color': fertility_color,
        'fertility_score': fertility_score,
        'deficiency': deficiency,
        'disease_risk': disease_risk,
        'yield_impact': yield_impact,
        'soil_amendments': amendments,
        'fertilizer': fertilizer,
        'irrigation': irrigation,
        'economics': {
            'fertilizer_cost_inr': total_fertilizer_cost,
            'fertilizer_savings_inr': total_fertilizer_savings,
            'amendment_cost_inr': total_amendment_cost,
            'total_input_cost_inr': total_input_cost,
            'expected_revenue_inr': round(expected_revenue, 0),
            'potential_revenue_inr': round(potential_revenue, 0),
            'revenue_loss_inr': round(yield_impact['economic_loss_inr'], 0),
            'net_projection': round(expected_revenue - total_input_cost, 0),
            'multi_season_note': multi_season_note
        },
        'formulas': formulas  # NEW
    }

   

