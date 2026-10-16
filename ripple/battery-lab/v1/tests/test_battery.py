"""Independent mathematical and measurement tests; no hardware claimed."""
import math
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battery_core import (FARADAY_C_PER_MOL, theoretical_calcium_charge,
    reversible_chemical_energy, nernst_voltage, ionic_resistance,
    diffusion_current_ceiling, symmetric_butler_volmer_overpotential,
    read_measurements, analyze_measurements, literature_proxy, Sample)

class BatteryCoreTests(unittest.TestCase):
    def test_faraday_from_exact_constants(self):
        self.assertAlmostEqual(FARADAY_C_PER_MOL,96485.33212331,places=6)
    def test_two_electrons_per_calcium(self):
        x=theoretical_calcium_charge(40.078)
        self.assertAlmostEqual(x["charge_coulomb_theoretical"],2*FARADAY_C_PER_MOL,places=6)
        self.assertAlmostEqual(x["capacity_mAh_theoretical"],2*FARADAY_C_PER_MOL/3.6,places=6)
        self.assertAlmostEqual(x["specific_mAh_g_theoretical"],1337.466,delta=0.005)
    def test_reversible_voltage(self):
        x=reversible_chemical_energy(-2*FARADAY_C_PER_MOL*1.7,2)
        self.assertAlmostEqual(x["reversible_voltage_V"],1.7,places=12)
    def test_nernst_at_unit_quotient(self):
        self.assertEqual(nernst_voltage(1.7,2,298.15,1.0),1.7)
    def test_nernst_decade(self):
        a=nernst_voltage(1.7,2,298.15,10)
        self.assertAlmostEqual(a,1.7-0.02958,delta=0.0001)
    def test_bulk_ohmic_from_published_conductivity(self):
        # 5.3 mS/cm = 0.53 S/m; geometry synthetic 100um/1cm2.
        r=ionic_resistance(1e-4,1e-4,0.53)["ohm"]
        self.assertAlmostEqual(r,1/0.53,places=9)
    def test_diffusion_flux_and_charge(self):
        d=diffusion_current_ceiling(1e-4,1e-10,1000,1e-4)
        self.assertAlmostEqual(d["max_current_A_model"], 2*FARADAY_C_PER_MOL*1e-7,places=9)
    def test_butler_volmer_zero_and_symmetry(self):
        self.assertEqual(symmetric_butler_volmer_overpotential(0,1,298.15),0)
        p=symmetric_butler_volmer_overpotential(.1,1,298.15)
        self.assertAlmostEqual(-p,symmetric_butler_volmer_overpotential(-.1,1,298.15))
    def test_exact_constant_voltage_capacity_and_energy(self):
        s=[Sample(0,2,1,"charge")]
        # This invented sign inconsistency is not used; construct valid synthetic cycle
        s=[Sample(0,3,-1,"charge"),Sample(3600,3,-1,"charge"),
           Sample(3601,2,1,"discharge"),Sample(7201,2,1,"discharge")]
        a=analyze_measurements(s)
        self.assertAlmostEqual(a["charge"]["Ah"],1)
        self.assertAlmostEqual(a["charge"]["Wh"],3)
        self.assertAlmostEqual(a["discharge"]["Ah"],1)
        self.assertAlmostEqual(a["discharge"]["Wh"],2)
        self.assertAlmostEqual(a["coulombic_efficiency"],1)
        self.assertAlmostEqual(a["energy_efficiency"],2/3)
        self.assertEqual(a["discharge"]["segments"],1)
    def test_different_phase_segments_not_integrated(self):
        s=[Sample(0,2,1,"discharge"),Sample(100,2,0,"rest"),Sample(300,3,-1,"charge")]
        m=analyze_measurements(s)
        self.assertEqual(m["discharge"]["Ah"],0)
        self.assertIsNone(m["coulombic_efficiency"])
    def test_voltage_integral_not_average_voltage_times_total_current_when_correlated(self):
        s=[Sample(0,1,1,"discharge"),Sample(3600,3,3,"discharge")]
        m=analyze_measurements(s)
        self.assertAlmostEqual(m["discharge"]["Ah"],2)
        self.assertAlmostEqual(m["discharge"]["Wh"],5)
    def test_reject_bad_sign_and_nonmonotonic(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.csv"
            p.write_text("time_s,voltage_v,current_a,phase\n0,2,-1,discharge\n1,2,-1,discharge\n")
            with self.assertRaisesRegex(ValueError,"Discharge current"):
                read_measurements(p)
            p.write_text("time_s,voltage_v,current_a,phase\n0,2,1,discharge\n0,2,1,discharge\n")
            with self.assertRaisesRegex(ValueError,"strictly increase"):
                read_measurements(p)
    def test_numeric_input_guards(self):
        for f,args in [(theoretical_calcium_charge,(-1,)),(ionic_resistance,(1,0,1)),(nernst_voltage,(1,2,298,0))]:
            with self.assertRaises(ValueError): f(*args)
    def test_literature_cathode_only(self):
        x=literature_proxy(105,1.7)
        self.assertAlmostEqual(x["cathode_active_specific_energy_Wh_kg_rectangular_estimate"],178.5)
        self.assertIn("NOT reported measured",x["scope"])

if __name__=='__main__':unittest.main()
