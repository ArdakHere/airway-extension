import logging
import os
import csv
import requests
import pandas as pd
from pandas import DataFrame
from math import radians, sin, cos, sqrt, atan2

## absolute path is used, the relative path does not work for some reason 
df_sergek = pd.read_csv("./src/datasets/lean_sergek_aq_dataset.csv")
two_gis_key = os.getenv('TWOGIS_API_KEY')


def find_closest_sensor(
    sensor_locations: DataFrame,
    apartment_location: dict
) -> dict:
    """
        Find the closest sensor to the apartment
    \n**Args**:
        sensor_locations (DataFrame): DataFrame with sensor locations
        apartment_location (CoordsModel): CoordsModel with apartment location

    \n**Returns**:
        closest_sensor (dict): dict containing corresponding data
        of the closest sensor
            - location_id (int): location id of the sensor
            - pm25 (float): PM2.5 value of the sensor
            - pm10 (float): PM10 value of the sensor
            - co (float): CO value of the sensor
            - lat (float): latitude of the sensor
            - lon (float): longitude of the sensor
    """
    closest_sensor = None
    min_distance_from_sensor_to_apartment = float('inf')

    for _, sensor_location in sensor_locations.iterrows():

        distance = calculate_haversine(
            float(apartment_location.lat),
            float(apartment_location.lon),
            float(sensor_location['lat']),
            float(sensor_location['lon']))
        if distance < min_distance_from_sensor_to_apartment:
            min_distance_from_sensor_to_apartment = distance
            closest_sensor = sensor_location
    
    return closest_sensor


def calculate_haversine(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
    **Args**:
        lat1 (float): latitude of the apartment
        lon1 (float): longitude of the apartment
        lat2 (float): latitude of the given sensor
        lon2 (float): longitude of the given sensor
    **Returns**:
        distance_to_closest_sensor (float): distance between two points in kilometers
    """

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance_to_closest_sensor = 6371 * c

    return distance_to_closest_sensor


def calculate_air_quality_index(metrics_data: dict) -> dict:
    """
        Calculate the air quality index based on the air quality metrics
    **Args**:
        metrics_data (dict): dict containing corresponding data
        of the closest sensor
            - location_id (int): location id of the sensor
            - pm25 (float): PM2.5 value of the sensor
            - pm10 (float): PM10 value of the sensor
            - co (float): CO value of the sensor
            - lat (float): latitude of the sensor
            - lon (float): longitude of the sensor
    **Returns**:
        index_color_data (dict): dictionary with air quality index and color
            - pm25 (float): PM2.5 value
            - pm10 (float): PM10 value
            - co (float): CO value
            - aq_index_numeric (float): numeric value of the eco index
            - aq_index_color (tuple[int, int, int]): color of the eco index
            - color_pm25 (tuple[int, int, int]): color of the PM2.5 value
            - color_pm10 (tuple[int, int, int]): color of the PM10 value
            - color_co (tuple[int, int, int]): color of the CO value
    """
    aq_index = 0
    pm25_weight = 0.5
    pm10_weight = 0.3
    co_weight = 0.2
    
    aq_index = round(get_weighted_aq_index(metrics_data), 1)

    index_color_data = {
        "pm25": round(float(metrics_data["pm25"]), 1),
        "pm10": round(float(metrics_data["pm10"]), 1),
        "co": round(float(metrics_data["co"]), 1),
        "aq_index_numeric": aq_index,
        "aq_index_color": get_particle_color(aq_index),
        "color_pm25": get_particle_color(float(metrics_data["pm25"])),
        "color_pm10": get_particle_color(float(metrics_data["pm10"])),
        "color_co": get_particle_color(float(metrics_data["co"]))
    }

    return index_color_data


def get_weighted_aq_index(metrics: dict) -> float:
    """
        Calculate the weighted air quality index based on
        the weights
    **Args**:
        metrics (dict): dict containing the following keys:
            - pm25 (float): PM2.5 value
            - pm10 (float): PM10 value
            - co (float): CO value
    **Returns**:
        weighted_aq_index (float): weighted air quality index
    """
    pm25_weight = 0.5
    pm10_weight = 0.3
    co_weight = 0.2
    weighted_aq_index = pm25_weight * metrics['pm25'] + pm10_weight * metrics['pm10'] + co_weight * metrics['co']

    return weighted_aq_index


def get_particle_color(particle_val: float) -> tuple:
    """
        Returns the color based on the particle value
    **Args**:
        particle_val (float): particle value
    **Returns**:
        tuple: RGB color code
    """
    if particle_val >= 100:
        return (255, 119, 0)
    if particle_val >= 85:
        return (255, 189, 55)
    if particle_val >= 45 and particle_val < 85:
        return (255, 224, 18)
    if particle_val < 30:
        return (67, 166, 0)
    if particle_val >= 30 and particle_val < 45:
        return (161, 219, 0)


# ecofriendly_index_car = ((gas_mileage_number * 10) + co2_val_number) / 1000
def get_car_eco_index(eco_index: float) -> dict:
    """
        Returns the dict with color and qualitative index corresponding
        to the eco index 
    Args:
        eco_index (float): eco index
    Returns:
        dict: dictionary with the following
            - rgbColor (tuple[int, int, int]): RGB color code
            - qualitativeIndex (str): qualitative index
    """
    if eco_index >= 0.5:
        rgbColor = (131, 0, 0)
        effect_index = "Опасное"
    elif 0.3 <= eco_index < 0.5:
        rgbColor = (255, 225, 20)
        effect_index = "Высокое"
    elif 0.2 <= eco_index < 0.3:
        rgbColor = (198, 239, 86)
        effect_index = "Среднее"
    elif 0 <= eco_index < 0.2:
        rgbColor = (27, 152, 3)
        effect_index = "Низкое"
    else:
        raise ValueError("eco_index must be between 0 and 1")

    return {"rgbColor": rgbColor, "qualitativeIndex": effect_index}


def get_apt_eco_index(eco_index: float) -> str:
    """
        Returns the qualitative index corresponding to the eco index 
    Args:
        eco_index (float): eco index
    Returns:
        str: qualitative index
    """
    if eco_index <= 40:
        return "Не несет риска, воздух чист"
    elif 50 >= eco_index > 40:
        return "Минимальное"
    elif 70 >= eco_index > 50:
        return "Средняя"
    elif 80 >= eco_index > 70:
        return "Повышенная"
    elif 90 > eco_index > 80:
        return "Высокая"
    elif eco_index >= 90:
        return "Опасная"
    else:
        raise ValueError("eco_index must be between 0 and 1")
    

def get_object_count(
        data: dict
) -> int:
    """
        Return the number of objects found within the radius by 2GIS API
    **Args**:
        data (dict): containing the following keys:
            - coords (CoordsModel): containing the following keys:
                - lat: (float): latitude
                - lon (float): longitude
            - radius (int): radius in meters
            - object_to_search (str): object to search for
    **Returns**:
        total (int): total count of objects found within the radius
    """

    if not two_gis_key:
        logging.error("2GIS API key not found!")
        raise HTTPException(status_code=500, detail="Internal Server Error: Missing API Key")

    coords = data.get('coords')
    radius = data.get('radius')
    object_to_search = data.get('object_to_search')

    location = f"{coords['lon']}%2C{coords['lat']}"

    object_type = ""

    base_url = f"https://catalog.api.2gis.com/3.0/items?q={object_to_search}&point={location}&radius={radius}&type={object_type}&key={two_gis_key}"  # noqa: E501

    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            if "result" in response_data:
                if response_data["result"]["total"]:
                    total = response_data["result"]["total"]
                    return total
                else:                       ## refactor this why such a big if-else statement: 57-60
                    total = len(response_data["result"])
                    return total
            else:
                total = 0
                return total
        elif response.status_code == 404:
            logging.info("No objects found")
            total = 0
            return total
        elif response.status_code == 403:
            logging.error("Forbidden: Access denied")
            raise HTTPException(status_code=403, detail="Forbidden: Access denied")
        else:
            logging.error(f"Unexpected error from API: {response.status_code}")
            raise HTTPException(status_code=500, detail="Unexpected error from API")
    ## refactor exceptions! why so many exceptions?
    except requests.Timeout:
        logging.error("Request timed out")
        raise HTTPException(status_code=504, detail="Gateway Timeout: External API did not respond in time")
    except requests.RequestException as e:
        logging.error(f"Network error: {str(e)}")
        raise HTTPException(status_code=502, detail="Bad Gateway: Network error when calling external API")
    except json.JSONDecodeError:
        logging.error("Failed to parse API response")
        raise HTTPException(status_code=500, detail="Internal Server Error: Invalid response from external API")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def access_metrics(coords: dict) -> dict:
    """
        Returns the key metrics of the air quality based on the coordinates
    **Args**:
        coords (CoordsModel), containing the following keys:
            - lat (float): latitude
            - lon: (float): longitude
    **Returns**:
        calculated_index_dict (dict): dictionary with the following
            - pm25 (float): PM2.5 value
            - pm10 (float): PM10 value
            - co (float): CO value
            - aq_index_numeric (float): numeric value of the eco index
            - aq_index_color (tuple[int, int, int]): color of the eco index
            - color_pm25 (tuple[int, int, int]): color of the PM2.5 value
            - color_pm10 (tuple[int, int, int]): color of the PM10 value
            - color_co (tuple[int, int, int]): color of the CO value
    """

    sensor_locations_df = pd.DataFrame(df_sergek).iloc[1:]

    closest_sensor = find_closest_sensor(sensor_locations_df, coords)
    closest_sensor_dict = closest_sensor.to_dict()

    calculated_index_dict = calculate_air_quality_index(closest_sensor_dict)

    return calculated_index_dict


def get_car_recommendations(price: int) -> str:
    """
        Returns the string with similarly priced cars from car_dataset.csv
        based on the price argument
    Args:
        price (int):
    Returns:
        non_ev_recommendations_str (str): simlarly priced non-electric cars
        ev_recommendations_str (str): simlarly priced electric cars
    """
    non_ev_recommendations = []
    ev_recommendations = []

    # Open the CSV file
    with open('./src/assets/datasets/car_dataset.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Iterate through each row in the CSV file
        for row in reader:
            car_price = int(row['price (KZT)'])
            car_brand = row['brand']
            car_model = row['model']
            car_type = row['type']

            if price - 1200000 <= car_price <= price + 1200000:
                # Check if it's an electric or non-electric car
                if car_type == 'non-ev':
                    if len(non_ev_recommendations) < 2:
                        non_ev_recommendations.append(f"{car_brand} {car_model} - {car_price:,} KZT")
                elif car_type == 'ev':
                    if len(ev_recommendations) < 2:
                        ev_recommendations.append(f"{car_brand} {car_model} - {car_price:,} KZT")

            # Break if we have found at least 2 recommendations for both non-ev and ev cars
            if len(non_ev_recommendations) >= 2 and len(ev_recommendations) >= 2:
                break

    # Format the recommendations
    non_ev_recommendations_str = "\n".join(non_ev_recommendations)
    ev_recommendations_str = "\n".join(ev_recommendations)

    return non_ev_recommendations_str, ev_recommendations_str