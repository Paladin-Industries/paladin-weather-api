from flask import Flask, request, jsonify
import random

from getPoints import get_points

app = Flask(__name__)

@app.route("/test", methods=["GET", "POST"])
def test():
   return jsonify({"test": "success"})

@app.route("/getWeather", methods=["POST"])
def get_weather():
  data = request.get_json()

  if not data or not isinstance(data, list):
    return jsonify({ "error": "Invalid input format" }), 400

  try:

    if len(data) != 3:
       return jsonify({ "error": "Data must be formatted as [lat_point, lng_point, time_bounds]"}), 400

    for coordinates in data:
      if len(coordinates) != 2:
        return jsonify({ "error": "Each element must be formatted as [float, float]"}), 400
      
    north_west, south_east, time_interval = data

    result = get_points(south_east=south_east, north_west=north_west, time_interval=time_interval)

    return jsonify({"data_points": result}), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
	app.run(debug=True)
