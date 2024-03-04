from datetime import timedelta
from os import environ

from requests_cache import CachedSession


class SafpisAPI:
    """This is a class for interacting with the SAFPIS REST API."""

    def __init__(self) -> None:
        """Constructor method"""
        self.base_url = "https://" "fppdirectapi-prod.safuelpricinginformation.com.au"
        self.__country_id = 21  # 21 = Australia
        self.__geo_region_level = 3  # 3 = States
        self.__geo_region_id = 4  # 4 = South Australia

        try:
            subscriber_token = environ.get("SAFPIS_SUBSCRIBER_TOKEN")
            if not subscriber_token:
                raise APIKeyMissingError
        except KeyError as exc:
            raise APIKeyMissingError from exc

        self.__token = subscriber_token

        self.cached_session_day = CachedSession(
            "safpis_cache_day",
            use_cache_dir=True,
            cache_control=True,
            expire_after=timedelta(days=1),
            allowable_codes=[200, 400],
            allowable_methods=["GET"],
            stale_if_error=False,
        )

        self.cached_session_minute = CachedSession(
            "safpis_cache_minute",
            use_cache_dir=True,
            cache_control=True,
            expire_after=timedelta(minutes=1),
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

    def GetCountryBrands(self, countryId: int = 21):
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

    def GetCountryGeographicRegions(self, countryId: int = 21):
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

    def GetCountryFuelTypes(self, countryId: int = 21):
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

    def GetFullSiteDetails(
        self,
        countryId: int = 21,
        GeoRegionLevel: int = 3,
        GeoRegionId: int = 4,
    ):
        """Sends a request to the GetFullSiteDetails endpoint, caching
        responses for a day.

        :param countryId: The ID of the country for which fuel station details
                are being requested, defaults to 21 (Australia).
        :type countryId: int
        :param GeoRegionLevel: The level of the geographic region for which
                fuel station details are being requested, defaults to 3 (states).
        :type GeoRegionLevel: int
        :param GeoRegionId: The ID of the geographic region for which fuel
                station details are being requested, defaults to 4 (South
                Australia).
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

    def GetSitesPrices(
        self,
        countryId: int = 21,
        GeoRegionLevel: int = 3,
        GeoRegionId: int = 4,
    ):
        """Sends a request to the GetSitesPrices endpoint, caching
        responses for a minute.

        :param countryId: The ID of the country for which fuel station prices
                are being requested, defaults to 21 (Australia).
        :type countryId: int
        :param GeoRegionLevel: The level of the geographic region for which
                fuel station prices are being requested, defaults to 3 (states).
        :type GeoRegionLevel: int
        :param GeoRegionId: The ID of the geographic region for which fuel
                station prices are being requested, defaults to 4 (South
                Australia).
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


class APIKeyMissingError(Exception):
    """Exception for a missing SAFPIS Subscriber Token.

    The SAFPIS Subscriber Token should be specified in the environmental
    variable 'SAFPIS_SUBSCRIBER_TOKEN'.
    """

    def __init__(self) -> None:
        super().__init__("Environmental variable SAFPIS_SUBSCRIBER_TOKEN is missing.")
