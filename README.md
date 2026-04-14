<h1>Agricultural Decision Support System</h1>



<p>A hybrid machine learning and rule-based advisory system for rice farmers in Bihar, India.</p>



<h2>Overview</h2>



<p>This system provides data-driven recommendations for soil fertility management and nutrient deficiency detection in rice crops.</p>



<h2>Features</h2>



<ul>

&#x20; <li><b>Soil Fertility Analysis</b> - XGBoost model with 98.7% accuracy</li>

&#x20; <li><b>Leaf Deficiency Detection</b> - KNN model with 81% accuracy</li>

&#x20; <li><b>Fertilizer Recommendations</b> - Precise NPK quantities</li>

&#x20; <li><b>Disease Risk Assessment</b> - Weather-based predictions</li>

&#x20; <li><b>Economic Impact</b> - Revenue and loss calculations</li>

</ul>



<h2>Tech Stack</h2>



<ul>

&#x20; <li><b>Backend:</b> Flask (Python)</li>

&#x20; <li><b>ML Models:</b> XGBoost, K-Nearest Neighbors</li>

&#x20; <li><b>Image Processing:</b> OpenCV</li>

&#x20; <li><b>Frontend:</b> HTML, CSS, JavaScript</li>

</ul>



<h2>Installation</h2>



<ol>

&#x20; <li>Clone the repository</li>

&#x20; <li>Create virtual environment: <code>python -m venv venv</code></li>

&#x20; <li>Activate: <code>venv\\Scripts\\activate</code> (Windows)</li>

&#x20; <li>Install: <code>pip install -r requirements.txt</code></li>

&#x20; <li>Run: <code>python app.py</code></li>

</ol>



<h2>Usage</h2>



<p><b>Soil Analysis:</b> Enter NPK values and growth stage at <code>/</code></p>

<p><b>Leaf Diagnosis:</b> Upload leaf image at <code>/leaf</code></p>



<h2>Model Performance</h2>



<table border="1" cellpadding="5">

&#x20; <tr>

&#x20;   <th>Model</th>

&#x20;   <th>Task</th>

&#x20;   <th>Accuracy</th>

&#x20; </tr>

&#x20; <tr>

&#x20;   <td>XGBoost</td>

&#x20;   <td>Soil Fertility</td>

&#x20;   <td>98.7%</td>

&#x20; </tr>

&#x20; <tr>

&#x20;   <td>KNN</td>

&#x20;   <td>Leaf Deficiency</td>

&#x20;   <td>81.0%</td>

&#x20; </tr>

</table>



<h2>Author</h2>



<p>Abdul<br>

Integral University, Lucknow<br>

BCA Final Year Project 2025-2026</p>



<hr>

<p><i>Submitted in partial fulfillment of BCA degree requirements.</i></p>

