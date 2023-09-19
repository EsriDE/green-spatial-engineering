from enum import Enum


class CarSize(Enum):
    UNKNOWN = 0,
    SMALL = 1,
    MEDIUM = 2,
    LARGE = 3,
    AVERAGE = 4



class Car(object):

    def __init__(self, car_size: CarSize = CarSize.AVERAGE) -> None:
        self._car_size = car_size

    @property
    def carbon_equivalent(self) -> float:
        """
        Returns the total emissions in kg CO2E per kilometer
        """
        return 0.17067 



class DieselCar(Car):

    def __init__(self, car_size: CarSize = CarSize.AVERAGE) -> None:
        super().__init__(car_size)

    @property
    def carbon_equivalent(self) -> float:
        """
        Returns the total emissions in kg CO2E per kilometer
        """
        if CarSize.SMALL == self._car_size:
            return 0.139894
        
        return 0.170824
    