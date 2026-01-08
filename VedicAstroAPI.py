from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
from vedicastro import VedicAstro, horary_chart, utils

app = FastAPI()

class ChartInput(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    utc: str
    latitude: float
    longitude: float
    ayanamsa: str = "Lahiri"
    house_system: str = "Equal"
    return_style: Optional[str] = None

class HoraryChartInput(BaseModel):
    horary_number: int
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    utc: str
    latitude: float
    longitude: float
    ayanamsa: str = "Krishnamurti"
    house_system: str = "Placidus"
    return_style: Optional[str] = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to VedicAstro FastAPI Service!",
            "info": "Visit http://127.0.0.1:8088/docs to test the API functions"}

@app.get("/chart", response_class=HTMLResponse)
async def get_chart_page():
    """Serves the horoscope chart input page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vedic Astrology Chart Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
            font-size: 0.9em;
        }
        
        .form-group input,
        .form-group select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .fixed-values {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }
        
        .fixed-values span {
            font-weight: 600;
            color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
            max-width: 300px;
            margin: 0 auto;
            display: block;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2em;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .results {
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .highlighted-house {
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%) !important;
            border: 3px solid #e17055 !important;
            box-shadow: 0 5px 15px rgba(225, 112, 85, 0.3) !important;
        }
        
        .table-container {
            overflow-x: auto;
            margin-bottom: 30px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tbody tr:hover {
            background: #f8f9fa;
        }
        
        tbody tr:last-child td {
            border-bottom: none;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-retro {
            background: #ff6b6b;
            color: white;
        }
        
        .badge-direct {
            background: #51cf66;
            color: white;
        }
        
        .house-special {
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 5px solid #e17055;
        }
        
        .house-special h3 {
            color: #e17055;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .house-special .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .info-item {
            background: white;
            padding: 12px;
            border-radius: 6px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .info-item strong {
            color: #667eea;
            display: block;
            margin-bottom: 5px;
        }
        
        .error {
            background: #ff6b6b;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        
        .error.show {
            display: block;
        }
        
        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            table {
                font-size: 0.9em;
            }
            
            th, td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 Vedic Astrology Chart Generator</h1>
            <p>Generate detailed horoscope charts with planetary and house positions</p>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: #333;">Chart Input Parameters</h2>
            
            <div class="fixed-values">
                <div><strong>Ayanamsa:</strong> <span>Krishnamurti</span></div>
                <div><strong>House System:</strong> <span>Placidus</span></div>
            </div>
            
            <form id="chartForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="year">Year</label>
                        <input type="number" id="year" name="year" value="1990" required min="1900" max="2100">
                    </div>
                    
                    <div class="form-group">
                        <label for="month">Month</label>
                        <input type="number" id="month" name="month" value="8" required min="1" max="12">
                    </div>
                    
                    <div class="form-group">
                        <label for="day">Day</label>
                        <input type="number" id="day" name="day" value="10" required min="1" max="31">
                    </div>
                    
                    <div class="form-group">
                        <label for="hour">Hour (0-23)</label>
                        <input type="number" id="hour" name="hour" value="12" required min="0" max="23">
                    </div>
                    
                    <div class="form-group">
                        <label for="minute">Minute</label>
                        <input type="number" id="minute" name="minute" value="0" required min="0" max="59">
                    </div>
                    
                    <div class="form-group">
                        <label for="second">Second</label>
                        <input type="number" id="second" name="second" value="0" required min="0" max="59">
                    </div>
                    
                    <div class="form-group">
                        <label for="utc">Timezone</label>
                        <input type="text" id="utc" name="utc" value="Asia/Kathmandu" required 
                               placeholder="e.g., Asia/Kathmandu or +5:45">
                    </div>
                    
                    <div class="form-group">
                        <label for="latitude">Latitude</label>
                        <input type="number" id="latitude" name="latitude" value="28.2323" required 
                               step="0.0001" min="-90" max="90">
                    </div>
                    
                    <div class="form-group">
                        <label for="longitude">Longitude</label>
                        <input type="number" id="longitude" name="longitude" value="83.923" required 
                               step="0.0001" min="-180" max="180">
                    </div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">Generate Chart</button>
            </form>
            
            <div class="error" id="errorMsg"></div>
            
            <div class="loading" id="loading">
                <p>🔄 Generating chart data... Please wait...</p>
            </div>
        </div>
        
        <div class="results" id="results">
            <div class="card">
                <h2 class="section-title">🏠 Highlighted Houses (1st, 6th, 11th)</h2>
                <div id="highlightedHouses"></div>
            </div>
            
            <div class="card">
                <h2 class="section-title">🪐 Planetary Positions</h2>
                <div class="table-container">
                    <table id="planetsTable">
                        <thead>
                            <tr>
                                <th>Object</th>
                                <th>Rasi</th>
                                <th>Retrograde</th>
                                <th>Longitude (Dec)</th>
                                <th>Sign Longitude</th>
                                <th>Nakshatra</th>
                                <th>Rasi Lord</th>
                                <th>Nakshatra Lord</th>
                                <th>Sub Lord</th>
                                <th>House</th>
                            </tr>
                        </thead>
                        <tbody id="planetsBody"></tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <h2 class="section-title">🏛️ House Positions</h2>
                <div class="table-container">
                    <table id="housesTable">
                        <thead>
                            <tr>
                                <th>House</th>
                                <th>Rasi</th>
                                <th>Longitude (Dec)</th>
                                <th>Sign Longitude</th>
                                <th>Deg Size</th>
                                <th>Nakshatra</th>
                                <th>Rasi Lord</th>
                                <th>Nakshatra Lord</th>
                                <th>Sub Lord</th>
                            </tr>
                        </thead>
                        <tbody id="housesBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('chartForm');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const errorMsg = document.getElementById('errorMsg');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Reset UI
            errorMsg.classList.remove('show');
            results.classList.remove('show');
            loading.classList.add('show');
            submitBtn.disabled = true;
            
            // Get form data
            const formData = {
                year: parseInt(document.getElementById('year').value),
                month: parseInt(document.getElementById('month').value),
                day: parseInt(document.getElementById('day').value),
                hour: parseInt(document.getElementById('hour').value),
                minute: parseInt(document.getElementById('minute').value),
                second: parseInt(document.getElementById('second').value),
                utc: document.getElementById('utc').value,
                latitude: parseFloat(document.getElementById('latitude').value),
                longitude: parseFloat(document.getElementById('longitude').value),
                ayanamsa: 'Krishnamurti',
                house_system: 'Placidus',
                return_style: 'string'
            };
            
            try {
                const response = await fetch('/get_all_horoscope_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to generate chart');
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                errorMsg.textContent = 'Error: ' + error.message;
                errorMsg.classList.add('show');
            } finally {
                loading.classList.remove('show');
                submitBtn.disabled = false;
            }
        });
        
        function displayResults(data) {
            // Display highlighted houses
            displayHighlightedHouses(data.houses_data);
            
            // Display planets
            displayPlanets(data.planets_data);
            
            // Display houses
            displayHouses(data.houses_data);
            
            // Show results
            results.classList.add('show');
            results.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        function displayHighlightedHouses(housesData) {
            const highlightedHouses = [1, 6, 11];
            const container = document.getElementById('highlightedHouses');
            container.innerHTML = '';
            
            highlightedHouses.forEach(houseNr => {
                const house = housesData.find(h => h.HouseNr === houseNr);
                if (house) {
                    const houseDiv = document.createElement('div');
                    houseDiv.className = 'house-special';
                    houseDiv.innerHTML = `
                        <h3>House ${houseNr} (${house.Object})</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <strong>Rasi:</strong> ${house.Rasi}
                            </div>
                            <div class="info-item">
                                <strong>Longitude:</strong> ${house.LonDecDeg.toFixed(3)}°
                            </div>
                            <div class="info-item">
                                <strong>Sign Longitude:</strong> ${house.SignLonDMS}
                            </div>
                            <div class="info-item">
                                <strong>Deg Size:</strong> ${house.DegSize.toFixed(2)}°
                            </div>
                            <div class="info-item">
                                <strong>Nakshatra:</strong> ${house.Nakshatra}
                            </div>
                            <div class="info-item">
                                <strong>Rasi Lord:</strong> ${house.RasiLord}
                            </div>
                            <div class="info-item">
                                <strong>Nakshatra Lord:</strong> ${house.NakshatraLord}
                            </div>
                            <div class="info-item">
                                <strong>Sub Lord:</strong> ${house.SubLord}
                            </div>
                        </div>
                    `;
                    container.appendChild(houseDiv);
                }
            });
        }
        
        function displayPlanets(planetsData) {
            const tbody = document.getElementById('planetsBody');
            tbody.innerHTML = '';
            
            planetsData.forEach(planet => {
                const row = document.createElement('tr');
                const retroBadge = planet.isRetroGrade 
                    ? '<span class="badge badge-retro">Retrograde</span>'
                    : '<span class="badge badge-direct">Direct</span>';
                
                row.innerHTML = `
                    <td><strong>${planet.Object}</strong></td>
                    <td>${planet.Rasi}</td>
                    <td>${retroBadge}</td>
                    <td>${planet.LonDecDeg.toFixed(3)}°</td>
                    <td>${planet.SignLonDMS}</td>
                    <td>${planet.Nakshatra}</td>
                    <td>${planet.RasiLord}</td>
                    <td>${planet.NakshatraLord}</td>
                    <td>${planet.SubLord}</td>
                    <td><strong>${planet.HouseNr}</strong></td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function displayHouses(housesData) {
            const tbody = document.getElementById('housesBody');
            tbody.innerHTML = '';
            
            housesData.forEach(house => {
                const row = document.createElement('tr');
                const isHighlighted = [1, 6, 11].includes(house.HouseNr);
                
                if (isHighlighted) {
                    row.className = 'highlighted-house';
                }
                
                row.innerHTML = `
                    <td><strong>${house.Object} (${house.HouseNr})</strong></td>
                    <td>${house.Rasi}</td>
                    <td>${house.LonDecDeg.toFixed(3)}°</td>
                    <td>${house.SignLonDMS}</td>
                    <td>${house.DegSize.toFixed(2)}°</td>
                    <td>${house.Nakshatra}</td>
                    <td>${house.RasiLord}</td>
                    <td>${house.NakshatraLord}</td>
                    <td><strong>${house.SubLord}</strong></td>
                `;
                tbody.appendChild(row);
            });
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/fetcher", response_class=HTMLResponse)
async def get_fetcher_page():
    """Serves the batch time fetcher page for extracting 1st, 6th, and 11th house data"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KP Astrology Batch Fetcher</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --success-color: #059669;
            --error-color: #dc2626;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --bg-light: #f9fafb;
            --bg-white: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-light);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 16px;
        }
        
        .container {
            max-width: 1100px;
            margin: 0 auto;
        }
        
        .header {
            background: var(--bg-white);
            padding: 20px 24px;
            margin-bottom: 16px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 4px;
        }
        
        .header p {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        .card {
            background: var(--bg-white);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 24px;
            margin-bottom: 16px;
        }
        
        .section-header {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-size: 0.813rem;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 4px;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            padding: 8px 10px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.875rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .form-group textarea {
            min-height: 140px;
            resize: vertical;
            font-family: 'Courier New', monospace;
            font-size: 0.813rem;
        }
        
        .config-bar {
            background: var(--bg-light);
            padding: 10px 12px;
            border-radius: 4px;
            margin-bottom: 16px;
            display: flex;
            gap: 20px;
            font-size: 0.813rem;
            color: var(--text-secondary);
        }
        
        .config-bar strong {
            color: var(--text-primary);
        }
        
        .btn {
            background: var(--primary-color);
            color: white;
            padding: 10px 24px;
            border: none;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .btn:hover {
            background: var(--secondary-color);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-success {
            background: var(--success-color);
        }
        
        .btn-success:hover {
            background: #047857;
        }
        
        .btn-container {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 16px;
        }
        
        .loading {
            text-align: center;
            padding: 24px;
            color: var(--text-secondary);
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 2px solid var(--border-color);
            border-top: 2px solid var(--primary-color);
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 8px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .table-container {
            overflow-x: auto;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }
        
        thead {
            background: var(--primary-color);
            color: white;
        }
        
        th {
            padding: 10px 12px;
            text-align: center;
            font-weight: 500;
        }
        
        td {
            padding: 8px 12px;
            border-bottom: 1px solid var(--border-color);
            text-align: center;
        }
        
        tbody tr:hover {
            background: var(--bg-light);
        }
        
        tbody tr:last-child td {
            border-bottom: none;
        }
        
        .time-cell {
            font-weight: 600;
            color: var(--primary-color);
            background: var(--bg-light);
        }
        
        .label-cell {
            text-align: left;
            padding-left: 16px;
            color: var(--text-secondary);
            font-size: 0.813rem;
        }
        
        .divider-row td {
            border-bottom: 2px solid var(--border-color);
        }
        
        .alert {
            padding: 12px 16px;
            border-radius: 4px;
            margin: 16px 0;
            display: none;
            font-size: 0.875rem;
        }
        
        .alert.show {
            display: block;
        }
        
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border-left: 4px solid var(--error-color);
        }
        
        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border-left: 4px solid var(--success-color);
        }
        
        .info-banner {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 4px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-size: 0.813rem;
            color: var(--text-secondary);
        }
        
        .info-banner ul {
            margin: 8px 0 0 20px;
        }
        
        .info-banner li {
            margin: 4px 0;
        }
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .config-bar {
                flex-direction: column;
                gap: 8px;
            }
            
            table {
                font-size: 0.75rem;
            }
            
            th, td {
                padding: 6px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>KP Astrology Batch Fetcher</h1>
            <p>Extract houses 1, 6, 11 data for multiple times</p>
        </div>
        
        <div class="card">
            <div class="config-bar">
                <div><strong>Ayanamsa:</strong> Krishnamurti</div>
                <div><strong>House System:</strong> Placidus (KP)</div>
            </div>
            
            <div class="info-banner">
                <strong>Instructions:</strong>
                <ul>
                    <li>Enter date, location, and timezone</li>
                    <li>Add times (one per line) in HH:MM or HH:MM:SS format</li>
                    <li>Click Fetch Data to generate results</li>
                    <li>Use Copy button to paste into Excel</li>
                </ul>
            </div>
            
            <form id="fetcherForm">
                <div class="section-header">Date</div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="year">Year</label>
                        <input type="number" id="year" name="year" value="2025" required min="1900" max="2100">
                    </div>
                    <div class="form-group">
                        <label for="month">Month</label>
                        <input type="number" id="month" name="month" value="1" required min="1" max="12">
                    </div>
                    <div class="form-group">
                        <label for="day">Day</label>
                        <input type="number" id="day" name="day" value="10" required min="1" max="31">
                    </div>
                </div>
                
                <div class="section-header">Location</div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="latitude">Latitude</label>
                        <input type="number" id="latitude" name="latitude" value="28.2323" required step="0.0001" min="-90" max="90">
                    </div>
                    <div class="form-group">
                        <label for="longitude">Longitude</label>
                        <input type="number" id="longitude" name="longitude" value="83.923" required step="0.0001" min="-180" max="180">
                    </div>
                        <div class="form-group">
                            <label for="utc">Timezone</label>
                            <select id="utc" name="utc" required>
                                <optgroup label="Africa">
                                    <option value="Africa/Abidjan">Africa/Abidjan</option>
                                    <option value="Africa/Accra">Africa/Accra</option>
                                    <option value="Africa/Addis_Ababa">Africa/Addis_Ababa</option>
                                    <option value="Africa/Algiers">Africa/Algiers</option>
                                    <option value="Africa/Cairo">Africa/Cairo</option>
                                    <option value="Africa/Casablanca">Africa/Casablanca</option>
                                    <option value="Africa/Johannesburg">Africa/Johannesburg</option>
                                    <option value="Africa/Lagos">Africa/Lagos</option>
                                    <option value="Africa/Nairobi">Africa/Nairobi</option>
                                    <option value="Africa/Tunis">Africa/Tunis</option>
                                </optgroup>
                                <optgroup label="America - North">
                                    <option value="America/Anchorage">America/Anchorage</option>
                                    <option value="America/Chicago">America/Chicago</option>
                                    <option value="America/Denver">America/Denver</option>
                                    <option value="America/Los_Angeles">America/Los_Angeles</option>
                                    <option value="America/Mexico_City">America/Mexico_City</option>
                                    <option value="America/New_York">America/New_York</option>
                                    <option value="America/Phoenix">America/Phoenix</option>
                                    <option value="America/Toronto">America/Toronto</option>
                                    <option value="America/Vancouver">America/Vancouver</option>
                                </optgroup>
                                <optgroup label="America - Central">
                                    <option value="America/Belize">America/Belize</option>
                                    <option value="America/Costa_Rica">America/Costa_Rica</option>
                                    <option value="America/El_Salvador">America/El_Salvador</option>
                                    <option value="America/Guatemala">America/Guatemala</option>
                                    <option value="America/Havana">America/Havana</option>
                                    <option value="America/Jamaica">America/Jamaica</option>
                                    <option value="America/Panama">America/Panama</option>
                                </optgroup>
                                <optgroup label="America - South">
                                    <option value="America/Argentina/Buenos_Aires">America/Argentina/Buenos_Aires</option>
                                    <option value="America/Bogota">America/Bogota</option>
                                    <option value="America/Caracas">America/Caracas</option>
                                    <option value="America/Lima">America/Lima</option>
                                    <option value="America/Santiago">America/Santiago</option>
                                    <option value="America/Sao_Paulo">America/Sao_Paulo</option>
                                </optgroup>
                                <optgroup label="Asia - Middle East">
                                    <option value="Asia/Baghdad">Asia/Baghdad</option>
                                    <option value="Asia/Beirut">Asia/Beirut</option>
                                    <option value="Asia/Damascus">Asia/Damascus</option>
                                    <option value="Asia/Dubai">Asia/Dubai</option>
                                    <option value="Asia/Jerusalem">Asia/Jerusalem</option>
                                    <option value="Asia/Kuwait">Asia/Kuwait</option>
                                    <option value="Asia/Riyadh">Asia/Riyadh</option>
                                    <option value="Asia/Tehran">Asia/Tehran</option>
                                </optgroup>
                                <optgroup label="Asia - Central">
                                    <option value="Asia/Almaty">Asia/Almaty</option>
                                    <option value="Asia/Karachi">Asia/Karachi</option>
                                    <option value="Asia/Tashkent">Asia/Tashkent</option>
                                </optgroup>
                                <optgroup label="Asia - South">
                                    <option value="Asia/Colombo">Asia/Colombo</option>
                                    <option value="Asia/Dhaka">Asia/Dhaka</option>
                                    <option value="Asia/Kathmandu">Asia/Kathmandu</option>
                                    <option value="Asia/Kolkata">Asia/Kolkata</option>
                                </optgroup>
                                <optgroup label="Asia - East">
                                    <option value="Asia/Bangkok">Asia/Bangkok</option>
                                    <option value="Asia/Hong_Kong">Asia/Hong_Kong</option>
                                    <option value="Asia/Jakarta">Asia/Jakarta</option>
                                    <option value="Asia/Kuala_Lumpur">Asia/Kuala_Lumpur</option>
                                    <option value="Asia/Manila">Asia/Manila</option>
                                    <option value="Asia/Seoul">Asia/Seoul</option>
                                    <option value="Asia/Shanghai">Asia/Shanghai</option>
                                    <option value="Asia/Singapore">Asia/Singapore</option>
                                    <option value="Asia/Taipei">Asia/Taipei</option>
                                    <option value="Asia/Tokyo">Asia/Tokyo</option>
                                </optgroup>
                                <optgroup label="Atlantic">
                                    <option value="Atlantic/Azores">Atlantic/Azores</option>
                                    <option value="Atlantic/Bermuda">Atlantic/Bermuda</option>
                                    <option value="Atlantic/Cape_Verde">Atlantic/Cape_Verde</option>
                                    <option value="Atlantic/Reykjavik">Atlantic/Reykjavik</option>
                                </optgroup>
                                <optgroup label="Australia">
                                    <option value="Australia/Adelaide">Australia/Adelaide</option>
                                    <option value="Australia/Brisbane">Australia/Brisbane</option>
                                    <option value="Australia/Darwin">Australia/Darwin</option>
                                    <option value="Australia/Melbourne">Australia/Melbourne</option>
                                    <option value="Australia/Perth">Australia/Perth</option>
                                    <option value="Australia/Sydney">Australia/Sydney</option>
                                </optgroup>
                                <optgroup label="Europe - West">
                                    <option value="Europe/Dublin">Europe/Dublin</option>
                                    <option value="Europe/Lisbon">Europe/Lisbon</option>
                                    <option value="Europe/London">Europe/London</option>
                                </optgroup>
                                <optgroup label="Europe - Central">
                                    <option value="Europe/Amsterdam">Europe/Amsterdam</option>
                                    <option value="Europe/Berlin">Europe/Berlin</option>
                                    <option value="Europe/Brussels">Europe/Brussels</option>
                                    <option value="Europe/Copenhagen">Europe/Copenhagen</option>
                                    <option value="Europe/Madrid">Europe/Madrid</option>
                                    <option value="Europe/Paris">Europe/Paris</option>
                                    <option value="Europe/Rome">Europe/Rome</option>
                                    <option value="Europe/Stockholm">Europe/Stockholm</option>
                                    <option value="Europe/Vienna">Europe/Vienna</option>
                                    <option value="Europe/Zurich">Europe/Zurich</option>
                                </optgroup>
                                <optgroup label="Europe - East">
                                    <option value="Europe/Athens">Europe/Athens</option>
                                    <option value="Europe/Bucharest">Europe/Bucharest</option>
                                    <option value="Europe/Helsinki">Europe/Helsinki</option>
                                    <option value="Europe/Istanbul">Europe/Istanbul</option>
                                    <option value="Europe/Kiev">Europe/Kiev</option>
                                    <option value="Europe/Moscow">Europe/Moscow</option>
                                    <option value="Europe/Warsaw">Europe/Warsaw</option>
                                </optgroup>
                                <optgroup label="Pacific">
                                    <option value="Pacific/Auckland">Pacific/Auckland</option>
                                    <option value="Pacific/Fiji">Pacific/Fiji</option>
                                    <option value="Pacific/Guam">Pacific/Guam</option>
                                    <option value="Pacific/Honolulu">Pacific/Honolulu</option>
                                    <option value="Pacific/Pago_Pago">Pacific/Pago_Pago</option>
                                    <option value="Pacific/Tahiti">Pacific/Tahiti</option>
                                </optgroup>
                                <optgroup label="UTC">
                                    <option value="UTC">UTC</option>
                                </optgroup>
                            </select>
                        </div>
                </div>
                
                <div class="section-header">Times</div>
                <div class="form-group">
                    <label for="times">One time per line (HH:MM or HH:MM:SS)</label>
                    <textarea id="times" name="times" required placeholder="11:09&#10;11:26&#10;11:42&#10;11:58&#10;12:14&#10;12:31"></textarea>
                </div>
                
                <div class="btn-container">
                    <button type="submit" class="btn" id="submitBtn">
                        <span>▶</span> Fetch Data
                    </button>
                </div>
            </form>
            
            <div class="alert alert-error" id="errorMsg"></div>
            <div class="alert alert-success" id="successMsg"></div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing times...</p>
            </div>
        </div>
        
        <div class="results" id="results">
            <div class="card">
                <div class="section-header">Results</div>
                
                <div class="btn-container" style="margin-bottom: 16px;">
                    <button class="btn btn-success" id="copyBtn">
                        <span>⎘</span> Copy to Clipboard
                    </button>
                </div>
                
                <div class="table-container">
                    <table id="resultsTable">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>1</th>
                                <th>6</th>
                                <th>11</th>
                            </tr>
                        </thead>
                        <tbody id="resultsBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('fetcherForm');
        const submitBtn = document.getElementById('submitBtn');
        const copyBtn = document.getElementById('copyBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const errorMsg = document.getElementById('errorMsg');
        const successMsg = document.getElementById('successMsg');
        
        let fetchedData = [];
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Reset UI
            errorMsg.classList.remove('show');
            successMsg.classList.remove('show');
            results.classList.remove('show');
            loading.classList.add('show');
            submitBtn.disabled = true;
            
            // Parse times from textarea
            const timesText = document.getElementById('times').value;
            const timesList = timesText.split('\\n')
                .map(t => t.trim())
                .filter(t => t.length > 0);
            
            if (timesList.length === 0) {
                errorMsg.textContent = 'Error: Please enter at least one time';
                errorMsg.classList.add('show');
                loading.classList.remove('show');
                submitBtn.disabled = false;
                return;
            }
            
            // Get form data
            const year = parseInt(document.getElementById('year').value);
            const month = parseInt(document.getElementById('month').value);
            const day = parseInt(document.getElementById('day').value);
            const latitude = parseFloat(document.getElementById('latitude').value);
            const longitude = parseFloat(document.getElementById('longitude').value);
            const utc = document.getElementById('utc').value;
            
            fetchedData = [];
            const tbody = document.getElementById('resultsBody');
            tbody.innerHTML = '';
            
            // Process each time
            for (const timeStr of timesList) {
                try {
                    const timeResult = await fetchTimeData(year, month, day, timeStr, latitude, longitude, utc);
                    if (timeResult) {
                        fetchedData.push(timeResult);
                        displayTimeResult(timeResult);
                    }
                } catch (error) {
                    console.error('Error processing time ' + timeStr + ':', error);
                }
            }
            
            if (fetchedData.length > 0) {
                results.classList.add('show');
                results.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                errorMsg.textContent = 'Error: Failed to fetch data. Please check your inputs.';
                errorMsg.classList.add('show');
            }
            
            loading.classList.remove('show');
            submitBtn.disabled = false;
        });
        
        async function fetchTimeData(year, month, day, timeStr, latitude, longitude, utc) {
            // Parse time string
            const timeParts = timeStr.split(':');
            const hour = parseInt(timeParts[0]);
            const minute = parseInt(timeParts[1] || '0');
            const second = parseInt(timeParts[2] || '0');
            
            const formData = {
                year: year,
                month: month,
                day: day,
                hour: hour,
                minute: minute,
                second: second,
                utc: utc,
                latitude: latitude,
                longitude: longitude,
                ayanamsa: 'Krishnamurti',
                house_system: 'Placidus',
                return_style: 'string'
            };
            
            const response = await fetch('/get_all_horoscope_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch data for time ' + timeStr);
            }
            
            const data = await response.json();
            
            // Extract houses 1, 6, 11
            const house1 = data.houses_data.find(h => h.HouseNr === 1);
            const house6 = data.houses_data.find(h => h.HouseNr === 6);
            const house11 = data.houses_data.find(h => h.HouseNr === 11);
            
            // Format time for display
            const hourStr = hour.toString().padStart(2, '0');
            const minuteStr = minute.toString().padStart(2, '0');
            const timeDisplay = hourStr + ':' + minuteStr;
            
            return {
                time: timeDisplay,
                house1: house1,
                house6: house6,
                house11: house11
            };
        }
        
        function displayTimeResult(result) {
            const tbody = document.getElementById('resultsBody');
            
            const timeRow = document.createElement('tr');
            timeRow.innerHTML = `
                <td class="time-cell">${result.time}</td>
                <td>1</td>
                <td>6</td>
                <td>11</td>
            `;
            tbody.appendChild(timeRow);
            
            const rasiRow = document.createElement('tr');
            rasiRow.innerHTML = `
                <td class="label-cell">rasi lord</td>
                <td>${result.house1.RasiLord}</td>
                <td>${result.house6.RasiLord}</td>
                <td>${result.house11.RasiLord}</td>
            `;
            tbody.appendChild(rasiRow);
            
            const nakshatraRow = document.createElement('tr');
            nakshatraRow.innerHTML = `
                <td class="label-cell">nakshatra</td>
                <td>${result.house1.Nakshatra}</td>
                <td>${result.house6.Nakshatra}</td>
                <td>${result.house11.Nakshatra}</td>
            `;
            tbody.appendChild(nakshatraRow);
            
            const sublordRow = document.createElement('tr');
            sublordRow.className = 'divider-row';
            sublordRow.innerHTML = `
                <td class="label-cell">sublord</td>
                <td>${result.house1.SubLord}</td>
                <td>${result.house6.SubLord}</td>
                <td>${result.house11.SubLord}</td>
            `;
            tbody.appendChild(sublordRow);
        }
        
        copyBtn.addEventListener('click', () => {
            let clipboardText = '';
            
            fetchedData.forEach(result => {
                clipboardText += result.time + '\\t1\\t6\\t11\\n';
                clipboardText += 'rasi lord\\t' + result.house1.RasiLord + '\\t' + result.house6.RasiLord + '\\t' + result.house11.RasiLord + '\\n';
                clipboardText += 'nakshatra\\t' + result.house1.Nakshatra + '\\t' + result.house6.Nakshatra + '\\t' + result.house11.Nakshatra + '\\n';
                clipboardText += 'sublord\\t' + result.house1.SubLord + '\\t' + result.house6.SubLord + '\\t' + result.house11.SubLord + '\\n';
            });
            
            navigator.clipboard.writeText(clipboardText).then(() => {
                successMsg.textContent = 'Data copied to clipboard successfully';
                successMsg.classList.add('show');
                setTimeout(() => {
                    successMsg.classList.remove('show');
                }, 3000);
            }).catch(err => {
                errorMsg.textContent = 'Failed to copy: ' + err.message;
                errorMsg.classList.add('show');
            });
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/get_all_horoscope_data")
async def get_chart_data(input: ChartInput):
    """
    Generates all data for a given time and location, based on the selected ayanamsa & house system
    """
    horoscope = VedicAstro.VedicHoroscopeData(input.year, input.month, input.day, 
                                              input.hour, input.minute, input.second,
                                              input.latitude, input.longitude, 
                                              input.utc,
                                              input.ayanamsa, input.house_system)
    chart = horoscope.generate_chart()
    
    planets_data = horoscope.get_planets_data_from_chart(chart)
    houses_data = horoscope.get_houses_data_from_chart(chart)
    planet_significators = horoscope.get_planet_wise_significators(planets_data, houses_data)
    planetary_aspects = horoscope.get_planetary_aspects(chart)
    house_significators = horoscope.get_house_wise_significators(planets_data, houses_data)
    vimshottari_dasa_table = horoscope.compute_vimshottari_dasa(chart)
    consolidated_chart_data = horoscope.get_consolidated_chart_data(planets_data=planets_data, 
                                                                    houses_data=houses_data,
                                                                    return_style = input.return_style)

    return {
        "planets_data": [planet._asdict() for planet in planets_data],
        "houses_data": [house._asdict() for house in houses_data],
        "planet_significators": planet_significators,
        "planetary_aspects": planetary_aspects,
        "house_significators": house_significators,
        "vimshottari_dasa_table": vimshottari_dasa_table,
        "consolidated_chart_data": consolidated_chart_data
    }

@app.post("/get_all_horary_data")
async def get_horary_data(input: HoraryChartInput):
    """
    Generates all data for a given horary number, time and location as per KP Astrology system
    """
    matched_time, vhd_hora_houses_chart, houses_data  = horary_chart.find_exact_ascendant_time(input.year, input.month, input.day, input.utc, input.latitude, input.longitude, input.horary_number, input.ayanamsa)
    vhd_hora = VedicAstro.VedicHoroscopeData(input.year, input.month, input.day, 
                                              input.hour, input.minute, input.second,
                                              input.utc, input.latitude, input.longitude, 
                                              input.ayanamsa, input.house_system)
    
    vhd_hora_planets_chart = vhd_hora.generate_chart()
    planets_data = vhd_hora.get_planets_data_from_chart(vhd_hora_planets_chart, vhd_hora_houses_chart)
    planet_significators = vhd_hora.get_planet_wise_significators(planets_data, houses_data)
    planetary_aspects = vhd_hora.get_planetary_aspects(vhd_hora_planets_chart)
    house_significators = vhd_hora.get_house_wise_significators(planets_data, houses_data)
    vimshottari_dasa_table = vhd_hora.compute_vimshottari_dasa(vhd_hora_planets_chart)
    consolidated_chart_data = vhd_hora.get_consolidated_chart_data(planets_data=planets_data, 
                                                                    houses_data=houses_data,
                                                                    return_style = input.return_style)

    return {
        "planets_data": [planet._asdict() for planet in planets_data],
        "houses_data": [house._asdict() for house in houses_data],
        "planet_significators": planet_significators,
        "planetary_aspects": planetary_aspects,
        "house_significators": house_significators,
        "vimshottari_dasa_table": vimshottari_dasa_table,
        "consolidated_chart_data": consolidated_chart_data
    }