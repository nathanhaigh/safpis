#!/usr/bin/env python

"""Tests for `safpis` package."""


from unittest import TestCase, mock
from click.testing import CliRunner

from safpis.api import SafpisAPI, APIKeyMissing
from safpis.models import Brand, Fuel, Site, SitePrice
from safpis import cli
from geopy.distance import Distance
from datetime import datetime
from decimal import Decimal
import os
import configparser


class TestSafpis(TestCase):
    """Tests for `safpis` package."""

    def setUp(self):
        secret_config_file = "secrets.cfg"
        if os.path.exists(secret_config_file):
            config = configparser.ConfigParser()
            config.read(secret_config_file)
            os.environ["SAFPIS_SUBSCRIBER_TOKEN"] = config["TEST"][
                "SAFPIS_SUBSCRIBER_TOKEN"
            ]

        self.site_dict = {
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
        self.site_prices_dict = {
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
        safpis_api = SafpisAPI()
        self.assertIsInstance(safpis_api, SafpisAPI)

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": "INVALID-TOKEN"})
    def test_token_invalid(self):
        safpis_api = SafpisAPI()
        self.assertIsInstance(safpis_api, SafpisAPI)

    def test_get_country_brands(self):
        safpis_api = SafpisAPI()
        response = safpis_api.get_country_brands()
        self.assertIsInstance(response, dict)
        self.assertIn("Brands", response)

    @mock.patch.dict(os.environ, {"SAFPIS_SUBSCRIBER_TOKEN": "INVALID-TOKEN"})
    def test_get_country_brands_invalid_token(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.get_country_brands()

    def test_get_country_geographic_regions(self):
        safpis_api = SafpisAPI()
        response = safpis_api.get_country_geographic_regions()
        self.assertIsInstance(response, dict)
        self.assertIn("GeographicRegions", response)

    def test_get_country_fuel_types(self):
        safpis_api = SafpisAPI()
        response = safpis_api.get_country_fuel_types()
        self.assertIsInstance(response, dict)
        self.assertIn("Fuels", response)

    def test_get_full_site_details(self):
        safpis_api = SafpisAPI()
        response = safpis_api.get_full_site_details()
        self.assertIsInstance(response, dict)
        self.assertIn("S", response)

    def test_get_sites_prices(self):
        safpis_api = SafpisAPI()
        response = safpis_api.get_sites_prices()
        self.assertIsInstance(response, dict)
        self.assertIn("SitePrices", response)

    def test_brands_by_id(self):
        safpis_api = SafpisAPI()
        brands = safpis_api.brands_by_id(id=2)
        self.assertIsInstance(brands, list)
        self.assertIsInstance(brands[0], Brand)
        self.assertEqual(brands[0].Name, "Caltex")

    def test_brands_by_id_non_existant(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.brands_by_id(id=9999999)

    def test_brands_by_name(self):
        safpis_api = SafpisAPI()
        brands = safpis_api.brands_by_name(name="Caltex")
        self.assertIsInstance(brands, list)
        self.assertIsInstance(brands[0], Brand)
        self.assertEqual(brands[0].BrandId, 2)

    def test_brands_by_name_non_existant(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.brands_by_name(name="Non-existent")

    def test_fuels_by_id(self):
        safpis_api = SafpisAPI()
        fuels = safpis_api.fuels_by_id(id=2)
        self.assertIsInstance(fuels, list)
        self.assertIsInstance(fuels[0], Fuel)
        self.assertEqual(fuels[0].Name, "Unleaded")

    def test_fuels_by_id_non_existant(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.fuels_by_id(id=9999999)

    def test_fuels_by_name(self):
        safpis_api = SafpisAPI()
        fuels = safpis_api.fuels_by_name(name="e10")
        self.assertIsInstance(fuels, list)
        self.assertIsInstance(fuels[0], Fuel)
        self.assertEqual(fuels[0].FuelId, 12)

    def test_fuels_by_name_non_existant(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.fuels_by_name(name="Non-existent")

    def test_site_instantiation_M_with_subsecond(self):
        site = Site(**self.site_dict)
        self.assertIsInstance(site, Site)

    def test_site_instantiation_M_without_subsecond(self):
        self.site_dict["M"] = "2023-12-27T09:15:01"
        site = Site(**self.site_dict)
        self.assertIsInstance(site, Site)

    def test_site_instantiation_MO_as_None(self):
        self.site_dict["MO"] = None
        site = Site(**self.site_dict)
        self.assertIsInstance(site, Site)

    def test_site_instantiation_MO_as_empty(self):
        self.site_dict["MO"] = ""
        site = Site(**self.site_dict)
        self.assertIsInstance(site, Site)

    def test_site_is_open(self):
        self.site_dict["MO"] = "06:00"
        self.site_dict["MC"] = "23:59"
        site = Site(**self.site_dict)
        self.assertTrue(site.is_open(datetime(2023, 12, 25, 6, 0, 0)))
        self.assertFalse(site.is_open(datetime(2023, 12, 25, 4, 0, 0)))
        self.assertTrue(site.is_open(datetime(2023, 12, 25, 23, 59, 0)))
        self.assertFalse(site.is_open(datetime(2023, 12, 25, 0, 0, 0)))
        self.assertTrue(site.is_open())

    def test_sites_by_id(self):
        safpis_api = SafpisAPI()
        sites = safpis_api.sites_by_id(id=61205460)
        self.assertIsInstance(sites, list)
        self.assertIsInstance(sites[0], Site)
        self.assertEqual(sites[0].N, "OTR Dry Creek")

    def test_sites_by_id_non_existant(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.sites_by_id(id=9999999)

    def test_sites_by_name(self):
        safpis_api = SafpisAPI()
        sites = safpis_api.sites_by_name(name="OTR Dry Creek")
        self.assertIsInstance(sites, list)
        self.assertIsInstance(sites[0], Site)
        self.assertEqual(sites[0].S, 61205460)

    def test_sites_by_name_non_existant(self):
        safpis_api = SafpisAPI()
        with self.assertRaises(Exception):
            safpis_api.sites_by_name(name="Non-existent")

    def test_site_distance_between(self):
        site = Site(**self.site_dict)
        dist = site.distance_between(-34.819297, 138.592116)
        self.assertIsInstance(dist, Distance)
        self.assertEqual(dist.km, 0)

    def test_sites_by_distance(self):
        safpis_api = SafpisAPI()
        sites = safpis_api.sites_by_distance(
            latitude=-34.819297,
            longitude=138.592116,
            max_distance=Distance(kilometers=10),
        )
        self.assertIsInstance(sites, list)
        self.assertIsInstance(sites[0], Site)
        self.assertEqual(sites[0].N, "OTR Dry Creek")

    def test_sites_open(self):
        safpis_api = SafpisAPI()
        sites = safpis_api.sites_open(datetime(2023, 12, 25, 4, 0, 0))
        self.assertIsInstance(sites, list)
        self.assertIsInstance(sites[0], Site)

    def test_site_price(self):
        site_price = SitePrice(**self.site_prices_dict)
        self.assertIsInstance(site_price, SitePrice)
        self.assertIsInstance(site_price.Price.amount, Decimal)
        self.assertEqual(site_price.Price.amount, Decimal("1356"))

    def test_sites_by_cheapest_fuel_type(self):
        safpis_api = SafpisAPI()
        site_prices = safpis_api.sites_by_cheapest_fuel_type(fuel_type="e10")
        self.assertIsInstance(site_prices, list)
        self.assertIsInstance(site_prices[0], SitePrice)

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert "safpis.cli.main" in result.output
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "--help  Show this message and exit." in help_result.output
