# app.py
from flask import Flask, request, jsonify, render_template_string, g
import sqlite3
from datetime import datetime
import folium

DATABASE = "locations.db"
app = Flask(__name__)

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.execute("""CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        lat REAL,
                        lon REAL,
                        ts TEXT
                      )""")
        db.commit()
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

INDEX_HTML = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Share location</title></head>
<body>
  <h1>Share your location (consent required)</h1>
  <label>Name: <input id="name" /></label>
  <button id="share">Share my location</button>
  <div id="status"></div>
  <p><a href="/map" target="_blank">Open map</a> (shows stored locations)</p>

<script>
document.getElementById('share').addEventListener('click', function(){
  if(!navigator.geolocation){
    document.getElementById('status').innerText = 'Geolocation not supported';
    return;
  }
  navigator.geolocation.getCurrentPosition(function(pos){
    fetch('/send_location', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: document.getElementById('name').value || 'anonymous',
        lat: pos.coords.latitude,
        lon: pos.coords.longitude
      })
    }).then(r => r.json()).then(j => {
      document.getElementById('status').innerText = JSON.stringify(j);
    }).catch(e => document.getElementById('status').innerText = e);
  }, function(err){
    document.getElementById('status').innerText = 'Error: ' + err.message;
  });
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/send_location', methods=['POST'])
def send_location():
    data = request.get_json()
    if not data or 'lat' not in data or 'lon' not in data:
        return jsonify({'status':'error','message':'missing coordinates'}), 400
    name = data.get('name', 'anonymous')
    lat = float(data['lat'])
    lon = float(data['lon'])
    ts = datetime.utcnow().isoformat()
    db = get_db()
    db.execute('INSERT INTO locations (name, lat, lon, ts) VALUES (?,?,?,?)',
               (name, lat, lon, ts))
    db.commit()
    return jsonify({'status':'ok'})

@app.route('/map')
def map_view():
    db = get_db()
    rows = db.execute('SELECT name, lat, lon, ts FROM locations').fetchall()
    if rows:
        last = rows[-1]
        m = folium.Map(location=[last[1], last[2]], zoom_start=12)
    else:
        m = folium.Map(location=[0,0], zoom_start=2)
    for name, lat, lon, ts in rows:
        folium.Marker([lat, lon], popup=f'{name} @ {ts}').add_to(m)
    return m._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)
