from unittest import TestCase
from util.Import_WRF_CSV import *

__author__ = 'Alex Zylstra'


class TestWRF_CSV(TestCase):
    """Test the import of analysis program generated CSV files."""

    def test_All(self):
        """Test all of the retrieved data against known values"""
        path = os.path.dirname(__file__)
        file = os.path.join(path, "N130520-002-999_WRF_Pos1_3_13425888_AL_13511794_S1_40x_5hr_ANALYSIS.CSV")
        w = WRF_CSV(file)

        self.assertEqual(w.date, '2013-06-10')
        self.assertEqual(w.time, '08:32')
        self.assertEqual(w.program_date, '2013-06-07')
        self.assertEqual(w.scan_file, 'N130520-002-999_WRF_Pos1_3_13425888_AL_13511794_S1_40x_5hr')
        self.assertEqual(w.port, 'pos1_3')
        self.assertEqual(w.distance, 50)
        self.assertEqual(w.WRF_ID, '13425888-g058')
        self.assertEqual(w.CR39_ID, '13511794')
        self.assertEqual(w.Al_Blast_Filter, 0)
        self.assertEqual(w.WRF_Cal, 'cal13.0225')
        self.assertTupleEqual(w.Data_Limits, (0, 89, 0, 63))
        self.assertTupleEqual(w.BG1_Limits, (0, 13, 0, 63))
        self.assertTupleEqual(w.BG2_Limits, (39, 61, 0, 63))
        self.assertTupleEqual(w.Dia_Limits, (5.61, 16.75))
        self.assertEqual(w.Dia_Auto, True)
        self.assertTupleEqual(w.E_Limits, (1.0, 4.0))
        self.assertEqual(w.c, 1.203)
        self.assertEqual(w.dc, 0.086)
        self.assertEqual(w.chi2, 1.32)
        self.assertTupleEqual(w.Fit_Limits, (7.5, 10.0))
        self.assertTupleEqual(w.Fit, (8.799, 0.573, 4.027e7))
        self.assertTupleEqual(w.Unc_Random, (0.216, 0.027, 10868872.999999998))
        self.assertTupleEqual(w.Unc_Systematic, (0.147, 0, 0))
        self.assertTupleEqual(w.Unc_CountingStats, (0.036, 0.021, 2388011.0))
        self.assertTupleEqual(w.Unc_DvE, (0.091, 0.015, 10522550.999999998))
        self.assertTupleEqual(w.Unc_Dmax, (0.065, 0, 1328910.0))
        self.assertTupleEqual(w.Unc_EtchScan, (0.127, 0.007, 0))
        self.assertTupleEqual(w.Unc_Nonlinearity, (0.020, 0., 0))
        self.assertTupleEqual(w.Unc_CalProc, (0.128, 0, 0))

        # spectrum, just check # rows:
        self.assertEqual(len(w.spectrum), 63)