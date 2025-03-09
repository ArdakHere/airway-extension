
from http.client import HTTPException
import os
import requests
import json
import logging
from src.services.utils import get_apt_eco_index, get_car_eco_index, get_object_count, access_metrics
from src.validation.schema import FindObjectModel, CarListingData, AptListingData, AptListingResponse, CarListingResponse


two_gis_key = os.getenv('TWOGIS_API_KEY')


def get_apt_eco_data(data: AptListingData):
    try:  # error is here in the try block
        
        eco_data = access_metrics(data.coords)

        # parks = get_object_count(
        #     FindObjectModel(
        #         coords=new_coords,
        #         radius=800,
        #         object_to_search="парк"
        #     )
        # )

        # ev_chargers = get_object_count(
        #     FindObjectModel(
        #         coords=new_coords,
        #         radius=500,
        #         object_to_search="зарядка для автомобиля"
        #     )
        # )

        ## missing the numeric number of aq
        eco_data.update({
            "num_of_parks": 2,
            "num_of_ev_chargers": 2})
        print(eco_data)
        return AptListingResponse(
            pm25=eco_data['pm25'],
            pm10=eco_data['pm10'],
            co=eco_data['co'],
            aq_index_numeric=eco_data['aq_index_numeric'],
            aq_index_color=eco_data['aq_index_color'],
            color_pm25=eco_data['color_pm25'],
            color_pm10=eco_data['color_pm10'],
            color_co=eco_data['color_co'],
            num_of_parks=eco_data['num_of_parks'],
            num_of_ev_chargers=eco_data['num_of_ev_chargers']
        )

    except Exception as e:
        print(f"Error: {e}")
    

def get_car_eco_data(data: CarListingData):
    
    try:
        # all the functionality has to be in a separate utils fil
        
        # We are not going to use LLM so these function calls are to be removed
        # car_emission_and_recs_tuple = request_metrics_and_recommendations(car_data)
        # car_emission_data = car_emission_and_recs_tuple[0]

        # use single кавычки
        # fuel_efficiency = car_emission_data['Gas expenditure']
        # co2_val = car_emission_data['CO2']
        fuel_efficiency = 5

        car_recommendations_ev_nonev, nonev_recs, ev_recs = get_car_recommendations(car_data['price'])

        # fuel_efficiency = extract_gas_mileage(gas_mileage)
        # co2_val_number = extract_co2_emissions(co2_val)

        ecofriendly_index_car = ((fuel_efficiency * 10) + co2_val_number) / 1000
        effect_index_numeric = ecofriendly_index_car

        index_and_color_data = get_car_eco_index(eco_index=ecofriendly_index_car)


        return CarListingResponse(
            fuel_efficiency=fuel_efficiency, 
            effect_index=index_and_color_data['qualitativeIndex'],
            effect_index_numeric=effect_index_numeric,
            rgbColor=index_and_color_data['rgbColor'],
            ev_car_recs=ev_recs,
            nonev_car_recs=nonev_recs
        )
    
    except Exception as e:
        print(f"Error: {e}")
    
