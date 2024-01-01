"""Console script for safpis."""
import sys
import click
from safpis.api import SafpisAPI


@click.group()
def main(args=None):
    """Command line interface to the South Australia Fuel Pricing Information
    Scheme (SAFPIS)."""
    pass


#####
# site
#####
@main.command()
@click.option("--id", type=int, help="Fuel station site ID.")
@click.option("--name", type=str, help="Fuel station site name.")
def site(id, name):
    """Get fuel station site information."""
    if (not id and not name) or (id and name):
        click.echo("Error: You must provide either --id or --name.")
        return

    safpis_api = SafpisAPI()

    if id:
        sites = safpis_api.sites_by_id(id=id)
    elif name:
        sites = safpis_api.sites_by_name(name=name)
    click.echo(sites[0])


#####
# brand
#####
@main.command()
@click.option("--id", type=int, help="Fuel station brand ID.")
@click.option("--name", type=str, help="Fuel station brand name.")
def brand(id, name):
    """Get fuel station brand information."""
    if (not id and not name) or (id and name):
        click.echo("Error: You must provide either --id or --name.")
        return

    safpis_api = SafpisAPI()

    if id:
        brands = safpis_api.brands_by_id(id=id)
    elif name:
        brands = safpis_api.brands_by_name(name=name)
    click.echo(brands[0])


#####
# Fuel
#####
@main.command()
@click.option("--id", type=int, help="Fuel ID.")
@click.option("--name", type=str, help="Fuel name.")
def fuel(id, name):
    """Get fuel information."""
    if (not id and not name) or (id and name):
        click.echo("Error: You must provide either --id or --name.")
        return

    safpis_api = SafpisAPI()

    if id:
        fuels = safpis_api.fuels_by_id(id=id)
    elif name:
        fuels = safpis_api.fuels_by_name(name=name)
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

    price = safpis_api.price(site_id=site_id, fuel_id=fuel_id)
    click.echo(price[0])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
