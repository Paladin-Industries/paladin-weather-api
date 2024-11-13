from flask import Flask, request, jsonify
from flask_cors import CORS

from getPoints import *

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@app.route("/test", methods=["GET", "POST"])
def test():
   return jsonify({"test": "success"})

# @app.route("/getWeather", methods=["POST"])
# def get_weather():
#   data = request.get_json()

#   print(data)

#   if not data or not isinstance(data, list):
#     return jsonify({ "error": "Invalid input format" }), 400

#   try:

#     if len(data) != 3:
#        return jsonify({ "error": "Data must be formatted as [north_west_lat_lng, south_east_lat_lng, time_bounds]"}), 400

#     for coordinates in data:
#       if len(coordinates) != 2:
#         return jsonify({ "error": "Each element must be formatted as [float, float]"}), 400
      
#     north_west, south_east, time_interval = data

#     result = get_points(south_east=south_east, north_west=north_west, time_interval=time_interval) # here's where the model is read

#     return jsonify({"data_points": result}), 200

#   except Exception as e:
#     return jsonify({"error": str(e)}), 400
  
@app.route("/getWeather", methods=["POST"])
def get_weather():
  data = request.get_json()

  print(data)

  if not data or not isinstance(data, list):
    return jsonify({ "error": "Invalid input format" }), 400

  try:

    if len(data) != 3:
       return jsonify({ "error": "Data must be formatted as [north_west_lat_lng, south_east_lat_lng, time_bounds]"}), 400

    for coordinates in data:
      if len(coordinates) != 2:
        return jsonify({ "error": "Each element must be formatted as [float, float]"}), 400
      
    north_west, south_east, time_interval = data

    result = WxPal(south_east=south_east, north_west=north_west, time_interval=time_interval) # here's where the model is read

    # return jsonify({"data_points": result}), 200
    return jsonify({"image": result}), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 400
  
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
	app.run(debug=True)
