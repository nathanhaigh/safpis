from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from decimal import Decimal

import pytz
from dateutil import parser
from geopy.distance import geodesic
from money import Money


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
    GeoRegionParentId: int | None = field(default=None)


@dataclass
class Fuel:
    """Fuel returned ...
    :param FuelId: Unique Fuel Type ID
    :param Name: name of the Fuel Type
    """

    FuelId: int
    Name: str


@dataclass
class FuelStation:
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
        adl_tz = pytz.timezone("Australia/Adelaide")

        if isinstance(self.M, str):
            try:
                self.M = datetime.strptime(self.M, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=adl_tz)
            except ValueError:
                self.M = datetime.strptime(self.M, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=adl_tz)

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
                        datetime.strptime(value, "%H:%M").replace(tzinfo=adl_tz).time(),
                    )

    def distance(self, latitude: float, longitude: float):
        """Function to return a distance between the fuel station and a
        lat/long coordinate.
        :return: Distance object
        """
        return geodesic(
            (self.Lat, self.Lng),
            (latitude, longitude),
        )

    def is_open(self, date_time: datetime | None = None):
        adl_tz = pytz.timezone("Australia/Adelaide")

        if date_time is None:
            date_time = datetime.now(tz=adl_tz)

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
            and opening_hours[weekday][0] <= time <= opening_hours[weekday][1]
        ):
            return True

        return False


@dataclass
class FuelStationPrice:
    SiteId: int
    FuelId: int
    CollectionMethod: str
    TransactionDateUtc: str
    Price: Money

    def __post_init__(self):
        if isinstance(self.TransactionDateUtc, str):
            self.TransactionDateUtc = parser.parse(self.TransactionDateUtc)
        if isinstance(self.Price, float):
            self.Price = Money(
                amount=Decimal(str(self.Price)),
                currency="AUD",
            )
