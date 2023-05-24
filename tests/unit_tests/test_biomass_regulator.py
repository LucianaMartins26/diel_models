import os
import copy
from unittest import TestCase

import cobra

from diel_models.biomass_regulator import BiomassAdjuster
from tests import TEST_DIR


class TestBiomassRegulator(TestCase):

    def test_reset_boundaries(self):
        diel_sp_no_night_photon_model = os.path.join(TEST_DIR, "data",
                                                     "Diel_AraGEM_sp_photon_restricted.xml")
        diel_model = cobra.io.read_sbml_model(diel_sp_no_night_photon_model)
        diel_model_copy = copy.deepcopy(diel_model)

        biomass_adjuster = BiomassAdjuster(diel_model_copy, "BIO_L_Day", "BIO_L_Night",
                                           ["R03845_c_Night", "R07856_c_Night"])
        biomass_adjuster.reset_boundaries()

        for id_reaction in ["R03845_c_Night", "R07856_c_Night"]:
            reaction = diel_model_copy.reactions.get_by_id(id_reaction)
            self.assertEqual(reaction.lower_bound, 0)
            self.assertEqual(reaction.upper_bound, 0)

    def test_reset_boundaries_with_invalid_photosynthesis_reaction(self):
        diel_sp_no_night_photon_model = os.path.join(TEST_DIR, "data",
                                                     "Diel_AraGEM_sp_photon_restricted.xml")
        diel_model = cobra.io.read_sbml_model(diel_sp_no_night_photon_model)
        diel_model_copy = copy.deepcopy(diel_model)

        biomass_adjuster = BiomassAdjuster(diel_model_copy, "BIO_L_Day", "BIO_L_Night",
                                           ["R03845_c_Night", "Invalid"])

        with self.assertRaises(ValueError):
            biomass_adjuster.reset_boundaries()

    def test_total_biomass_reaction(self):
        diel_sp_no_night_photon_model = os.path.join(TEST_DIR, "data",
                                                     "Diel_AraGEM_sp_photon_restricted.xml")
        diel_model = cobra.io.read_sbml_model(diel_sp_no_night_photon_model)
        diel_model_copy = copy.deepcopy(diel_model)

        biomass_adjuster = BiomassAdjuster(diel_model_copy, "BIO_L_Day", "BIO_L_Night",
                                           ["R03845_c_Night", "R07856_c_Night"])
        biomass_adjuster.reset_boundaries()
        biomass_adjuster.total_biomass_reaction()

        biomass_after = diel_model_copy.reactions.get_by_id("Biomass_Total")
        biomass_before = diel_model.reactions.get_by_id("BIO_L_Night")

        self.assertEqual(2 * (len(biomass_before.reactants)), len(biomass_after.reactants))
        self.assertEqual(2 * (len(biomass_before.products)), len(biomass_after.products))
        self.assertEqual(2 * (len(biomass_before.metabolites)), len(biomass_after.metabolites))

        self.assertIn('Biomass_Total', str(diel_model_copy.objective.expression))

    def test_total_biomass_with_invalid_biomass_reaction(self):
        diel_sp_no_night_photon_model = os.path.join(TEST_DIR, "data",
                                                     "Diel_AraGEM_sp_photon_restricted.xml")
        diel_model = cobra.io.read_sbml_model(diel_sp_no_night_photon_model)
        diel_model_copy = copy.deepcopy(diel_model)

        biomass_adjuster = BiomassAdjuster(diel_model_copy, "BIO_L_Day", "Invalid",
                                           ["R03845_c_Night", "R07856_c_Night"])

        with self.assertRaises(ValueError):
            biomass_adjuster.total_biomass_reaction()
