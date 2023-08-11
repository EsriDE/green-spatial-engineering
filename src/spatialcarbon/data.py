from codecarbon.viz.data import Data
import pandas as pd



def get_print_emissions(carbon_equivalent: float) -> str:
    """
    Returns a text representation providing exemplary equivalents from daily life.
    """
    emissions_stats = Data()
    return f"{emissions_stats.get_household_fraction(carbon_equivalent)} % of weekly American household emissions \
    \t{emissions_stats.get_car_miles(carbon_equivalent)} miles driven \
    \t{emissions_stats.get_tv_time(carbon_equivalent)} of 32-inch LCD TV watched"

def get_summary_emissions(filepath: str) -> str:
    """
    Reads the emissions data and summarizes each project providing exemplary equivalents from daily life.
    """
    emissions_df = pd.read_csv(filepath)
    overall_emissions_df = emissions_df.groupby(["project_name"])["emissions"].sum().reset_index()
    for _, emission_row in overall_emissions_df.iterrows():
        yield ""
        yield "-" * len(emission_row['project_name'])
        yield f"{emission_row['project_name']}"
        yield "-" * len(emission_row['project_name'])
        yield f"{get_print_emissions(emission_row['emissions'])}"