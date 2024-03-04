"""Tests for `safpis` package."""

import configparser
import os
from unittest import TestCase

from click.testing import CliRunner

from safpis import cli


class TestCli(TestCase):
    """Tests for `cli` package."""

    def setUp(self):
        secret_config_file = "secrets.cfg"
        if os.path.exists(secret_config_file):
            config = configparser.ConfigParser()
            config.read(secret_config_file)
            os.environ["SAFPIS_SUBSCRIBER_TOKEN"] = config["TEST"]["SAFPIS_SUBSCRIBER_TOKEN"]

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert "SAFPIS" in result.output
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "--help  Show this message and exit." in help_result.output
