
from pydantic import BaseModel, Field
from enum import Enum

class CoordsModel(BaseModel):
    lat: float = Field(..., ge=0, description="Latitude coordinate")
    lon: float = Field(..., ge=0, description="Longitude coordinate")


class FindObjectModel(BaseModel):
    coords: CoordsModel
    radius: int = Field(..., description="Search radius in meters")
    object_to_search: str = Field(..., min_length=1, max_length=50, description="String value of the object to search for")


class WheelDrive(str, Enum):
    awd = "4wd"
    rwd = "rwd"
    fwd = "fwd"
    
class CarListingData(BaseModel):
    car_title: str = Field(..., description="Brand and model of the car")
    prod_year: str = Field(..., description="Production year")
    engine_displacement: float = Field(..., description="Engine displacement of the car")
    distance_run_km: int = Field(..., description="Distance run in kilometers")
    N_wheel_drive: WheelDrive = Field(..., description="Number of wheels drive")
    price: int = Field(..., description="Price of the car")

class CarListingResponse(BaseModel):
    fuel_efficiency: str = Field(..., description="Gas mileage of the car")
    effect_index: str = Field(..., description="Qualitative index")
    effect_index_numeric: float = Field(..., description="Numeric value of the eco index")
    rgbColor: tuple[int, int, int] = Field(..., description="RGB color code")
    ev_car_recs: str = Field(..., description="Recommendations for electric cars")
    nonev_car_recs: str = Field(..., description="Recommendations for non-electric cars")

# emission_data = {
#     'fuel_efficiency': fuel_efficiency,
#     'effect_index': index_and_color_data['qualitativeIndex'],
#     'effect_index_numeric': effect_index_numeric,
#     'rgbColor': index_and_color_data['rgbColor'],
#     'ev_car_recs': ev_recs,
#     'nonev_car_recs': nonev_recs,
# }

class AptListingData(BaseModel):
    coords: CoordsModel
    location: str = Field(..., description="Location of the apartment (city, settlement, etc.)", max_length=50)
    street: str = Field(..., description="Street of the apartment", max_length=50)
    floor_number: int = Field(..., gt=-1, le=100, description="Floor number of the apartment")
    area: float = Field(..., gt=0, description="Area of the apartment in square meters")
    room_count: int = Field(..., gt=0, description="The amount of rooms in the apartment")
    year_of_construction: int = Field(..., gt=1000, le=2050, description="Year of construction of the apartment") 

class AptListingResponse(BaseModel):
    pm25: float = Field(..., description="PM2.5 value")
    pm10: float = Field(..., description="PM10 value")
    co: float = Field(..., description="CO value")
    aq_index_numeric: float = Field(..., description="Numeric value of the eco index")
    aq_index_color: tuple[int, int, int] = Field(..., description="Color of the eco index")
    color_pm25: tuple[int, int, int] = Field(..., description="Color of the PM2.5 value")
    color_pm10: tuple[int, int, int] = Field(..., description="Color of the PM10 value")
    color_co: tuple[int, int, int] = Field(..., description="Color of the CO value")
    num_of_parks: int = Field(..., description="Number of parks within 800m")
    num_of_ev_chargers: int = Field(..., description="Number of electric car chargers within 500m")

# class QualitativeIndex(str, Enum):
#     dangerous = "Опасный"
#     high = "Высокий"
#     average = "Средний"
#     low = "Низкий"

# class IndexClassification(BaseModel):
#     rgbColor: str = Field(..., description="RGB color code")
#     qualitativeIndex: QualitativeIndex = Field(..., description="Qualitative index")