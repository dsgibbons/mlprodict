"""
@brief      test tree node (time=30s)
"""
import os
import unittest
from pyquickhelper.loghelper import BufferedPrint
from pyquickhelper.pycode import ExtTestCase, get_temp_folder, skipif_circleci
from mlprodict.__main__ import main


class TestCliValidate(ExtTestCase):

    def test_cli_validate(self):
        st = BufferedPrint()
        main(args=["validate_runtime", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("verbose", res)

    def test_cli_validate_model(self):
        temp = get_temp_folder(__file__, "temp_validate_model")
        out1 = os.path.join(temp, "raw.xlsx")
        out2 = os.path.join(temp, "sum.xlsx")
        st = BufferedPrint()
        main(args=["validate_runtime", "--out_raw", out1,
                   "--out_summary", out2, "--models",
                   "LogisticRegression,LinearRegression",
                   '-o', '10', '-op', '10', '-v', '1', '-b', '1',
                   '-t', '{"1":{"number":10,"repeat":10},"10":{"number":5,"repeat":5}}'],
             fLOG=st.fprint)
        res = str(st)
        self.assertIn('Linear', res)
        self.assertExists(out1)
        self.assertExists(out2)

    def test_cli_validate_model_csv(self):
        temp = get_temp_folder(__file__, "temp_validate_model_csv")
        out1 = os.path.join(temp, "raw.csv")
        out2 = os.path.join(temp, "sum.csv")
        st = BufferedPrint()
        main(args=["validate_runtime", "--out_raw", out1,
                   "--out_summary", out2, "--models",
                   "LogisticRegression,LinearRegression",
                   '-o', '10', '-op', '10', '-v', '1', '-b', '1'],
             fLOG=st.fprint)
        res = str(st)
        self.assertIn('Linear', res)
        self.assertExists(out1)
        self.assertExists(out2)

    def test_cli_validate_model_csv_bug(self):
        temp = get_temp_folder(__file__, "temp_validate_model_csv_bug")
        out1 = os.path.join(temp, "raw.csv")
        out2 = os.path.join(temp, "sum.csv")
        st = BufferedPrint()
        main(args=["validate_runtime", "--out_raw", out1,
                   "--out_summary", out2, "--models",
                   "AgglomerativeClustering",
                   '-o', '10', '-op', '10', '-v', '1', '-b', '1'],
             fLOG=st.fprint)
        res = str(st)
        self.assertIn('AgglomerativeClustering', res)
        self.assertExists(out1)
        self.assertExists(out2)

    @skipif_circleci('too long')
    def test_cli_validate_model_lightgbm(self):
        temp = get_temp_folder(__file__, "temp_validate_model_lgbm_csv")
        out1 = os.path.join(temp, "raw.csv")
        out2 = os.path.join(temp, "sum.csv")
        st = BufferedPrint()
        main(args=["validate_runtime", "--out_raw", out1,
                   "--out_summary", out2, "--models",
                   "LGBMClassifier",
                   '-o', '10', '-op', '10', '-v', '1', '-b', '1',
                   '-dum', '1', '-du', temp],
             fLOG=st.fprint)
        res = str(st)
        self.assertIn('LGBMClassifier', res)
        self.assertExists(out1)
        self.assertExists(out2)
        exp1 = os.path.join(
            temp, "dump-ERROR-python-LGBMClassifier-default-b-cl--.pkl")
        exp2 = os.path.join(
            temp, "dump-i-python-LGBMClassifier-default-b-cl--.pkl")
        if not os.path.exists(exp1) and not os.path.exists(exp2):
            raise FileNotFoundError(
                "Unable to find '{}' or '{}'.".format(exp1, exp2))


if __name__ == "__main__":
    unittest.main()
