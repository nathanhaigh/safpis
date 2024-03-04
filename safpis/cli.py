"""Console script for safpis."""

import sys

import click

from safpis.api import SafpisAPI


@click.group()
def main():
    """Command line interface to the South Australia Fuel Pricing Information
    Scheme (SAFPIS)."""


#####
# site
#####
@main.command()
@click.option("--id", type=int, help="Fuel station site ID.")
@click.option("--name", type=str, help="Fuel station site name.")
def site(site_id, name):
    """Get fuel station site information."""
    if (not site_id and not name) or (site_id and name):
        click.echo("Error: You must provide either --id or --name.")
        return

    safpis_api = SafpisAPI()

    if site_id:
        sites = safpis_api.sites_by_id(site_id)
    elif name:
        sites = safpis_api.sites_by_name(name=name)
    click.echo(sites[0])


#####
# brand
#####
@main.command()
@click.option("--id", type=int, help="Fuel station brand ID.")
@click.option("--name", type=str, help="Fuel station brand name.")
def brand(brand_id, name):
    """Get fuel station brand information."""
    if (not brand_id and not name) or (brand_id and name):
        click.echo("Error: You must provide either --id or --name.")
        return

    safpis_api = SafpisAPI()

    if brand_id:
        brands = safpis_api.brands_by_id(brand_id)
    elif name:
        brands = safpis_api.brands_by_name(name=name)
    click.echo(brands[0])


#####
# Fuel
#####
@main.command()
@click.option("--id", type=int, help="Fuel ID.")
@click.option("--name", type=str, help="Fuel name.")
def fuel(fuel_id, name):
    """Get fuel information."""
    if (not fuel_id and not name) or (fuel_id and name):
        click.echo("Error: You must provide either --id or --name.")
        return

    safpis_api = SafpisAPI()

    if fuel_id:
        fuels = safpis_api.fuels_by_id(fuel_id)
    elif name:
        fuels = safpis_api.fuels_by_name(name)
    click.echo(fuels[0])


#####
# Price
#####
@main.command()
@click.option("--site-id", type=int, help="Site ID.")
@click.option("--fuel-id", type=int, help="Fuel ID.")
def price(site_id, fuel_id):
    """Get price information."""
    if not (site_id and fuel_id):
        click.echo("Error: You must provide both --site-id or --fuel-id.")
        return

    safpis_api = SafpisAPI()

    price = safpis_api.price(site_id, fuel_id)
    click.echo(price[0])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
