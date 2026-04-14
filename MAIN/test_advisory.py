# ============================================================
# test_advisory.py
# Test script for advisory_engine.py
# Run: python test_advisory.py
# ============================================================

from advisory_engine import (
    assign_fertility_with_deficiency,
    predict_disease_risk,
    estimate_yield_impact,
    soil_amendment_recommendations,
    fertilizer_recommendation,
    irrigation_advisory,
    get_complete_advisory
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """Print a formatted subsection header"""
    print("\n" + "-" * 50)
    print(f"  {title}")
    print("-" * 50)


def test_fertility_scoring():
    """Test fertility scoring with different NPK scenarios"""
    print_section("TEST 1: FERTILITY SCORING (NPK SCENARIOS)")
    
    # Test scenarios covering: Optimal, Deficient, Excess, Toxic
    test_cases = [
        {
            'name': 'Optimal NPK',
            'n': 120, 'p': 60, 'k': 60,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'Severe N Deficiency',
            'n': 30, 'p': 60, 'k': 60,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'Toxic N Excess',
            'n': 250, 'p': 60, 'k': 60,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'Toxic K Excess',
            'n': 120, 'p': 60, 'k': 150,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'Multiple Deficiencies',
            'n': 50, 'p': 25, 'k': 35,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'All Toxic Excess (Should Save Money)',
            'n': 300, 'p': 200, 'k': 250,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        }
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        fertility, deficiency, color, score = assign_fertility_with_deficiency(
            case['n'], case['p'], case['k'],
            case['temp'], case['humidity'], case['ph'], case['rainfall']
        )
        
        print(f"  Fertility: {fertility} (Score: {score}/15, Color: {color})")
        
        for nutrient in ['Nitrogen', 'Phosphorus', 'Potassium']:
            if nutrient in deficiency:
                data = deficiency[nutrient]
                status = data.get('status', 'N/A')
                if 'deficit' in data and data['deficit'] > 0:
                    print(f"    {nutrient}: {status} (Deficit: {data['deficit']} kg/ha)")
                elif 'excess' in data and data['excess'] > 0:
                    print(f"    {nutrient}: {status} (Excess: {data['excess']} kg/ha)")
                else:
                    print(f"    {nutrient}: {status}")
        
        if '_toxicity_warning' in deficiency:
            tw = deficiency['_toxicity_warning']
            print(f"\n  [TOXICITY WARNING] {tw['message']}")
            print(f"    Wasted fertilizer cost: Rs. {tw['wasted_cost']}")


def test_disease_risk():
    """Test disease risk detection with different environmental conditions"""
    print_section("TEST 2: DISEASE RISK DETECTION")
    
    test_cases = [
        {
            'name': 'High Blast Risk',
            'temp': 27, 'humidity': 92, 'growth_stage': 2, 'rainfall': 100
        },
        {
            'name': 'High Sheath Blight Risk',
            'temp': 30, 'humidity': 88, 'growth_stage': 3, 'rainfall': 100
        },
        {
            'name': 'Bacterial Leaf Blight Risk',
            'temp': 30, 'humidity': 85, 'growth_stage': 2, 'rainfall': 200
        },
        {
            'name': 'False Smut Risk (Flowering Stage)',
            'temp': 28, 'humidity': 90, 'growth_stage': 3, 'rainfall': 100
        },
        {
            'name': 'Low Disease Risk (Dry Conditions)',
            'temp': 30, 'humidity': 50, 'growth_stage': 2, 'rainfall': 50
        },
        {
            'name': 'Heat Stress + High Humidity',
            'temp': 42, 'humidity': 90, 'growth_stage': 2, 'rainfall': 50
        }
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        result = predict_disease_risk(
            case['temp'], case['humidity'], 
            case['growth_stage'], case['rainfall']
        )
        
        print(f"  Overall Risk: {result['overall_risk']}")
        print(f"  Advisory: {result['advisory']}")
        
        if result['diseases']:
            print("  Detected Diseases:")
            for d in result['diseases']:
                print(f"    - {d['name']}: {d['risk']} Risk")
                print(f"      Management: {d['management'][:60]}...")
        else:
            print("  No specific diseases detected.")


def test_fertilizer_recommendations():
    """Test fertilizer recommendations including excess handling"""
    print_section("TEST 3: FERTILIZER RECOMMENDATIONS")
    
    test_cases = [
        {
            'name': 'Normal Deficiencies',
            'n': 80, 'p': 40, 'k': 45,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'Excess Potassium (Should NOT recommend MOP)',
            'n': 80, 'p': 40, 'k': 130,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'All Nutrients Excess (Should recommend ZERO fertilizer)',
            'n': 250, 'p': 150, 'k': 140,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        },
        {
            'name': 'Optimal NPK (Should recommend ZERO fertilizer)',
            'n': 120, 'p': 60, 'k': 60,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200
        }
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        fertility, deficiency, color, score = assign_fertility_with_deficiency(
            case['n'], case['p'], case['k'],
            case['temp'], case['humidity'], case['ph'], case['rainfall']
        )
        
        fertilizer = fertilizer_recommendation(deficiency)
        
        print(f"  Fertilizer Recommendations:")
        for fert_name in ['Urea', 'DAP', 'MOP']:
            if fert_name in fertilizer:
                f = fertilizer[fert_name]
                if f.get('bags_50kg', 0) > 0:
                    print(f"    {fert_name}: {f['bags_50kg']} bags (Rs. {f['cost_inr']})")
                    if 'warning' in f:
                        print(f"      WARNING: {f['warning']}")
                else:
                    status = f.get('status', 'Not needed')
                    print(f"    {fert_name}: {status}")
                    if 'saved_inr' in f and f['saved_inr'] > 0:
                        print(f"      Savings: Rs. {f['saved_inr']}")
        
        print(f"\n  Total Fertilizer Cost: Rs. {fertilizer.get('total_cost_inr', 0)}")
        print(f"  Total Savings (from not over-applying): Rs. {fertilizer.get('total_saved_inr', 0)}")
        
        if '_global_warning' in fertilizer:
            gw = fertilizer['_global_warning']
            print(f"\n  [GLOBAL WARNING] {gw['message']}")
            print(f"    {gw['advice']}")
            for action in gw['actions']:
                print(f"      - {action}")


def test_irrigation_advisory():
    """Test irrigation recommendations across growth stages"""
    print_section("TEST 4: IRRIGATION ADVISORY")
    
    test_cases = [
        {'name': 'Seedling - Adequate Rain', 'rainfall': 180, 'stage': 1},
        {'name': 'Seedling - Drought', 'rainfall': 30, 'stage': 1},
        {'name': 'Tillering - Moderate Deficit', 'rainfall': 100, 'stage': 2},
        {'name': 'Flowering - Severe Deficit', 'rainfall': 20, 'stage': 3},
        {'name': 'Maturity - Waterlogging', 'rainfall': 450, 'stage': 4},
        {'name': 'Flowering - Optimal', 'rainfall': 140, 'stage': 3}
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        result = irrigation_advisory(case['rainfall'], case['stage'])
        
        if 'error' in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Growth Stage: {result['growth_stage']}")
            print(f"  Rainfall: {result['rainfall_mm']} mm")
            print(f"  Water Deficit: {result['deficit_mm']} mm")
            print(f"  Urgency: {result['urgency']} ({result['urgency_color']})")
            print(f"  Ideal Depth: {result['ideal_depth']}")
            print(f"  Advice: {result['advice']}")
            print(f"  Note: {result['stage_note']}")


def test_soil_amendments():
    """Test soil amendment recommendations for pH issues"""
    print_section("TEST 5: SOIL AMENDMENTS")
    
    test_cases = [
        {'name': 'Acidic Soil', 'ph': 4.2},
        {'name': 'Alkaline Soil', 'ph': 8.2},
        {'name': 'Optimal pH', 'ph': 6.5},
        {'name': 'Slightly Acidic', 'ph': 5.2}
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        # Create minimal deficiency dict with just pH
        deficiency = {}
        if case['ph'] < 5.0:
            deficiency['pH'] = {'status': 'Critical - Soil Amendment Needed', 'severity': 'critical'}
        elif case['ph'] > 7.5:
            deficiency['pH'] = {'status': 'Critical - Soil Amendment Needed', 'severity': 'critical'}
        elif 5.0 <= case['ph'] <= 7.5:
            deficiency['pH'] = {'status': 'Optimal', 'severity': 'optimal'}
        
        amendments = soil_amendment_recommendations(case['ph'], deficiency)
        
        print(f"  Soil pH: {case['ph']}")
        print(f"  Recommendations:")
        for amd in amendments:
            print(f"    - {amd['type']}")
            print(f"      Amount: {amd['amount_kg_per_ha']} kg/ha")
            print(f"      Cost: Rs. {amd['cost_inr']}")
            if 'note' in amd:
                print(f"      Note: {amd['note']}")


def test_yield_impact():
    """Test yield impact calculations"""
    print_section("TEST 6: YIELD IMPACT ESTIMATION")
    
    test_cases = [
        {
            'name': 'Optimal Conditions',
            'n': 120, 'p': 60, 'k': 60,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200,
            'stage': 2
        },
        {
            'name': 'Multiple Stress Factors',
            'n': 40, 'p': 25, 'k': 35,
            'temp': 42, 'humidity': 92, 'ph': 4.5, 'rainfall': 30,
            'stage': 3
        },
        {
            'name': 'Nutrient Toxicity',
            'n': 300, 'p': 200, 'k': 250,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200,
            'stage': 2
        }
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        fertility, deficiency, color, score = assign_fertility_with_deficiency(
            case['n'], case['p'], case['k'],
            case['temp'], case['humidity'], case['ph'], case['rainfall']
        )
        
        disease_risk = predict_disease_risk(
            case['temp'], case['humidity'], case['stage'], case['rainfall']
        )
        
        yield_impact = estimate_yield_impact(
            deficiency, disease_risk, case['temp'], case['ph'], case['rainfall']
        )
        
        print(f"  Potential Yield: {yield_impact['potential_yield_tons']} tons/ha")
        print(f"  Expected Yield: {yield_impact['expected_yield_tons']} tons/ha")
        print(f"  Loss Percentage: {yield_impact['loss_percentage']}%")
        print(f"  Economic Loss: Rs. {yield_impact['economic_loss_inr']}")
        print(f"  Loss Factors:")
        for factor in yield_impact['loss_factors']:
            print(f"    - {factor}")


def test_complete_advisory():
    """Test the main get_complete_advisory function"""
    print_section("TEST 7: COMPLETE ADVISORY (MAIN FUNCTION)")
    
    test_cases = [
        {
            'name': 'Healthy Field - Optimal Conditions',
            'n': 120, 'p': 60, 'k': 60,
            'temp': 28, 'humidity': 65, 'ph': 6.5, 'rainfall': 200,
            'stage': 2
        },
        {
            'name': 'Stressed Field - Multiple Issues',
            'n': 50, 'p': 30, 'k': 40,
            'temp': 35, 'humidity': 88, 'ph': 5.8, 'rainfall': 80,
            'stage': 3
        },
        {
            'name': 'Toxic Field - Excess Nutrients',
            'n': 280, 'p': 180, 'k': 200,
            'temp': 30, 'humidity': 70, 'ph': 6.8, 'rainfall': 150,
            'stage': 2
        }
    ]
    
    for case in test_cases:
        print_subsection(case['name'])
        
        result = get_complete_advisory(
            case['n'], case['p'], case['k'],
            case['temp'], case['humidity'], case['ph'],
            case['rainfall'], case['stage']
        )
        
        print(f"  Fertility: {result['fertility']} (Score: {result['fertility_score']}/15)")
        print(f"  Disease Risk: {result['disease_risk']['overall_risk']}")
        print(f"  Expected Yield: {result['yield_impact']['expected_yield_tons']} tons/ha")
        print(f"  Yield Loss: {result['yield_impact']['loss_percentage']}%")
        
        print(f"\n  Fertilizer Summary:")
        print(f"    Total Cost: Rs. {result['economics']['fertilizer_cost_inr']}")
        print(f"    Total Savings: Rs. {result['economics']['fertilizer_savings_inr']}")
        
        print(f"\n  Economics:")
        print(f"    Expected Revenue: Rs. {result['economics']['expected_revenue_inr']}")
        print(f"    Revenue Loss: Rs. {result['economics']['revenue_loss_inr']}")
        print(f"    Net Projection: Rs. {result['economics']['net_projection']}")
        
        print(f"\n  Irrigation: {result['irrigation']['advice']}")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "=" * 70)
    print("  ADVISORY ENGINE TEST SUITE")
    print("  Bihar Rice Crop Decision Support System")
    print("=" * 70)
    
    test_fertility_scoring()
    test_disease_risk()
    test_fertilizer_recommendations()
    test_irrigation_advisory()
    test_soil_amendments()
    test_yield_impact()
    test_complete_advisory()
    
    print("\n" + "=" * 70)
    print("  ALL TESTS COMPLETED")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    run_all_tests()