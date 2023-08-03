
class Experiment(object):
    """
    Represents a spatial carbon experiment
    """

    def __init__(self, project_name: str, use_case: str) -> None:
        self._project_name = project_name
        self._use_case = use_case

    @property
    def project_name(self):
        return self._project_name

    @property
    def use_case(self):
        return self._use_case
    
    def create_tracker_name(self):
        """
        Returns a tracker name using the project name and the use case.
        """
        return f"{self._project_name} - {self._use_case}"