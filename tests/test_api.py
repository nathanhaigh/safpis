#!/usr/bin/env python

"""Tests for `safpis` package."""


from unittest import TestCase, mock

from safpis.api import SafpisAPI, APIKeyMissing
import os
import configparser


class TestApi(TestCase):
    """Tests for `api` package."""

    def setUp(self):
        secret_config_file = "secrets.cfg"
        if os.path.exists(secret_config_file):
            config = configparser.ConfigParser()
            config.read(secret_config_file)
            os.environ["SAFPIS_SUBSCRIBER_TOKEN"] = config["TEST"][
                "SAFPIS_SUBSCRIBER_TOKEN"
            ]

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

    @mock.patch.dict(os.environ, {"fake_key": "fake"}, clear=True)
    def test_token_None(self):
        with self.assertRaises(APIKeyMissing):
            SafpisAPI()

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": ""})
    def test_token_empty(self):
        with self.assertRaises(APIKeyMissing):
            SafpisAPI()

    def test_token_valid(self):
        api = SafpisAPI()
        self.assertIsInstance(api, SafpisAPI)

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": "INVALID-TOKEN"})
    def test_token_invalid(self):
        api = SafpisAPI()
        self.assertIsInstance(api, SafpisAPI)

    def test_GetCountryBrands(self):
        api = SafpisAPI()
        response = api.GetCountryBrands()
        self.assertIsInstance(response, dict)
        self.assertIn("Brands", response)

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": "INVALID-TOKEN"})
    def test_GetCountryBrands_invalid_token(self):
        api = SafpisAPI()
        with self.assertRaises(Exception):
            api.GetCountryBrands()

    def test_GetCountryGeographicRegions(self):
        api = SafpisAPI()
        response = api.GetCountryGeographicRegions()
        self.assertIsInstance(response, dict)
        self.assertIn("GeographicRegions", response)

    def test_GetCountryFuelTypes(self):
        api = SafpisAPI()
        response = api.GetCountryFuelTypes()
        self.assertIsInstance(response, dict)
        self.assertIn("Fuels", response)

    def test_GetFullSiteDetails(self):
        api = SafpisAPI()
        response = api.GetFullSiteDetails()
        self.assertIsInstance(response, dict)
        self.assertIn("S", response)

    def test_GetSitesPrices(self):
        api = SafpisAPI()
        response = api.GetSitesPrices()
        self.assertIsInstance(response, dict)
        self.assertIn("SitePrices", response)
