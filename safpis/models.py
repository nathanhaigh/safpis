from datetime import datetime, time
import geopy.distance
from money import Money


class Brand:
    def __init__(self, BrandId: int, Name: str) -> None:
        """
        Brand returned ...
        :param BrandId: Unique Brand ID
        :param Name: Brand's name
        """
        self.id = int(BrandId)
        self.name = str(Name)

    def __str__(self):
        return f"Brand: id={self.id}, name={self.name}"


class Region:
    def __init__(
        self,
        GeoRegionId: int,
        GeoRegionLevel: int,
        Name: str,
        Abbrev: str,
        GeoRegionParentId: int,
    ) -> None:
        """
        Region returned ...
        :param GeoRegionId: Unique Region ID
        :param GeoRegionLevel: The Level (3 = State, 2 = City and 1 = Suburb)
        :param Name: Name of the Region
        :param Abbrev: Abbreviated form of the Region's Name
        :param GeoRegionParentId: ID of the Region's parent
        """
        self.id = int(GeoRegionId)
        self.level = int(GeoRegionLevel)
        self.name = str(Name)
        self.abbrev = str(Abbrev)
        if GeoRegionParentId is not None:
            self.parent_id = int(GeoRegionParentId)
        else:
            self.parent_id = None

    def __str__(self):
        return (
            f"Region: id={self.id}, name={self.name}, level={self.level}, "
            f"abbrev={self.abbrev}, parent_id={self.parent_id}"
        )


class Fuel:
    def __init__(self, FuelId: int, Name: str) -> None:
        """
        Fuel returned ...
        :param FuelId: Unique Fuel Type ID
        :param Name: name of the Fuel Type
        """
        self.id = int(FuelId)
        self.name = str(Name)

    def __str__(self):
        return f"Fuel: id={self.id}, name={self.name}"


class Site:
    def __init__(
        self,
        S: int,
        A: str,
        N: str,
        B: int,
        P: int,
        G1: int,
        G2: int,
        G3: int,
        G4: int,
        G5: int,
        Lat: float,
        Lng: float,
        M: datetime,
        GPI: str,
        MO: time,
        MC: time,
        TO: time,
        TC: time,
        WO: time,
        WC: time,
        THO: time,
        THC: datetime,
        FO: time,
        FC: time,
        SO: time,
        SC: time,
        SUO: time,
        SUC: time,
    ) -> None:
        """
        Look at using treelib: https://treelib.readthedocs.io/en/latest/
        """
        self.id = int(S)
        self.address = str(A)
        self.name = str(N)
        self.brand_id = int(B)
        self.postcode = int(P)
        self.subsurb = int(G1)
        self.city = int(G2)
        self.state = int(G3)
        self.geographic_level_4 = int(G4)
        self.geographic_level_5 = int(G5)
        self.latitude = float(Lat)
        self.longitude = float(Lng)
        try:
            self.last_modified = datetime.strptime(M, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            self.last_modified = datetime.strptime(M, "%Y-%m-%dT%H:%M:%S")
        self.google_place_id = str(GPI)

        # Monday
        if MO.strip() == "":
            self.monday_open = None
        else:
            self.monday_open = datetime.strptime(MO, "%H:%M")
        if MC.strip() == "":
            self.monday_close = None
        else:
            self.monday_close = datetime.strptime(MC, "%H:%M")

        # Tuesday
        if TO.strip() == "":
            self.tuesday_open = None
        else:
            self.tuesday_open = datetime.strptime(TO, "%H:%M")
        if TC.strip() == "":
            self.tuesday_close = None
        else:
            self.tuesday_close = datetime.strptime(TC, "%H:%M")

        # Wednesday
        if WO.strip() == "":
            self.wednesday_open = None
        else:
            self.wednesday_open = datetime.strptime(WO, "%H:%M")
        if WC.strip() == "":
            self.wednesday_close = None
        else:
            self.wednesday_close = datetime.strptime(WC, "%H:%M")

        # Thursday
        if THO.strip() == "":
            self.thursday_open = None
        else:
            self.thursday_open = datetime.strptime(THO, "%H:%M")
        if THC.strip() == "":
            self.thursday_close = None
        else:
            self.thursday_close = datetime.strptime(THC, "%H:%M")

        # Friday
        if FO.strip() == "":
            self.friday_open = None
        else:
            self.friday_open = datetime.strptime(FO, "%H:%M")
        if FC.strip() == "":
            self.friday_close = None
        else:
            self.friday_close = datetime.strptime(FC, "%H:%M")

        # Saturday
        if SO.strip() == "":
            self.saturday_open = None
        else:
            self.saturday_open = datetime.strptime(SO, "%H:%M")
        if SC.strip() == "":
            self.saturday_close = None
        else:
            self.saturday_close = datetime.strptime(SC, "%H:%M")

        # Sunday
        if SUO.strip() == "":
            self.sunday_open = None
        else:
            self.sunday_open = datetime.strptime(SUO, "%H:%M")
        if SUC.strip() == "":
            self.sunday_close = None
        else:
            self.sunday_close = datetime.strptime(SUC, "%H:%M")

    def __str__(self):
        return (
            f"Site: id={self.id}, brand_id={self.brand_id}, name={self.name}, "
            f"postcode={self.postcode}, "
            f"google_place_id=https://www.google.com/maps/search/?api=1&query=Google&query_place_id={self.google_place_id}"
        )

    def distance_between(self, latitude: float, longitude: float):
        """
        Function to return a distance between the site and a lat/long
        coordinate.
        :return: Distance object
        """
        return geopy.distance.geodesic(
            (self.latitude, self.longitude), (latitude, longitude)
        )


class _AUD(Money):
    def __init__(self, amount: float):
        super().__init__(amount=str(int(amount * 10) / 10000), currency="AUD")


class SitePrice:
    def __init__(
        self,
        SiteId: int,
        FuelId: int,
        CollectionMethod: str,
        TransactionDateUtc: datetime,
        Price: float,
    ) -> None:
        """
        SitePrice returned ...
        :param SiteId: Unique Site ID
        :param FuelId: Unique Fuel Type ID
        :param CollectionMethod: This is will be "T" for South Australia as
               prices are collected by the Aggregator.
        :param TransactionDateUtc:
        :param Price: Price of the fuel in tenths of a cent
        """
        self.site_id = int(SiteId)
        self.fuel_id = int(FuelId)
        self.collection_method = str(CollectionMethod)
        try:
            self.transaction_date = datetime.strptime(
                TransactionDateUtc, "%Y-%m-%dT%H:%M:%S.%f"
            )
        except ValueError:
            self.transaction_date = datetime.strptime(
                TransactionDateUtc, "%Y-%m-%dT%H:%M:%S"
            )

        self.price = _AUD(Price)

    def __str__(self):
        return (
            f"SitePrice: site_id={self.site_id}, fuel_id={self.fuel_id}, "
            f"collection_method={self. collection_method}, "
            f"transaction_date={self.transaction_date}, "
            f"price={self.price.amount}"
        )
