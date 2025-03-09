
from http.client import HTTPException
import os
import requests
import json
import logging
from src.services.utils import get_apt_eco_index, get_car_eco_index, get_object_count, access_metrics, get_car_recommendations
from src.validation.schema import FindObjectModel, CarListingData, AptListingData, AptListingResponse, CarListingResponse


two_gis_key = os.getenv('TWOGIS_API_KEY')


def get_apt_eco_data(data: AptListingData):
    """
        Get the eco data for an apartment
    \n**Args**:
        AptListingData model
    \n**Returns**:
        AptListingResponse model
    """
    try:  # error is here in the try block
        
        eco_data = access_metrics(data.coords)

        # parks = get_object_count(
        #     FindObjectModel(
        #         coords=data.coords,
        #         radius=800,
        #         object_to_search="парк"
        #     )
        # )
        parks = 1
        # ev_chargers = get_object_count(
        #     FindObjectModel(
        #         coords=data.coords,
        #         radius=500,
        #         object_to_search="зарядка для автомобиля"
        #     )
        # )
        ev_chargers = 1

        return AptListingResponse(
            pm25=eco_data['pm25'],
            pm10=eco_data['pm10'],
            co=eco_data['co'],
            aq_index_numeric=eco_data['aq_index_numeric'],
            aq_index_color=eco_data['aq_index_color'],
            color_pm25=eco_data['color_pm25'],
            color_pm10=eco_data['color_pm10'],
            color_co=eco_data['color_co'],
            num_of_parks=parks,
            num_of_ev_chargers=ev_chargers
        )

    except Exception as e:
        print(f"Error: {e}")
    

def get_car_eco_data(data: CarListingData) -> CarListingResponse:
    """
        Get the eco data for a car
    \n**Args**:
        CarListingData model
    \n**Returns**:
        CarListingResponse model
    """
    try:
      
        fuel_efficiency = 5 # To be replaced with real values

        nonev_recs, ev_recs = get_car_recommendations(data.price)

        # fuel_efficiency = extract_gas_mileage(gas_mileage)
        # co2_val_number = extract_co2_emissions(co2_val)

        co2_val_number = 5 # To be replaced with real values
        eco_index_numeric = ((fuel_efficiency * 10) + co2_val_number) / 1000

        index_and_color_data = get_car_eco_index(eco_index=eco_index_numeric)

        return CarListingResponse(
            fuel_efficiency=fuel_efficiency, 
            effect_index=index_and_color_data['qualitativeIndex'],
            effect_index_numeric=eco_index_numeric,
            rgbColor=index_and_color_data['rgbColor'],
            ev_car_recs=ev_recs,
            nonev_car_recs=nonev_recs
        )
    
    except Exception as e:
        print(f"Error: {e}")
    
