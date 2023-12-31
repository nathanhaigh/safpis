import os
import requests_cache
import datetime
from safpis.models import Brand, Fuel, Site, SitePrice
from geopy.distance import Distance


class SafpisAPI:
    """This is a class for interacting with the SAFPIS REST API."""

    def __init__(self) -> None:
        """Constructor method"""
        self.base_url = (
            "https://" "fppdirectapi-prod.safuelpricinginformation.com.au"
        )
        self.__country_id = 21  # 21 = Australia
        self.__geo_region_level = 3  # 3 = States
        self.__geo_region_id = 4  # 4 = South Australia

        try:
            subscriber_token = os.environ.get("SAFPIS_SUBSCRIBER_TOKEN")
            if not subscriber_token:
                raise APIKeyMissing(
                    "Environmental variable SAFPIS_SUBSCRIBER_TOKEN is set "
                    "but empty."
                )
        except KeyError:
            raise APIKeyMissing(
                "Environmental variable SAFPIS_SUBSCRIBER_TOKEN is not set."
            )

        self.__token = subscriber_token

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
            "Authorization": f"FPDAPI SubscriberToken={self.__token}",
        }

    def __call_api(self, url: str, params: dict, cache: str = "day"):
        """Dispatches requests to the SAFPIS REST API, caching responses to
        avoid undue load on the service as required by the SAFPIS API (OUT)
        Guide.

        :param url: The path and endpoint for the request.
        :type url: str
        :param params: Request Parameters.
        :type params: dict
        :param cache: The cache used for the request, defaults to 'day'.  It
             can be 'day' or 'minute'.
        :type cache: str
        :raises ValueError: if :param cache: value is not recognised.
        :raises HTTPError: if the HTTP response is a 4XX client or 5XX server
            error response.
        :return: The request response.
        :rtype: requests.Response
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
        elif cache == "minute":
            response = self.cached_session_minute.get(
                url,
                headers=self.headers,
                params=params,
            )

        response.raise_for_status()

        return response

    def get_country_brands(self, countryId: int = 21):
        """Sends a request to the GetCountryBrands endpoint, caching responses
        for a day.

        :param countryId: The ID of the country for which fuel brands are being
            requested, defaults to 21 (Australia).
        :type countryId: int
        :return: The json-encoded content of the response.
        """
        url = f"{self.base_url}/Subscriber/GetCountryBrands"
        params = {"countryId": countryId}

        response = self.__call_api(
            url,
            params=params,
        )

        return response.json()

    def get_country_geographic_regions(self, countryId: int = 21):
        """Sends a request to the GetCountryGeographicRegions endpoint, caching
        responses for a day.

        :param countryId: The ID of the country for which geographic regions
            are being requested, defaults to 21 (Australia).
        :type countryId: int
        :return: The json-encoded content of the response.
        """
        url = f"{self.base_url}/Subscriber/GetCountryGeographicRegions"
        params = {"countryId": countryId}

        response = self.__call_api(
            url,
            params=params,
        )

        return response.json()

    def get_country_fuel_types(self, countryId: int = 21):
        """Sends a request to the GetCountryFuelTypes endpoint, caching
        responses for a day.

        :param countryId: The ID of the country for which fuel types are being
            requested, defaults to 21 (Australia).
        :type countryId: int
        :return: The json-encoded content of the response.
        """
        url = f"{self.base_url}/Subscriber/GetCountryFuelTypes"
        params = {"countryId": countryId}

        response = self.__call_api(
            url,
            params=params,
        )

        return response.json()

    def get_full_site_details(
        self,
        countryId: int = 21,
        GeoRegionLevel: int = 3,
        GeoRegionId: int = 4,
    ):
        """Sends a request to the GetFullSiteDetails endpoint, caching
        responses for a day.

        :param countryId: The ID of the country for which site details are
            being requested, defaults to 21 (Australia).
        :type countryId: int
        :param GeoRegionLevel: The level of the geographic region for which
            site details are being requested, defaults to 3 (states).
        :type GeoRegionLevel: int
        :param GeoRegionId: The ID of the geographic region for which site
            details are being requested, defaults to 4 (South Australia).
        :type GeoRegionId: int
        :return: The json-encoded content of the response.
        """
        url = f"{self.base_url}/Subscriber/GetFullSiteDetails"
        params = {
            "countryId": countryId,
            "geoRegionLevel": GeoRegionLevel,
            "geoRegionId": GeoRegionId,
        }

        response = self.__call_api(
            url,
            params=params,
        )

        return response.json()

    def get_sites_prices(
        self,
        countryId: int = 21,
        GeoRegionLevel: int = 3,
        GeoRegionId: int = 4,
    ):
        """Sends a request to the GetSitesPrices endpoint, caching
        responses for a minute.

        :param countryId: The ID of the country for which site prices are
            being requested, defaults to 21 (Australia).
        :type countryId: int
        :param GeoRegionLevel: The level of the geographic region for which
            site prices are being requested, defaults to 3 (states).
        :type GeoRegionLevel: int
        :param GeoRegionId: The ID of the geographic region for which site
            prices are being requested, defaults to 4 (South Australia).
        :type GeoRegionId: int
        :return: The json-encoded content of the response.
        """
        url = f"{self.base_url}/Price/GetSitesPrices"
        params = {
            "countryId": countryId,
            "geoRegionLevel": GeoRegionLevel,
            "geoRegionId": GeoRegionId,
        }

        response = self.__call_api(
            url,
            params=params,
            cache="minute",
        )

        return response.json()

    def brands_by_id(self, id: int):
        brands = [
            Brand(**brand)
            for brand in self.get_country_brands()["Brands"]
            if brand["BrandId"] == id
        ]
        if not brands:
            raise ValueError(f"No brand found for id: {id}")
        return brands

    def brands_by_name(self, name: str):
        brands = [
            Brand(**brand)
            for brand in self.get_country_brands()["Brands"]
            if brand["Name"] == name
        ]
        if not brands:
            raise ValueError(f"No brand found for name: {name}")
        return brands

    def fuels_by_id(self, id: int):
        fuels = [
            Fuel(**fuel)
            for fuel in self.get_country_fuel_types()["Fuels"]
            if fuel["FuelId"] == id
        ]
        if not fuels:
            raise ValueError(f"No fuel type found for id: {id}")
        return fuels

    def fuels_by_name(self, name: str):
        fuels = [
            Fuel(**fuel)
            for fuel in self.get_country_fuel_types()["Fuels"]
            if fuel["Name"] == name
        ]
        if not fuels:
            raise ValueError(f"No fuel type found for name: {name}")
        return fuels

    def sites_by_id(self, id: int):
        sites = [
            Site(**site)
            for site in self.get_full_site_details()["S"]
            if site["S"] == id
        ]
        if not sites:
            raise ValueError(f"No sites found for id: {id}")
        return sites

    def sites_by_name(self, name: str):
        sites = [
            Site(**site)
            for site in self.get_full_site_details()["S"]
            if site["N"] == name
        ]
        if not sites:
            raise ValueError(f"No sites found for name: {name}")
        return sites

    def sites_by_distance(
        self, latitude: float, longitude: float, max_distance: Distance
    ):
        sites = [Site(**site) for site in self.get_full_site_details()["S"]]
        filtered_sites = filter(
            lambda site: site.distance_between(latitude, longitude)
            <= max_distance,
            sites,
        )
        sorted_sites = sorted(
            filtered_sites,
            key=lambda site: site.distance_between(latitude, longitude),
        )

        return sorted_sites

    def sites_open(self, datetime: datetime):
        sites = [Site(**site) for site in self.get_full_site_details()["S"]]
        filtered_sites = filter(lambda site: site.is_open(datetime), sites)

        return list(filtered_sites)

    def sites_by_cheapest_fuel_type(self, fuel_type: str):
        """
        Function to return a list of sites, ordered by price
        :param fuel_type: Fuel type. Type - str
        :return: List of Site objects
        """
        site_prices = [
            SitePrice(**site_price)
            for site_price in self.get_sites_prices()["SitePrices"]
        ]
        fuel_id = self.fuels_by_name(name=fuel_type)[0].FuelId
        filtered_site_prices = filter(
            lambda site_price: site_price.FuelId == fuel_id,
            site_prices,
        )
        sorted_site_prices = sorted(
            filtered_site_prices,
            key=lambda site_price: site_price.Price.amount,
        )

        return sorted_site_prices


class APIKeyMissing(Exception):
    """Exception for a missing SAFPIS Subscriber Token.

    The SAFPIS Subscriber Token should be specified in the environmental
    variable 'SAFPIS_SUBSCRIBER_TOKEN'.
    """

    pass
