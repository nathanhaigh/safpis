#!/usr/bin/env python

"""Tests for `safpis` package."""


from unittest import TestCase, mock

from safpis.safpis import Safpis
from safpis.models import Brand, Fuel, FuelStation, FuelStationPrice
from geopy.distance import Distance
from datetime import datetime
from decimal import Decimal
from money import Money
import os


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

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_price(self):
        safpis = Safpis()
        prices = safpis.price(fuel_station_id=61205460, fuel_id=2)
        fuel_station_price = prices[0]
        self.assertIsInstance(fuel_station_price.Price, Money)
        patched_money = Money(
            amount=Decimal(str(5678.9)),
            currency="AUD",
        )
        with mock.patch.object(fuel_station_price, "Price", patched_money):
            self.assertEqual(
                fuel_station_price.Price.amount, Decimal("5678.9")
            )

    def test_brand_by_id(self):
        safpis = Safpis()
        brand = safpis.brand_by_id(id=2)
        self.assertIsInstance(brand, Brand)
        self.assertEqual(brand.Name, "Caltex")

    def test_brand_by_id_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.brand_by_id(id=9999999)

    def test_brand_by_name(self):
        safpis = Safpis()
        brand = safpis.brand_by_name(name="Caltex")
        self.assertIsInstance(brand, Brand)
        self.assertEqual(brand.BrandId, 2)

    def test_brands_by_name_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.brand_by_name(name="Non-existent")

    def test_fuel_by_id(self):
        safpis = Safpis()
        fuel = safpis.fuel_by_id(id=2)
        self.assertIsInstance(fuel, Fuel)
        self.assertEqual(fuel.Name, "Unleaded")

    def test_fuel_by_id_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.fuel_by_id(id=9999999)

    def test_fuel_by_name(self):
        safpis = Safpis()
        fuel = safpis.fuel_by_name(name="e10")
        self.assertIsInstance(fuel, Fuel)
        self.assertEqual(fuel.FuelId, 12)

    def test_fuel_by_name_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.fuel_by_name(name="Non-existent")

    def test_fuel_station_instantiation_M_with_subsecond(self):
        """Ensures we are able to instatiate a FuelStation when the M field
        returned by SAFPIS REST API contains subseconds."""
        fuel_station = FuelStation(**self.fuel_station_dict)
        self.assertIsInstance(fuel_station, FuelStation)

    def test_fuel_station_instantiation_M_without_subsecond(self):
        """Ensures we are able to instatiate a FuelStation when the M field
        returned by SAFPIS REST API does NOT contain subseconds."""
        self.fuel_station_dict["M"] = "2023-12-27T09:15:01"
        fuel_station = FuelStation(**self.fuel_station_dict)
        self.assertIsInstance(fuel_station, FuelStation)

    def test_fuel_station_instantiation_MO_as_None(self):
        """Ensures we are able to instatiate a FuelStation when an Open field
        returned by SAFPIS REST API is None."""
        self.fuel_station_dict["MO"] = None
        fuel_station = FuelStation(**self.fuel_station_dict)
        self.assertIsInstance(fuel_station, FuelStation)

    def test_fuel_station_instantiation_MO_as_empty(self):
        """Ensures we are able to instatiate a FuelStation when an Open field
        returned by SAFPIS REST API is empty."""
        self.fuel_station_dict["MO"] = ""
        fuel_station = FuelStation(**self.fuel_station_dict)
        self.assertIsInstance(fuel_station, FuelStation)

    def test_fuel_station_is_open(self):
        self.fuel_station_dict["MO"] = "06:00"
        self.fuel_station_dict["MC"] = "23:59"
        fuel_station = FuelStation(**self.fuel_station_dict)
        self.assertTrue(fuel_station.is_open(datetime(2023, 12, 25, 6, 0, 0)))
        self.assertFalse(fuel_station.is_open(datetime(2023, 12, 25, 4, 0, 0)))
        self.assertTrue(
            fuel_station.is_open(datetime(2023, 12, 25, 23, 59, 0))
        )
        self.assertFalse(fuel_station.is_open(datetime(2023, 12, 25, 0, 0, 0)))

    def test_fuel_station_by_id(self):
        safpis = Safpis()
        fuel_station = safpis.fuel_station_by_id(id=61205460)
        self.assertIsInstance(fuel_station, FuelStation)
        self.assertEqual(fuel_station.N, "OTR Dry Creek")

    def test_fuel_station_by_id_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.fuel_station_by_id(id=9999999)

    def test_fuel_station_by_name(self):
        safpis = Safpis()
        fuel_station = safpis.fuel_station_by_name(name="OTR Dry Creek")
        self.assertIsInstance(fuel_station, FuelStation)
        self.assertEqual(fuel_station.S, 61205460)

    def test_fuel_station_by_name_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.fuel_station_by_name(name="Non-existent")

    def test_fuel_stations_by_brand_name(self):
        safpis = Safpis()
        fuel_stations = safpis.fuel_stations_by_brand_name(name="United")
        self.assertIsInstance(fuel_stations, list)
        self.assertIsInstance(fuel_stations[0], FuelStation)
        self.assertEqual(fuel_stations[0].B, 23)

    def test_fuel_stations_by_brand_name_non_existant(self):
        safpis = Safpis()
        with self.assertRaises(Exception):
            safpis.fuel_stations_by_brand_name(name="Non-existent")

    def test_fuel_station_distance(self):
        fuel_station = FuelStation(**self.fuel_station_dict)
        dist = fuel_station.distance(-34.819297, 138.592116)
        self.assertIsInstance(dist, Distance)
        self.assertEqual(dist.km, 0)

    def test_closest_fuel_stations(self):
        safpis = Safpis()
        fuel_stations = safpis.closest_fuel_stations(
            latitude=-34.819297, longitude=138.592116
        )
        self.assertIsInstance(fuel_stations, list)
        self.assertIsInstance(fuel_stations[0], FuelStation)
        self.assertEqual(fuel_stations[0].N, "OTR Dry Creek")

    def test_open_fuel_stations(self):
        safpis = Safpis()
        fuel_stations = safpis.open_fuel_stations(
            datetime(2023, 12, 25, 4, 0, 0)
        )
        self.assertIsInstance(fuel_stations, list)
        self.assertIsInstance(fuel_stations[0], FuelStation)

    def test_fuel_station_price(self):
        fuel_station_price = FuelStationPrice(**self.fuel_station_prices_dict)
        self.assertIsInstance(fuel_station_price, FuelStationPrice)
        self.assertIsInstance(fuel_station_price.Price.amount, Decimal)
        self.assertEqual(fuel_station_price.Price.amount, Decimal("1356"))

    def test_cheapest_fuel_type(self):
        safpis = Safpis()
        fuel_station_prices = safpis.cheapest_fuel_type(name="e10")
        self.assertIsInstance(fuel_station_prices, list)
        self.assertIsInstance(fuel_station_prices[0], FuelStationPrice)
