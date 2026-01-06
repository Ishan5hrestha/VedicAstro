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