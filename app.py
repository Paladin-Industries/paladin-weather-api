from flask import Flask, request, jsonify
import random

from getPoints import get_points

app = Flask(__name__)

@app.route("/getWeather", methods=["POST"])
def get_weather():
  data = request.get_json()

  if not data or not isinstance(data, list):
    return jsonify({ "error": "Invalid input format" }), 400

  try:

    for coordinates in data:
      if len(coordinates) != 3:
        return jsonify({ "error": "Each element must be formatted as [lat_point, lng_point, time_bounds]"}), 400
      
      north_west, south_east, time_interval = coordinates

      result = get_points(south_east=south_east, north_west=north_west, time_interval=time_interval)

    return jsonify({"data_points": result}), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
	app.run(debug=True)
