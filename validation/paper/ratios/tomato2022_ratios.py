import os
import cobra
from tests import TEST_DIR
from cobra.flux_analysis import pfba
import pandas as pd


def validate_ratios(original_model, diel_model):
    original_model.objective = "EX_photon_h"
    original_model.objective_direction = "max"

    original_carboxylation = original_model.reactions.get_by_id("RBPCh")
    original_oxygenation = original_model.reactions.get_by_id("RBCh_1")

    same_flux = original_model.problem.Constraint(
        original_carboxylation.flux_expression * 1 -
        original_oxygenation.flux_expression * 3, lb=0, ub=0)
    original_model.add_cons_vars(same_flux)

    original_solution = pfba(original_model).fluxes

    diel_model.objective = "EX_photon_h_Day"
    diel_model.objective_direction = "max"

    diel_carboxylation_day = diel_model.reactions.get_by_id("RBPCh_Day")
    diel_oxygenation_day = diel_model.reactions.get_by_id("RBCh_1_Day")

    same_flux = diel_model.problem.Constraint(
        diel_carboxylation_day.flux_expression * 1 -
        diel_oxygenation_day.flux_expression * 3, lb=0, ub=0)
    diel_model.add_cons_vars(same_flux)

    diel_carboxylation_night = diel_model.reactions.get_by_id("RBPCh_Night")
    diel_oxygenation_night = diel_model.reactions.get_by_id("RBCh_1_Night")

    same_flux = diel_model.problem.Constraint(
        diel_carboxylation_night.flux_expression * 1 -
        diel_oxygenation_night.flux_expression * 3, lb=0, ub=0)
    diel_model.add_cons_vars(same_flux)

    diel_solution = pfba(diel_model).fluxes

    data = {'Carboxylation/Oxygenation': [original_solution["RBPCh"] / original_solution["RBCh_1"],
                                          diel_solution["RBPCh_Day"] / diel_solution["RBCh_1_Day"],
                                          diel_solution["RBPCh_Night"] / diel_solution["RBCh_1_Night"]]}
    tabel = pd.DataFrame(data)

    tabel.index = ["Tomato2022", "Day Tomato2022", "Night Tomato2022"]

    print(tabel)


if __name__ == '__main__':
    original_model = cobra.io.read_sbml_model(os.path.join(TEST_DIR, 'models', 'tomato_Sl2183.xml'))
    diel_model = cobra.io.read_sbml_model(os.path.join(TEST_DIR, 'models', "diel_tomato2022_model.xml"))

    validate_ratios(original_model, diel_model)
