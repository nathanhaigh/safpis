"""Tests for `safpis` package."""

import configparser
import os
from unittest import TestCase, mock

import pytest
import requests

from safpis.api import APIKeyMissingError, SafpisAPI


class TestApi(TestCase):
    """Tests for `api` package."""

    def setUp(self):
        secret_config_file = "secrets.cfg"
        if os.path.exists(secret_config_file):
            config = configparser.ConfigParser()
            config.read(secret_config_file)
            os.environ["SAFPIS_SUBSCRIBER_TOKEN"] = config["TEST"]["SAFPIS_SUBSCRIBER_TOKEN"]

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
        with pytest.raises(APIKeyMissingError):
            SafpisAPI()

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": ""})
    def test_token_empty(self):
        with pytest.raises(APIKeyMissingError):
            SafpisAPI()

    def test_token_valid(self):
        api = SafpisAPI()
        assert isinstance(api, SafpisAPI)

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": "INVALID-TOKEN"})
    def test_token_invalid(self):
        api = SafpisAPI()
        assert isinstance(api, SafpisAPI)

    def test_GetCountryBrands(self):
        api = SafpisAPI()
        response = api.GetCountryBrands()
        assert isinstance(response, dict)
        assert "Brands" in response

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": "INVALID-TOKEN"})
    def test_GetCountryBrands_invalid_token(self):
        api = SafpisAPI()
        with pytest.raises(requests.exceptions.HTTPError):
            api.GetCountryBrands()

    def test_GetCountryGeographicRegions(self):
        api = SafpisAPI()
        response = api.GetCountryGeographicRegions()
        assert isinstance(response, dict)
        assert "GeographicRegions" in response

    def test_GetCountryFuelTypes(self):
        api = SafpisAPI()
        response = api.GetCountryFuelTypes()
        assert isinstance(response, dict)
        assert "Fuels" in response

    def test_GetFullSiteDetails(self):
        api = SafpisAPI()
        response = api.GetFullSiteDetails()
        assert isinstance(response, dict)
        assert "S" in response

    def test_GetSitesPrices(self):
        api = SafpisAPI()
        response = api.GetSitesPrices()
        assert isinstance(response, dict)
        assert "SitePrices" in response
