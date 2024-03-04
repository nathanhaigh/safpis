from __future__ import annotations

from configparser import ConfigParser
from os import environ
from typing import TYPE_CHECKING

from safpis.api import SafpisAPI
from safpis.models import Brand, Fuel, FuelStation, FuelStationPrice

if TYPE_CHECKING:
    from datetime import datetime


class Safpis:
    def __init__(self):
        self.__api = SafpisAPI()
        self.__brands = self._api().GetCountryBrands()["Brands"]
        self.__fuels = self._api().GetCountryFuelTypes()["Fuels"]
        self.__regions = self._api().GetCountryGeographicRegions()["GeographicRegions"]
        self.__fuel_stations = self._api().GetFullSiteDetails()["S"]

    @staticmethod
    def load_token(
        ini: str = "secrets.cfg",
        section: str = "TEST",
        key: str = "SAFPIS_SUBSCRIBER_TOKEN",
    ):
        config = ConfigParser()
        config.read(ini)
        environ["SAFPIS_SUBSCRIBER_TOKEN"] = config[section][key]

    def _api(self):
        return self.__api

    def _brands(self):
        return self.__brands

    def brand_by_id(self, brand_id: int):
        """Gets a Brand object by brand ID.

        :param brand_id: The ID of the brand.
        :type brand_id: int
        :return: A Brand object.
        """
        brands = [Brand(**brand) for brand in self._brands() if brand["BrandId"] == brand_id]
        what = "brand"
        if not brands:
            raise NoResultsError(what, brand_id)
        if len(brands) > 1:
            raise ToManyResultsError(what, brand_id)
        return brands[0]

    def brand_by_name(self, brand_name: str):
        """Gets a Brand object by brand name.

        :param brand_name: The name of the brand.
        :type brand_name: str
        :return: A Brand object.
        """
        brands = [Brand(**brand) for brand in self._brands() if brand["Name"] == brand_name]
        what = "brand"
        if not brands:
            raise NoResultsError(what, brand_name)
        if len(brands) > 1:
            raise ToManyResultsError(what, brand_name)
        return brands[0]

    def _fuels(self):
        return self.__fuels

    def fuel_by_id(self, fuel_id: int):
        """Gets a Fuel object by fuel ID.

        :param fuel_id: The ID of the fuel.
        :type fuel_id: int
        :return: A Fuel object.
        """
        fuels = [Fuel(**fuel) for fuel in self._fuels() if fuel["FuelId"] == fuel_id]
        what = "fuel"
        if not fuels:
            raise NoResultsError(what, fuel_id)
        if len(fuels) > 1:
            raise ToManyResultsError(what, fuel_id)
        return fuels[0]

    def fuel_by_name(self, fuel_name: str):
        """Gets a Fuel object by fuel name.

        :param fuel_name: The name of the brand.
        :type fuel_name: int
        :return: A Brand object.
        """
        fuels = [Fuel(**fuel) for fuel in self._fuels() if fuel["Name"] == fuel_name]
        what = "fuel"
        if not fuels:
            raise NoResultsError(what, fuel_name)
        if len(fuels) > 1:
            raise ToManyResultsError(what, fuel_name)
        return fuels[0]

    def _fuel_stations(self):
        return self.__fuel_stations

    def fuel_station_by_id(self, fuel_station_id: int):
        """Gets a FuelStation object by fuel station ID.

        :param fuel_station_id: The ID of the fuel station.
        :type fuel_station_id: int
        :return: A FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
            if fuel_station["S"] == fuel_station_id
        ]
        what = "fuel station"
        if not fuel_stations:
            raise NoResultsError(what, fuel_station_id)
        if len(fuel_stations) > 1:
            raise ToManyResultsError(what, fuel_station_id)
        return fuel_stations[0]

    def fuel_station_by_name(self, fuel_station_name: str):
        """Gets a FuelStation object by fuel station name.

        :param fuel_station_name: The name of the fuel station.
        :type fuel_station_name: int
        :return: A FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
            if fuel_station["N"] == fuel_station_name
        ]
        what = "fuel station"
        if not fuel_stations:
            raise NoResultsError(what, fuel_station_name)
        if len(fuel_stations) > 1:
            raise ToManyResultsError(what, fuel_station_name)
        return fuel_stations[0]

    def fuel_stations_by_brand_name(self, brand_name: str):
        """Gets a list of FuelStation objects by brand name.

        :param brand_name: The name of the fuel station.
        :type brand_name: int
        :return: A list of FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
            if fuel_station["B"] == self.brand_by_name(brand_name).BrandId
        ]
        what = "fuel station"
        if not fuel_stations:
            raise NoResultsError(what, brand_name)
        return fuel_stations

    def closest_fuel_stations(self, latitude: float, longitude: float):
        """Gets a list of FuelStation objects with associated distances from of
        a latitude/longitude location.

        :param latitude: The latitude from which to measure.
        :type latitude: float
        :param longitude: The longitude from which to measure.
        :type longitude: float
        :return: A list of FuelStation object.
        :rtype: List
        """
        fuel_stations = [FuelStation(**fuel_station) for fuel_station in self._fuel_stations()]
        # filtered_fuel_stations = filter(
        #    lambda fuel_station: fuel_station.distance(latitude, longitude)
        #    <= max_distance,
        #    fuel_stations,
        # )
        return sorted(
            fuel_stations,
            key=lambda fuel_station: fuel_station.distance(latitude, longitude),
        )

    def open_fuel_stations(self, datetime: datetime):
        """Gets a list of FuelStation objects for fuel stations open on the
        requested datetime.

        :param datetime: A datetime object.
        :type datetime: datetime
        :return: A list of FuelStation object.
        """
        fuel_stations = [FuelStation(**fuel_station) for fuel_station in self._fuel_stations()]
        filtered_fuel_stations = filter(lambda fuel_station: fuel_station.is_open(datetime), fuel_stations)

        return list(filtered_fuel_stations)

    def cheapest_fuel_type(self, fuel_name: str):
        """Gets a list of FuelStationPrice objects for a particular fuel.

        :param fuel_name: The name of a fuel type.
        :type fuel_name: str
        :return: A list of FuelStationPrice objects ordered from cheapest to
                costliest.
        :rtype: List
        """
        fuel_station_prices = [
            FuelStationPrice(**fuel_station_price) for fuel_station_price in self._api().GetSitesPrices()["SitePrices"]
        ]
        fuel_id = self.fuel_by_name(fuel_name).FuelId
        filtered_fuel_station_prices = filter(
            lambda fuel_station_price: fuel_station_price.FuelId == fuel_id,
            fuel_station_prices,
        )
        return sorted(
            filtered_fuel_station_prices,
            key=lambda fuel_station_price: fuel_station_price.Price.amount,
        )

    def price(self, fuel_station_id: int, fuel_id: int):
        """Function to return the current price of a particular fuel at a
        particular fuel station.

        :param fuel_station_id: The ID of the fuel station.
        :type fuel_station_id: int
        :param fuel_id: The ID of the fuel type.
        :type fuel_id: int
        :return: The price of the fuel.
        :rtype: Decimal
        """
        fuel_station_prices = [
            FuelStationPrice(**fuel_station_price) for fuel_station_price in self._api().GetSitesPrices()["SitePrices"]
        ]
        filtered_fuel_station_prices = filter(
            lambda fuel_station_price: (
                fuel_station_price.FuelId == fuel_id and fuel_station_price.SiteId == fuel_station_id
            ),
            fuel_station_prices,
        )
        return list(filtered_fuel_station_prices)


class NoResultsError(Exception):
    """Exception raised when no results are returned from the REST API."""

    def __init__(self, what: str, id_: int | str) -> None:
        msg = f"No {what} found for: {id_}"
        super().__init__(msg)


class ToManyResultsError(Exception):
    """Exception raised when too many results are returned from the REST
    API.
    """

    def __init__(self, what: str, id_: int | str) -> None:
        msg = f"More than 1 {what} found for: {id_}"
        super().__init__(msg)
