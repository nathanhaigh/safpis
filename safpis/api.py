import os
import requests_cache
import datetime
from safpis.models import Brand, Region, Fuel, Site, SitePrice


class SafpisAPI:
    def __init__(self) -> None:
        """
        Function to initialise the SAFPIS API Class
        """
        token = os.environ.get("SAFPIS_SUBSCRIBER_TOKEN", None)

        if token is None:
            raise APIKeyMissingError(
                "A Subscriber Token is required. See "
                "https://www.safuelpricinginformation.com.au for information "
                "on registering as a Data Publisher and obtaining a Subscriber "
                "Token."
                "You must set the SAFPIS_SUBSCRIBER_TOKEN environmental "
                "variable value to your Subscriber Token or pass the name of "
                "the environmental variable holding your Subscriber Token "
                "when creating an instance of SafpisAPI."
            )

        self.base_url = "https://fppdirectapi-prod.safuelpricinginformation.com.au"
        self.__country_id = 21  # 21 = Australia
        self.__geo_region_level = 3  # 3 = States
        self.__geo_region_id = 4  # 4 = South Australia

        self.home = (-35.062058, 138.593400)

        self.cached_session_day = requests_cache.CachedSession(
            "safpis_cache_day",
            use_cache_dir=True,
            cache_control=True,
            expire_after=datetime.timedelta(days=1),
            allowable_codes=[200, 400],
            allowable_methods=["GET"],
            stale_if_error=False,
        )

        self.cached_session_minute = requests_cache.CachedSession(
            "safpis_cache_minute",
            use_cache_dir=True,
            cache_control=True,
            expire_after=datetime.timedelta(minutes=1),
            allowable_codes=[200, 400],
            allowable_methods=["GET"],
            stale_if_error=False,
        )

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": f"FPDAPI SubscriberToken={token}",
        }

    def __call_api(self, url: str, params: dict, cache="day"):
        """
        Function to call the API via the requests_cache Library
        :param request_type: Type of Request.
               Supported Values - GET, POST, PUT, PATCH, DELETE.
               Type - String
        :param url: URL of the API Endpoint. Type - String
        :param params: API Request Parameters. Type - String
        :param cache: Cache duration for API responses.
                      Values - day (default) or minute
        :return: Response. Type - Response
        """
        valid_cache = {"day", "minute"}
        if cache not in valid_cache:
            raise ValueError("cache must be one of %r." % valid_cache)

        if cache == "day":
            response = self.cached_session_day.get(
                url,
                headers=self.headers,
                params=params,
            )
        elif cache == "hour":
            response = self.cached_session_hour.get(
                url,
                headers=self.headers,
                params=params,
            )

        return response

    def brands(self):
        """
        Function to return a list of fuel brands.
        :return: Response. Type - Response
        """
        url = f"{self.base_url}/Subscriber/GetCountryBrands"
        params = {"countryId": self.__country_id}

        response = self.__call_api(
            url,
            params=params,
        )

        brand_list = [Brand(**brand) for brand in response.json()["Brands"]]

        return brand_list

    def regions(self):
        """
        Function to return a list of suburbs, cities and states
        :return: Response. Type - Response
        """
        url = f"{self.base_url}/Subscriber/GetCountryGeographicRegions"
        params = {"countryId": self.__country_id}

        response = self.__call_api(
            url,
            params=params,
        )

        region_list = [
            Region(**region) for region in response.json()["GeographicRegions"]
        ]

        return region_list

    def fuel_types(self):
        """
        Function to return a list of fuel types
        :return: Response. Type - Response
        """
        url = f"{self.base_url}/Subscriber/GetCountryFuelTypes"
        params = {"countryId": self.__country_id}

        response = self.__call_api(
            url,
            params=params,
        )

        fuel_type_list = [Fuel(**fuel_type) for fuel_type in response.json()["Fuels"]]

        return fuel_type_list

    def sites(self):
        """
        Function to return a list of sites
        :return: Response. Type - Response
        """
        url = f"{self.base_url}/Subscriber/GetFullSiteDetails"
        params = {
            "countryId": self.__country_id,
            "geoRegionLevel": self.__geo_region_level,
            "geoRegionId": self.__geo_region_id,
        }

        response = self.__call_api(
            url,
            params=params,
        )

        site_list = [Site(**site) for site in response.json()["S"]]

        return site_list

    def site_prices(self):
        """
        Function to return a list of fuel prices for all sites
        :return: Response. Type - Response
        """
        url = f"{self.base_url}/Price/GetSitesPrices"
        params = {
            "countryId": self.__country_id,
            "geoRegionLevel": self.__geo_region_level,
            "geoRegionId": self.__geo_region_id,
        }

        response = self.__call_api(
            url,
            params=params,
        )

        site_price_list = [
            SitePrice(**site_price) for site_price in response.json()["SitePrices"]
        ]

        return site_price_list

    def sites_by_nearest(self, lat: float, lng: float, n: int = None):
        """
        Function to return a list of sites, ordered by distance
        :param lat: Latitude. Type - float
        :param lng: Longitude. Type - float
        :param n: Number of sites to return. Type - int
        :return: List of Site objects
        """
        sites = self.sites() if n is None else self.sites()[:n]

        sorted_sites = sorted(sites, key=lambda site: site.distance_between(lat, lng))

        return sorted_sites

    def sites_by_cheapest_fuel(self, fuel_type: str, n: int = None):
        """
        Function to return a list of sites, ordered by price
        :param fuel_type: Fuel type. Type - str
        :param lng: Longitude. Type - float
        :param n: Number of sites to return. Type - int
        :return: List of Site objects
        """
        valid_fuel_types = [item.name for item in self.fuel_types()]
        if fuel_type not in valid_fuel_types:
            raise ValueError("fuel_type must be one of %r." % valid_fuel_types)

        fuel_type_id = [item.id for item in self.fuel_types() if item.name == fuel_type]

        site_prices = [
            item for item in self.site_prices() if item.fuel_id in fuel_type_id
        ]

        sorted_site_prices = sorted(
            site_prices, key=lambda site_price: site_price.price.amount
        )

        return sorted_site_prices


class APIKeyMissingError(Exception):
    pass
