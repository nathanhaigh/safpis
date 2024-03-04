"""Tests for `safpis` package."""

import os
from datetime import datetime
from decimal import Decimal
from unittest import TestCase, mock

import pytest
import pytz
from geopy.distance import Distance
from money import Money

from safpis.models import Brand, Fuel, FuelStation, FuelStationPrice
from safpis.safpis import NoResultsError, Safpis


class TestSafpis(TestCase):
    """Tests for `safpis` package."""

    def setUp(self):
        if os.path.exists("secrets.cfg"):
            Safpis.load_token()

        self.fuel_station_dict = {
            "S": "61205460",
            "A": "11 Vader Street",
            "N": "OTR Dry Creek",
            "B": 169,
            "P": "5094",
            "G1": 170227225,
            "G2": 189,
            "G3": 4,
            "G4": 0,
            "G5": 0,
            "Lat": -34.819297,
            "Lng": 138.592116,
            "M": "2023-12-27T09:15:01.100",
            "GPI": "ChIJKy0p_ra3sGoRaWz3bT-5iEk",
            "MO": "00:00",
            "MC": "23:59",
            "TO": "00:00",
            "TC": "23:59",
            "WO": "00:00",
            "WC": "23:59",
            "THO": "00:00",
            "THC": "23:59",
            "FO": "00:00",
            "FC": "23:59",
            "SO": "00:00",
            "SC": "23:59",
            "SUO": "00:00",
            "SUC": "23:59",
        }
        self.fuel_station_prices_dict = {
            "SiteId": 61501045,
            "FuelId": 14,
            "CollectionMethod": "T",
            "TransactionDateUtc": "2021-01-06T22:55:00",
            "Price": 1356.0,
        }

        self.adl_tz = pytz.timezone("Australia/Adelaide")

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_price(self):
        safpis = Safpis()
        prices = safpis.price(61205460, 2)
        fuel_station_price = prices[0]
        assert isinstance(fuel_station_price.Price, Money)
        patched_money = Money(
            amount=Decimal(str(5678.9)),
            currency="AUD",
        )
        with mock.patch.object(fuel_station_price, "Price", patched_money):
            assert fuel_station_price.Price.amount == Decimal("5678.9")

    def test_brand_by_id(self):
        safpis = Safpis()
        brand = safpis.brand_by_id(2)
        assert isinstance(brand, Brand)
        assert brand.Name == "Caltex"

    def test_brand_by_id_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.brand_by_id(9999999)

    def test_brand_by_name(self):
        safpis = Safpis()
        brand = safpis.brand_by_name("Caltex")
        assert isinstance(brand, Brand)
        assert brand.BrandId == 2

    def test_brands_by_name_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.brand_by_name("Non-existent")

    def test_fuel_by_id(self):
        safpis = Safpis()
        fuel = safpis.fuel_by_id(2)
        assert isinstance(fuel, Fuel)
        assert fuel.Name == "Unleaded"

    def test_fuel_by_id_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.fuel_by_id(9999999)

    def test_fuel_by_name(self):
        safpis = Safpis()
        fuel = safpis.fuel_by_name("e10")
        assert isinstance(fuel, Fuel)
        assert fuel.FuelId == 12

    def test_fuel_by_name_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.fuel_by_name("Non-existent")

    def test_fuel_station_instantiation_m_with_subsecond(self):
        """Ensures we are able to instatiate a FuelStation when the M field
        returned by SAFPIS REST API contains subseconds."""
        fuel_station = FuelStation(**self.fuel_station_dict)
        assert isinstance(fuel_station, FuelStation)

    def test_fuel_station_instantiation_m_without_subsecond(self):
        """Ensures we are able to instatiate a FuelStation when the M field
        returned by SAFPIS REST API does NOT contain subseconds."""
        self.fuel_station_dict["M"] = "2023-12-27T09:15:01"
        fuel_station = FuelStation(**self.fuel_station_dict)
        assert isinstance(fuel_station, FuelStation)

    def test_fuel_station_instantiation_monday_open_as_none(self):
        """Ensures we are able to instatiate a FuelStation when an Open field
        returned by SAFPIS REST API is None."""
        self.fuel_station_dict["MO"] = None
        fuel_station = FuelStation(**self.fuel_station_dict)
        assert isinstance(fuel_station, FuelStation)

    def test_fuel_station_instantiation_monday_open_as_empty(self):
        """Ensures we are able to instatiate a FuelStation when an Open field
        returned by SAFPIS REST API is empty."""
        self.fuel_station_dict["MO"] = ""
        fuel_station = FuelStation(**self.fuel_station_dict)
        assert isinstance(fuel_station, FuelStation)

    def test_fuel_station_is_open(self):
        self.fuel_station_dict["MO"] = "06:00"
        self.fuel_station_dict["MC"] = "23:59"
        fuel_station = FuelStation(**self.fuel_station_dict)
        assert fuel_station.is_open(datetime(2023, 12, 25, 6, 0, 0, tzinfo=self.adl_tz))
        assert not fuel_station.is_open(datetime(2023, 12, 25, 4, 0, 0, tzinfo=self.adl_tz))
        assert fuel_station.is_open(datetime(2023, 12, 25, 23, 59, 0, tzinfo=self.adl_tz))
        assert not fuel_station.is_open(datetime(2023, 12, 25, 0, 0, 0, tzinfo=self.adl_tz))

    def test_fuel_station_by_id(self):
        safpis = Safpis()
        fuel_station = safpis.fuel_station_by_id(61205460)
        assert isinstance(fuel_station, FuelStation)
        assert fuel_station.N == "OTR Dry Creek"

    def test_fuel_station_by_id_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.fuel_station_by_id(9999999)

    def test_fuel_station_by_name(self):
        safpis = Safpis()
        fuel_station = safpis.fuel_station_by_name("OTR Dry Creek")
        assert isinstance(fuel_station, FuelStation)
        assert fuel_station.S == 61205460

    def test_fuel_station_by_name_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.fuel_station_by_name("Non-existent")

    def test_fuel_stations_by_brand_name(self):
        safpis = Safpis()
        fuel_stations = safpis.fuel_stations_by_brand_name("United")
        assert isinstance(fuel_stations, list)
        assert isinstance(fuel_stations[0], FuelStation)
        assert fuel_stations[0].B == 23

    def test_fuel_stations_by_brand_name_non_existant(self):
        safpis = Safpis()
        with pytest.raises(NoResultsError):
            safpis.fuel_stations_by_brand_name("Non-existent")

    def test_fuel_station_distance(self):
        fuel_station = FuelStation(**self.fuel_station_dict)
        latitude = -34.819297
        longitude = 138.592116
        dist = fuel_station.distance(latitude, longitude)
        assert isinstance(dist, Distance)
        assert dist.km == 0

    def test_closest_fuel_stations(self):
        safpis = Safpis()
        latitude = -34.819297
        longitude = 138.592116
        fuel_stations = safpis.closest_fuel_stations(latitude, longitude)
        assert isinstance(fuel_stations, list)
        assert isinstance(fuel_stations[0], FuelStation)
        assert fuel_stations[0].N == "OTR Dry Creek"

    def test_open_fuel_stations(self):
        safpis = Safpis()
        fuel_stations = safpis.open_fuel_stations(datetime(2023, 12, 25, 4, 0, 0, tzinfo=self.adl_tz))
        assert isinstance(fuel_stations, list)
        assert isinstance(fuel_stations[0], FuelStation)

    def test_fuel_station_price(self):
        fuel_station_price = FuelStationPrice(**self.fuel_station_prices_dict)
        assert isinstance(fuel_station_price, FuelStationPrice)
        assert isinstance(fuel_station_price.Price.amount, Decimal)
        assert fuel_station_price.Price.amount == Decimal("1356")

    def test_cheapest_fuel_type(self):
        safpis = Safpis()
        fuel_station_prices = safpis.cheapest_fuel_type("e10")
        assert isinstance(fuel_station_prices, list)
        assert isinstance(fuel_station_prices[0], FuelStationPrice)
