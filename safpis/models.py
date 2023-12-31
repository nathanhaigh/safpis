from datetime import datetime, time
import geopy.distance
from money import Money
from dataclasses import dataclass, field
from typing import Optional
from dateutil import parser
from decimal import Decimal


@dataclass
class Brand:
    """Brand returned ...
    :param BrandId: Unique Brand ID
    :param Name: Brand's name
    """

    BrandId: int
    Name: str


@dataclass
class Region:
    """Region returned ...
    :param GeoRegionId: Unique Region ID
    :param GeoRegionLevel: The Level (3 = State, 2 = City and 1 = Suburb)
    :param Name: Name of the Region
    :param Abbrev: Abbreviated form of the Region's Name
    :param GeoRegionParentId: ID of the Region's parent
    """

    GeoRegionId: int
    GeoRegionLevel: int
    Name: int
    Abbrev: str
    GeoRegionParentId: Optional[int] = field(default=None)


@dataclass
class Fuel:
    """Fuel returned ...
    :param FuelId: Unique Fuel Type ID
    :param Name: name of the Fuel Type
    """

    FuelId: int
    Name: str


@dataclass
class Site:
    S: int
    A: str
    N: str
    B: int
    P: int
    G1: int
    G2: int
    G3: int
    G4: int
    G5: int
    Lat: float
    Lng: float
    M: datetime
    GPI: str
    MO: time
    MC: time
    TO: time
    TC: time
    WO: time
    WC: time
    THO: time
    THC: time
    FO: time
    FC: time
    SO: time
    SC: time
    SUO: time
    SUC: time

    def __post_init__(self):
        if isinstance(self.M, str):
            try:
                self.M = datetime.strptime(self.M, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                self.M = datetime.strptime(self.M, "%Y-%m-%dT%H:%M:%S")

        for variable_name in [
            "MO",
            "MC",
            "TO",
            "TC",
            "WO",
            "WC",
            "THO",
            "THC",
            "FO",
            "FC",
            "SO",
            "SC",
            "SUO",
            "SUC",
        ]:
            value = getattr(self, variable_name, None)
            if value is not None:
                if value.strip() == "":
                    setattr(self, variable_name, None)
                else:
                    setattr(
                        self,
                        variable_name,
                        datetime.strptime(value, "%H:%M").time(),
                    )

    def distance_between(self, latitude: float, longitude: float):
        """Function to return a distance between the site and a lat/long
        coordinate.
        :return: Distance object
        """
        distance = geopy.distance.geodesic(
            (self.Lat, self.Lng),
            (latitude, longitude),
        )
        return distance

    def is_open(self, date_time: datetime = None):
        if date_time is None:
            date_time = datetime.now()

        opening_hours = {
            "Monday": (self.MO, self.MC),
            "Tuesday": (self.TO, self.TC),
            "Wednesday": (self.WO, self.WC),
            "Thursday": (self.THO, self.THC),
            "Friday": (self.FO, self.FC),
            "Saturday": (self.SO, self.SC),
            "Sunday": (self.SUO, self.SUC),
        }

        weekday = date_time.strftime("%A")
        time = date_time.time()

        if (
            opening_hours[weekday][0] is not None
            and opening_hours[weekday][1] is not None
        ):
            if opening_hours[weekday][0] <= time <= opening_hours[weekday][1]:
                return True

        return False


@dataclass
class SitePrice:
    SiteId: int
    FuelId: int
    CollectionMethod: str
    TransactionDateUtc: str
    Price: float

    def __post_init__(self):
        if isinstance(self.TransactionDateUtc, str):
            self.TransactionDateUtc = parser.parse(self.TransactionDateUtc)
        if isinstance(self.Price, float):
            self.Price = Money(
                amount=Decimal(str(self.Price)),
                currency="AUD",
            )
