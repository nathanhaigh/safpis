=====
Usage
=====

Basic Usage
===========

To use this SAFPIS REST API wrapper library::

    from safpis.safpis import Safpis
    from tabulate import tabulate

    # First ensure you have your SAFPIS Data Publisher Token defined
    # in the SAFPIS_SUBSCRIBER_TOKEN environmental variable.
    #
    # To be secure, it is best to store your SAFPIS Data Publisher
    # Token in a file. We provide a convienient way to load the
    # token from an ini-style config file using something like:
    Safpis.load_token(
        ini = "secrets.cfg",
        section = "TEST",
        key = "SAFPIS_SUBSCRIBER_TOKEN"
    )

    safpis = Safpis()

    # Get list of fuel types
    #####
    print(tabulate(safpis._fuels(), headers="keys", tablefmt="pretty"))

    # Get fuel by name or id
    #####
    fuel = safpis.fuel_by_name("Unleaded")
    fuel.FuelId
    fuel = safpis.fuel_by_id(2)
    fuel.Name

    # Get list of brands
    #####
    print(tabulate(safpis._brands(), headers="keys", tablefmt="pretty"))

    # Get brand by name or id
    #####
    brand = safpis.brand_by_name("Caltex")
    brand.BrandId
    brand = safpis.brand_by_id(2)
    brand.Name

    # Get the list of fuel stations
    #####
    print(tabulate(safpis._fuel_stations(), headers="keys", tablefmt="pretty"))

    # Get fuel stations sorted by distance to a particular location
    #####
    latitude = -35.073360
    longitude = 138.570401

    # TODO: this function should allow a list of sites to be provided
    # to it and also return the associated distances
    fuel_stations = safpis.closest_fuel_stations(
        latitude,
        longitude,
    )
    print(tabulate(fuel_stations, headers="keys", tablefmt="pretty"))

    # Get the distance to the closest fuel station
    #####
    fuel_stations[0].distance(latitude, longitude)

    # Get the ID's of the closest 5 fuel stations
    #####
    [fuel_station.S for fuel_station in fuel_stations[0:5]]

    # Get fuel stations for a particular brand
    #####
    fuel_stations = safpis.fuel_stations_by_brand_name("EG Ampol")
    print(tabulate(fuel_stations, headers="keys", tablefmt="pretty"))

    # Get fuel stations for a particular brand within a certain
    # distance
    #####
    latitude = -35.073360
    longitude = 138.570401
    brand_name = "On the Run"
    max_dist_km = 10

    fuel_stations = sorted(
        filter(
            lambda fuel_station: fuel_station.distance(latitude, longitude)
            <= max_dist_km,
            safpis.fuel_stations_by_brand_name(brand_name),
        ),
        key=lambda fuel_station: fuel_station.distance(latitude, longitude),
    )
    print(tabulate(fuel_stations, headers="keys", tablefmt="pretty"))

Working with the REST API
=========================

To work more directly with the SAFPIS REST API, you can just import and use `safpis.api`.
It provided little more than a wrapper around the API calls, with convienient default
request parameters, appropriate caching of the requests and returning of the JSON
response::

    from safpis.api import SafpisAPI
    from safpis.safpis import Safpis

    # Load the token from a ini-style config file
    Safpis.load_token(
        ini = "secrets.cfg",
        section = "TEST",
        key = "SAFPIS_SUBSCRIBER_TOKEN"
    )

    api = SafpisAPI()

    # The GetCountryBrands endpoint
    brands = api.GetCountryBrands()

    # The GetCountryGeographicRegions endpoint
    regions = api.GetCountryGeographicRegions()

    # The GetCountryFuelTypes endpoint
    fuel_types = api.GetCountryFuelTypes()

    # The GetFullSiteDetails endpoint
    fuel_stations = api.GetFullSiteDetails()

    # The GetSitesPrices endpoint
    prices = api.GetSitesPrices()


Home Assistant Rest Sensor
==========================

You can generate a rest sensor stub for a tracking the price of fuel at a fuel
station of your choice::

    # Generate a Home Assistant rest sensor for a particular
    # type of fuel from a particular fuel station
    #####
    def ha_fuel_sensor(fuel_station_id, fuel_id):
        site_name = safpis.fuel_station_by_id(fuel_station_id).N
        fuel_name = safpis.fuel_by_id(fuel_id).Name
        print(f'      - name: "{site_name} - {fuel_name}"')
        print(f'        value_template: "{{ ((value_json.SitePrices|selectattr(\'SiteId\',\'==\',{fuel_station_id})|selectattr(\'FuelId\', \'==\', {fuel_id})|first).Price / 1000) | round(3) }}"')
        print(f'        unit_of_measurement: AUD')
        print(f'        state_class: measurement')

    # Using the above info, find the ID of a fuel station and fuel
    # type for which you want a sensor
    #####
    fuel_station_id = 61501319
    fuel_id = 2

    # Double-check the names
    safpis.fuel_station_by_id(fuel_station_id).N
    safpis.fuel_by_id(fuel_id).FuelId

    # Generate the rest sensor text
    #####
    ha_fuel_sensor(fuel_station_id, fuel_id)
    #ha_fuel_sensor(site_name = "EG Ampol Eden Hills", fuel_name = "Unleaded")
