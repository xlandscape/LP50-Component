"""
Landscape Model component of the LP50 module.
"""
import numpy as np
import os
import base
import attrib
import datetime


class LP50(base.Component):
    """
    Calculates the LP50 for a margin of safety analysis.
    """
    # RELEASES
    VERSION = base.VersionCollection(
        base.VersionInfo("2.1.1", "2021-09-17"),
        base.VersionInfo("2.1.0", "2021-09-09"),
        base.VersionInfo("2.0.4", "2021-08-24"),
        base.VersionInfo("2.0.3", "2021-08-05"),
        base.VersionInfo("2.0.2", "2021-07-16"),
        base.VersionInfo("2.0.1", "2020-12-03"),
        base.VersionInfo("2.0.0", "2020-10-22"),
        base.VersionInfo("1.4.0", None)
    )

    # AUTHORS
    VERSION.authors.extend((
        "Sascha Bub (component & module) - sascha.bub@gmx.de",
        "Thorsten Schad (component) - thorsten.schad@bayer.com",
        "Hans Baveco (module) - hans.baveco@wur.nl"
    ))

    # ACKNOWLEDGEMENTS
    VERSION.acknowledgements.extend((
        "[data.table](https://cran.r-project.org/web/packages/data.table)",
        "[NumPy](https://numpy.org)",
        "[R](https://cran.r-project.org)",
        "[drc](https://cran.r-project.org/web/packages/drc/index.html)"
    ))

    # ROADMAP
    VERSION.roadmap.extend((
        "Better error handling ([#2](https://gitlab.bayer.com/aqrisk-landscape/lp50-component/-/issues/2))",
    ))

    # CHANGELOG
    VERSION.added("1.4.0", "components.LP50 component")
    VERSION.changed("2.0.0", "First independent release")
    VERSION.added("2.0.1", "Changelog and release history")
    VERSION.added("2.0.2", ".gitignore")
    VERSION.changed("2.0.3", "Scale of `Reaches` input")
    VERSION.added("2.0.4", "Base documentation")
    VERSION.added("2.1.0", "Updated runtime environment to R version 4.1.1")
    VERSION.added("2.1.1", "Make use of generic types for class attributes")

    def __init__(self, name, observer, store):
        super(LP50, self).__init__(name, observer, store)
        self._module = base.Module("MarginOfSafety R script", "1.1")
        self._inputs = base.InputContainer(self, [
            base.Input(
                "ProcessingPath",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The working directory for the module. It is used for all files prepared as module inputs
                or generated as (temporary) module outputs."""
            ),
            base.Input(
                "Values",
                (
                    attrib.Class(np.ndarray, 1),
                    attrib.Unit("1", 1),
                    attrib.Scales("time/year, space/base_geometry, other/factor", 1)
                ),
                self.default_observer,
                description="The response values to which the regression function is fitted."
            ),
            base.Input(
                "MultiplicationFactors",
                (attrib.Class(list[float], 1), attrib.Unit("1", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The applied multiplication factors leading to the different [#Values](#Values)."
            ),
            base.Input(
                "Reaches",
                (attrib.Class(list[int], 1), attrib.Scales("space/base_geometry", 1)),
                self.default_observer,
                description="""The numeric identifiers for individual reaches (in the order of the [#Values](#Values) 
                input) that apply scenario-wide."""
            ),
            base.Input(
                "SimulationStart",
                (attrib.Class(datetime.date, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The first time step for which values are provided."
            ),
            base.Input(
                "MinimumReportValue",
                (attrib.Class(float, 1), attrib.Scales("global", 1), attrib.Unit("1")),
                self.default_observer,
                description="""If no convergence during fitting was achieved because all values were <0.1, this value is
                reported instead."""
            ),
            base.Input(
                "MaximumReportValue",
                (attrib.Class(float, 1), attrib.Scales("global", 1), attrib.Unit("1")),
                self.default_observer,
                description="""If no convergence during fitting was achieved because all values were >0.99, this value
                is reported instead."""
            ),
            base.Input(
                "ErrorReportValue",
                (attrib.Class(float, 1), attrib.Scales("global", 1), attrib.Unit("1")),
                self.default_observer,
                description="If fitting was not possible because an error occurred, this value is reported."
            )
        ])
        self._outputs = base.OutputContainer(self, [
            base.Output(
                "LP50",
                store,
                self,
                {"scales": "time/year, space/base_geometry", "unit": "1"},
                "The calculated LP50 values.",
                {
                    "type": np.ndarray,
                    "data_type": np.float,
                    "shape": (
                        "the same years as the [Values](#Values) input",
                        "the same reaches as the [Values](#Values) input"
                    )
                }
            )
        ])
        return

    def run(self):
        """
        Runs the component.
        :return: Nothing.
        """
        processing_path = self._inputs["ProcessingPath"].read().values
        reaches = np.array(self._inputs["Reaches"].read().values)
        simulation_start = self._inputs["SimulationStart"].read().values
        self.prepare_module_inputs(processing_path, reaches, simulation_start)
        self.run_module(processing_path)
        self.read_module_outputs(processing_path, reaches, simulation_start)
        return

    def prepare_module_inputs(self, processing_path, reaches, simulation_start):
        """
        Prepares the input data required by the LP50 module.
        :param: processing_path: The working directory used by the module.
        :param: reaches: The identifiers of the reaches being processed.
        :param: simulation_start: The first day of the simulation.
        :return: Nothing.
        """
        os.makedirs(processing_path)
        effects = self._inputs["Values"].read().values
        multiplication_factors = self._inputs["MultiplicationFactors"].read().values
        with open(os.path.join(processing_path, "values.csv"), "w") as f:
            f.write("year,reach,factor,value\n")
            for index, value in np.ndenumerate(effects):
                f.write("{},{},{},{}\n".format(
                    simulation_start.year + index[0],
                    reaches[index[1]],
                    multiplication_factors[index[2]],
                    value)
                )
        return

    def run_module(self, processing_path):
        """
        Runs the module.
        :param: processing_path: The working directory of the module.
        :return: Nothing.
        """
        base.run_process(
            (
                os.path.join(os.path.dirname(__file__), "R-4.1.1", "bin", "x64", "RScript.exe"),
                "--vanilla",
                os.path.join(os.path.dirname(__file__), "MarginOfSafety.R"),
                os.path.join(processing_path, "values.csv"),
                os.path.join(processing_path, "lp50.csv")
            ),
            processing_path,
            self.default_observer
        )
        return

    def read_module_outputs(self, processing_path, reaches, simulation_start):
        """
        Reads the module's outputs and stores them in the Landscape model store.
        :param: processing_path: The working directory of the module.
        :param: reaches: The identifiers of the reaches considered.
        :param: simulation_start: The first day of the simulation.
        :return: Nothing.
        """
        minimum_report_value = self._inputs["MinimumReportValue"].read().values
        maximum_report_value = self._inputs["MaximumReportValue"].read().values
        error_report_value = self._inputs["ErrorReportValue"].read().values
        lp50 = np.zeros((self._inputs["Values"].describe()["shape"][:2]))
        with open(os.path.join(processing_path, "lp50.csv")) as f:
            data = f.readlines()
        for record in [x[:-1].split(",") for x in data[1:]]:
            time_index = simulation_start.year - int(record[0])
            space_index = np.argwhere(reaches == int(record[1]))[0][0]
            value = float(record[2])
            if value == -997:
                value = minimum_report_value
            elif value == -998:
                value = maximum_report_value
            elif value == -999:
                value = error_report_value
            lp50[time_index, space_index] = value
        self._outputs["LP50"].set_values(lp50)
        return
