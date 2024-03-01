from safpis.api import SafpisAPI
from safpis.models import Brand, Fuel, FuelStation, FuelStationPrice
import datetime
import configparser
import os


class Safpis:
    def __init__(self):
        self.__api = SafpisAPI()
        self.__brands = self._api().GetCountryBrands()["Brands"]
        self.__fuels = self._api().GetCountryFuelTypes()["Fuels"]
        self.__regions = self._api().GetCountryGeographicRegions()[
            "GeographicRegions"
        ]
        self.__fuel_stations = self._api().GetFullSiteDetails()["S"]

    @staticmethod
    def load_token(
        ini: str = "secrets.cfg",
        section: str = "TEST",
        key: str = "SAFPIS_SUBSCRIBER_TOKEN",
    ):
        config = configparser.ConfigParser()
        config.read(ini)
        os.environ["SAFPIS_SUBSCRIBER_TOKEN"] = config[section][key]

    def _api(self):
        return self.__api

    def _brands(self):
        return self.__brands

    def brand_by_id(self, id: int):
        """Gets a Brand object by brand ID.

        :param id: The ID of the brand.
        :type id: int
        :return: A Brand object.
        """
        brands = [
            Brand(**brand)
            for brand in self._brands()
            if brand["BrandId"] == id
        ]
        if not brands:
            raise ValueError(f"No brand found for id: {id}")
        if len(brands) > 1:
            raise ValueError(f"More than 1 brand found for id: {id}")
        return brands[0]

    def brand_by_name(self, name: str):
        """Gets a Brand object by brand name.

        :param name: The name of the brand.
        :type name: str
        :return: A Brand object.
        """
        brands = [
            Brand(**brand) for brand in self._brands() if brand["Name"] == name
        ]
        if not brands:
            raise ValueError(f"No brand found for name: {name}")
        if len(brands) > 1:
            raise ValueError(f"More than 1 brand found for name: {name}")
        return brands[0]

    def _fuels(self):
        return self.__fuels

    def fuel_by_id(self, id: int):
        """Gets a Fuel object by fuel ID.

        :param id: The ID of the fuel.
        :type id: int
        :return: A Fuel object.
        """
        fuels = [
            Fuel(**fuel) for fuel in self._fuels() if fuel["FuelId"] == id
        ]
        if not fuels:
            raise ValueError(f"No fuel type found for id: {id}")
        if len(fuels) > 1:
            raise ValueError(f"More than 1 fuel type found for id: {id}")
        return fuels[0]

    def fuel_by_name(self, name: str):
        """Gets a Fuel object by fuel name.

        :param name: The name of the brand.
        :type name: int
        :return: A Brand object.
        """
        fuels = [
            Fuel(**fuel) for fuel in self._fuels() if fuel["Name"] == name
        ]
        if not fuels:
            raise ValueError(f"No fuel type found for name: {name}")
        if len(fuels) > 1:
            raise ValueError(f"More than 1 fuel type found for name: {name}")
        return fuels[0]

    def _fuel_stations(self):
        return self.__fuel_stations

    def fuel_station_by_id(self, id: int):
        """Gets a FuelStation object by fuel station ID.

        :param id: The ID of the fuel station.
        :type id: int
        :return: A FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
            if fuel_station["S"] == id
        ]
        if not fuel_stations:
            raise ValueError(f"No fuel stations found for id: {id}")
        if len(fuel_stations) > 1:
            raise ValueError(f"More than 1 fuel stations found for id: {id}")
        return fuel_stations[0]

    def fuel_station_by_name(self, name: str):
        """Gets a FuelStation object by fuel station name.

        :param name: The name of the fuel station.
        :type name: int
        :return: A FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
            if fuel_station["N"] == name
        ]
        if not fuel_stations:
            raise ValueError(f"No fuel station found for name: {name}")
        if len(fuel_stations) > 1:
            raise ValueError(
                f"More than 1 fuel station found for name: {name}"
            )
        return fuel_stations[0]

    def fuel_stations_by_brand_name(self, name: str):
        """Gets a list of FuelStation objects by brand name.

        :param name: The name of the fuel station.
        :type name: int
        :return: A list of FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
            if fuel_station["B"] == self.brand_by_name(name).BrandId
        ]
        if not fuel_stations:
            raise ValueError(f"No fuel station found for brand: {name}")
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
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
        ]
        # filtered_fuel_stations = filter(
        #    lambda fuel_station: fuel_station.distance(latitude, longitude)
        #    <= max_distance,
        #    fuel_stations,
        # )
        sorted_fuel_stations = sorted(
            fuel_stations,
            key=lambda fuel_station: fuel_station.distance(
                latitude, longitude
            ),
        )

        return sorted_fuel_stations

    def open_fuel_stations(self, datetime: datetime):
        """Gets a list of FuelStation objects for fuel stations open on the
        requested datetime.

        :param datetime: A datetime object.
        :type datetime: datetime
        :return: A list of FuelStation object.
        """
        fuel_stations = [
            FuelStation(**fuel_station)
            for fuel_station in self._fuel_stations()
        ]
        filtered_fuel_stations = filter(
            lambda fuel_station: fuel_station.is_open(datetime), fuel_stations
        )

        return list(filtered_fuel_stations)

    def cheapest_fuel_type(self, name: str):
        """Gets a list of FuelStationPrice objects for a particular fuel.

        :param name: The name of a fuel type.
        :type name: str
        :return: A list of FuelStationPrice objects ordered from cheapest to
            costliest.
        :rtype: List
        """
        fuel_station_prices = [
            FuelStationPrice(**fuel_station_price)
            for fuel_station_price in self._api().GetSitesPrices()[
                "SitePrices"
            ]
        ]
        fuel_id = self.fuel_by_name(name=name).FuelId
        filtered_fuel_station_prices = filter(
            lambda fuel_station_price: fuel_station_price.FuelId == fuel_id,
            fuel_station_prices,
        )
        sorted_fuel_station_prices = sorted(
            filtered_fuel_station_prices,
            key=lambda fuel_station_price: fuel_station_price.Price.amount,
        )

        return sorted_fuel_station_prices

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
            FuelStationPrice(**fuel_station_price)
            for fuel_station_price in self._api().GetSitesPrices()[
                "SitePrices"
            ]
        ]
        filtered_fuel_station_prices = filter(
            lambda fuel_station_price: (
                fuel_station_price.FuelId == fuel_id
                and fuel_station_price.SiteId == fuel_station_id
            ),
            fuel_station_prices,
        )
        prices = list(filtered_fuel_station_prices)
        return prices
