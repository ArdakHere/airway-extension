import base64  # remove imports that are not used
from io import BytesIO

from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from src.back_krisha import *
from src.plotter import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# we also gotta add Pydantic models for validation
# Use FastAPI everywhere
@app.route("/analyze/kolesa", methods=["POST"])
def analyze_kolesa():
    try:
        # all the functionality has to be in a separate utils file
        data = request.json
        html_data = data.get('html')
        car_data = read_remote_kolesa_page(html_data)
        car_emission_and_recs_tuple = request_metrics_and_recommendations(car_data)
        car_emission_data = car_emission_and_recs_tuple[0]

        # use single кавычки
        gas_mileage = car_emission_data["Gas expenditure"]
        co2_val = car_emission_data["CO2"]
        car_recommendations_ev_nonev, nonev_recs, ev_recs = get_car_recommendations(car_data['price'])

        gas_mileage_number = extract_gas_mileage(gas_mileage)
        co2_val_number = extract_co2_emissions(co2_val)

        ecofriendly_index_car = ((gas_mileage_number * 10) + co2_val_number) / 1000
        effect_index_numeric = ecofriendly_index_car

        # this can be turned into a dict, in a separate file
        if ecofriendly_index_car >= 0.5:
            rgbColor = [131, 0, 0]
            effect_index = "Опасное"
        if ecofriendly_index_car >= 0.3 and ecofriendly_index_car < 0.5:
            rgbColor = [255, 225, 20]
            effect_index = "Высокое"
        if ecofriendly_index_car >= 0.2 and ecofriendly_index_car < 0.3:
            rgbColor = [198, 239, 86]
            effect_index = "Среднее"
        if ecofriendly_index_car >= 0 and ecofriendly_index_car < 0.2:
            rgbColor = [27, 152, 3]
            effect_index = "Низкое"

        # work on indentations
        # inconsistent кавычки
        emission_data = {
            'gas_mileage': gas_mileage_number,
            'effect_index': effect_index,
            "effect_index_numeric": effect_index_numeric,
            'rgbColor': rgbColor,
            'ev_car_recs': ev_recs,
            'nonev_car_recs': nonev_recs,
        }
        emission_data.update(car_data)
        return jsonify(emission_data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/analyze/krisha", methods=["POST"])
def analyze_krisha():
    try:  # error is here in the try block

        data = request.json

        coordinates = data.get('coords')

        if not coordinates:
            return jsonify({"error": "Coordinates missing"}), 400

        new_coords = {'Latitude': coordinates.pop('lat'), 'Longitude': coordinates.pop('lon')}

        result = access_metrics(new_coords)

        result['latitude'] = new_coords['Latitude']
        result['longitude'] = new_coords['Longitude']

        aq_index_numeric_saved = result['aq_index_numeric']

        # should be turned into a dict inside of something different
        if aq_index_numeric_saved <= 40:
            result['aq_index_numeric'] = "Не несет риска, воздух чист"
        if 50 >= aq_index_numeric_saved > 40:
            result['aq_index_numeric'] = "Минимальное"
        if 70 >= aq_index_numeric_saved > 50:
            result['aq_index_numeric'] = "Средняя"
        if 80 >= aq_index_numeric_saved > 70:
            result['aq_index_numeric'] = "Повышенная"
        if 90 > aq_index_numeric_saved > 80:
            result['aq_index_numeric'] = "Высокая"
        if aq_index_numeric_saved >= 90:
            result['aq_index_numeric'] = "Опасная"

        two_gis_key = os.getenv('TWOGIS_API_KEY')
        parks = make_2gis_request_and_return_object_count(
        two_gis_key,
            new_coords['Latitude'],
            new_coords['Longitude'],
            "adm_div",
            800,
            "парк"
        )

        ev_chargers = make_2gis_request_and_return_object_count(
            two_gis_key,
            new_coords['Latitude'],
            new_coords['Longitude'],
            "",
            500,
            "зарядка для автомобиля"
        )

        ## missing the numeric number of aq
        result.update({"aq_index_numeric_int": aq_index_numeric_saved,
            "num_of_parks": parks,
                       "num_of_ev_chargers": ev_chargers})

        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 6969

@app.route("/get_krisha_report", methods=["POST"])
def get_krisha_report():
    try:

        data = request.json.get('data', {})

        # should just pass the data dict inside of the function, no need to unpack it here
        image_base64 = test_generate_report_for_an_apartment(
            data['latitude'],
            data['longitude'],
            data['aq_index_numeric_int'],
            data['aq_index_color'],
            data['color_pm25'],
            data['color_pm10'],
            data['color_co'],
            data['pm25'],
            data['pm10'],
            data['co'],
            ""
        )

        new_dict = {'report_image': image_base64}
        return jsonify(new_dict)

    except Exception as e:
        print(f"Ayyy: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/get_kolesa_report", methods=["POST"])
def get_kolesa_report():
    try:

        data = request.json.get('data', {})

        image_base64 = generate_report_for_a_car(
            data['car_title'],
            data['generation'],
            data['engine_displacement'],
            data['distance run (km)'],
            data['N-wheel drive'],
            data['price'],
            data['gas_mileage'],
            data['effect_index_numeric'],
        )

        new_dict = {'report_image': image_base64}
        return jsonify(new_dict)

    except Exception as e:
        print(f"Ayyy: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/find_objects", methods=["POST"])
def find_objects():
    # add try except block

    data = request.json
    coords = data.get('coords')
    object_to_search = data.get('objectType')
    distance = data.get('distance')


    two_gis_key = os.getenv('TWOGIS_API_KEY')

    number_of_objects = make_2gis_request_and_return_object_count(
        two_gis_key,
        coords['lat'],
        coords['lon'],
        "",
        distance,
        object_to_search
    )

    return jsonify(count=number_of_objects)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
