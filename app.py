import base64  # remove imports that are not used
from io import BytesIO

from src.validation.schema import FindObjectModel, CarListingData, AptListingData, AptListingResponse, CarListingResponse
from src.services.core import get_object_count, get_car_eco_data, get_apt_eco_data

from fastapi import FastAPI
app = FastAPI()


@app.get('/')
def home():
    return {"message": "Welcome to the Airway API!"}


@app.post('/analyze/kolesa')
def analyze_kolesa(data: CarListingData) -> CarListingResponse:
    """
        Returns eco data of the car based on its
        characteristics
    \n**Args**:
        \n data (CarListingData): containing the following
            - car_title (str): Brand and model of the car
            - prod_year (str): Production year
            - engine_displacement (float): Engine displacement of the car
            - distance_run_km (int): Distance run in kilometers
            - N_wheel_drive (WheelDrive): Number of wheels drive
            - price (int): Price of the car
    \n**Returns**:
        \n data (dict): containing the following
            - fuel_efficiency (float): Gas mileage of the car (l/100km)
            - effect_index (dict); containing the following
                - rgbColor (tuple): RGB color code
                - qualitativeIndex (str): Qualitative index
            - effect_index_numeric (float): Numeric value of the eco index
            - ev_car_recs (str): Recommendations for electric cars
            - nonev_car_recs (str): Recommendations for non-electric cars
    """
    return get_car_eco_data(data)
    

@app.post('/analyze/krisha')
def analyze_krisha(data: AptListingData) -> AptListingResponse:
    """
        Returns eco data of the apartment based on its
        characteristics
    \n**Args**:
        \ncoords (CoordsModel): containing the following
            - lat (float): Latitude coordinate
            - lon (float): Longitude coordinate
        location (str): Location of the apartment (city, settlement, etc.)
        street (str): Street of the apartment
        floor_number (int): Floor number of the apartment
        area (float): Area of the apartment in square meters
        room_count (int): The amount of rooms in the apartment
        year_of_construction (int): Year of construction of the apartment
    \n**Returns**:
        \npm25 (float): PM2.5 value
        pm10 (float): PM10 value
        co (float): CO value
        aq_index_numeric_int (float): Numeric value of the eco index
        aq_index_color (tuple): Color of the eco index
        color_pm25 (tuple): Color of the PM2.5 value
        color_pm10 (tuple): Color of the PM10 value
        color_co (tuple): Color of the CO value
        num_of_parks (int): Number of parks within 800m
        num_of_ev_chargers (int): Number of electric car chargers within 500m
    """ 
    return get_apt_eco_data(data)


@app.post("/find_objects")
def find_objects(data: FindObjectModel) -> int:
    """
        Return the number of objects found within the radius by 2GIS API
    \n**Args**:
        \ndata (FindObjectModel): containing the following
            coords (CoordsModel), containing the following keys:
                - lat: float, latitude
                - lon: float, longitude
            radius (int): radius in meters
            object_to_search (str): object to search for
    \n**Returns**:
        \ntotal (int): number of objects found within the radius
    """
    # add try except block 

    return get_object_count(data)



# ### REPORT GENERATION ###
# @app.post('/get_krisha_report')
# def get_krisha_report():
#     try:

#         data = request.json.get('data', {})

#         # should just pass the data dict inside of the function, no need to unpack it here
#         image_base64 = test_generate_report_for_an_apartment(
#             data['latitude'],
#             data['longitude'],
#             data['aq_index_numeric_int'],
#             data['aq_index_color'],
#             data['color_pm25'],
#             data['color_pm10'],
#             data['color_co'],
#             data['pm25'],
#             data['pm10'],
#             data['co'],
#             ""
#         )

#         new_dict = {'report_image': image_base64}
#         return jsonify(new_dict)

#     except Exception as e:
#         print(f"Ayyy: {e}")
#         return jsonify({"error": "Internal server error"}), 500


### REPORT GENERATION ###
# @app.post("/get_kolesa_report")
# def get_kolesa_report():
#     try:

#         data = request.json.get('data', {})

#         image_base64 = generate_report_for_a_car(
#             data['car_title'],
#             data['generation'],
#             data['engine_displacement'],
#             data['distance run (km)'],
#             data['N-wheel drive'],
#             data['price'],
#             data['gas_mileage'],
#             data['effect_index_numeric'],
#         )

#         new_dict = {'report_image': image_base64}
#         return jsonify(new_dict)

#     except Exception as e:
#         print(f"Ayyy: {e}")
#         return jsonify({"error": "Internal server error"}), 500
