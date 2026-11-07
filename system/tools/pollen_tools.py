from pydantic import BaseModel, ConfigDict
from pydantic_ai import FunctionToolset
import requests
from functools import cache
import datetime
from geopy.distance import distance


pollen_tools = FunctionToolset()


API_ROOT = "https://api.pollenrapporten.se/v1"


class Region(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    longitude: str
    latitude: str


class PollenType(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    hasPollenCounts: bool
    hasForecasts: bool
    thresholdLow: int
    thresholdMedium: int
    thresholdHigh: int
    thresholdVeryHigh: int


class PollenCount(BaseModel):
    model_config = ConfigDict(extra="ignore")

    region: str
    pollen: str
    date: str
    dailyCount: int
    technicalError: bool


@cache
def api_fetch_all(endpoint, params=frozenset([]), api_root=API_ROOT):
    params = dict(params)
    url = f"{api_root}/{endpoint}"
    return list(fetch_all(url, params=params))


def fetch_all(url, params={}):
    response = requests.get(url, params=params)
    while response is not None:
        response.raise_for_status()
        data = response.json()
        for item in data["items"]:
            yield item

        next_url = next(
            (
                link["href"]
                for link in data["_links"]
                if link["rel"] == "next"
            ),
            None
        )
        response = (
            None
            if next_url is None
            else requests.get(next_url)
        )


def get_by_name(items, name):
    item = next((item for item in items if item["name"].lower() == name.lower()), None)
    return item


@pollen_tools.tool_plain
def get_regions() -> list[str]:
    """Gets all the currently available regions

    Returns:
        A list of all currently available regions represented as a list of strings containing regions names
    """
    regions = api_fetch_all("regions")
    return [
        region["name"]
        for region in regions
    ]


@pollen_tools.tool_plain
def get_region_info(region_name: str) -> Region:
    """Gets information related to a region by name

    Args:
        region_name (str): A string with the name of a region

    Returns:
        The available information about the specified region as a dict with the keys:
        - 'name' (str): The name of the location.
        - 'longitude' (float): The longitude of the location, measured in decimal degrees.
        - 'latitude' (float): The latitude of the location, measured in decimal degrees.
    """

    print(f"Get region: {region_name}")
    regions = api_fetch_all("regions")
    return Region.model_validate(get_by_name(regions, region_name))


@pollen_tools.tool_plain
def get_pollen_types() -> list[str]:
    """Gets all the currently available pollen types

    Returns:
        A list of all currently available pollen types represented as a list of strings containing pollen type names
    """
    pollen_types = api_fetch_all("pollen-types")
    return [
        pollen_type["name"]
        for pollen_type in pollen_types
    ]


@pollen_tools.tool_plain
def get_pollen_info(pollen_name: str) -> PollenType:
    """Gets information related to a pollen type by name

    Returns:
        The available information about the specified pollen type as a dict with the keys:
        - 'name' (str): The name of the pollen type.
        - 'thresholdLow' (int): Threshold for low impact on allergies
        - 'thresholdMedium' (int): Threshold for medium impact on allergies
        - 'thresholdHigh' (int): Threshold for high impact on allergies
        - 'thresholdVeryHigh' (int): Threshold for very high impact on allergies
    """

    pollen_types = api_fetch_all("pollen-types")
    return PollenType.model_validate(get_by_name(pollen_types, pollen_name))


@pollen_tools.tool_plain
def get_pollen_count(region_name: str, pollen_name: str, date: datetime.date | str) -> PollenCount | None:
    """Gets the pollen count for a given region, pollen and date

    Args:
        region_name (str): A string with the name of a region
        pollen_name (str): A string with the name of a pollen type
        date (datetime.date | str): A date object or an isoformated date string

    Returns:
        The pollen count for the given region, pollen and date as a dict with the keys:
        - 'pollen' (str): The pollen name
        - 'region' (str): The region name
        - 'dailyCount' (int): The number of counted pollen particles
        - 'technicalError' (boolean): Indication if there was a technical error on the specified day
        - 'date': The date as an isoformatted string

        The result is None when there was no data measured for the given properties.
    """

    region = get_by_name(api_fetch_all("regions"), region_name)
    pollen_type = get_by_name(api_fetch_all("pollen-types"), pollen_name)

    if not region or not pollen_type:
        return None

    date_str = date if isinstance(date, str) else date.isoformat()
    pollen_count = api_fetch_all(
        "pollen-count",
        params=frozenset({
            "region_id": region["id"],
            "pollen_id": pollen_type["id"],
            "start_date": date_str,
            "end_date": date_str
        }.items())
    )
    if len(pollen_count) > 0:
        data = pollen_count[0]
        data.pop("countDescription")
        data.pop("pollenId")
        data.pop("regionId")
        data["region"] = region_name
        data["pollen"] = pollen_name
        return PollenCount.model_validate(data)
    else:
        return None


@pollen_tools.tool_plain
def get_distance(coord_a: tuple[float, float], coord_b: tuple[float, float]) -> float:
    """Gets the distance between two geographic coordinates in meters

    Args:
        coord_a: A tuple containing longitude and latitude
        coord_b: A tuple containing longitude and latitude

    Returns:
      The distance between the input coordinates in meters
    """
    return distance(coord_a, coord_b).meters


@pollen_tools.tool_plain
def get_date() -> datetime.date:
    """Gets the current date as an isoformat string

    Returns:
      The current date as an isoformat string
    """
    return datetime.date.today()


@pollen_tools.tool_plain
def get_time() -> datetime.datetime:
    """Gets the current date and time as an isoformat string

    Returns:
      The current date and time as an isoformat string
    """
    return datetime.datetime


@pollen_tools.tool_plain
def interpolate_value(start_value: float, end_value: float, distance: float, position: float) -> float:
    """Gets a linearly interpolated value based on start_value and end_value, where the returned value is start_value when position is 0 and the value is end_value when the position == distance.

    Args:
        'start_value' (float): The start value
        'end_value' (float): The end value
        'distance' (float): The range maximum
        'position' (float): A value between 0 and 'distance' used to interpolate 'start_value' and 'end_value'

    Returns:
        The linearly interpolated value between start_value and end_value over the range from 0 to distance where position is a value within the range.
    """
    start_value = float(start_value)
    end_value = float(end_value)
    distance = float(distance)
    position = min(max(0, float(position)), distance)

    t = position / distance
    return t * end_value + (1 - t) * start_value