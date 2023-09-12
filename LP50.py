"""Landscape Model component of the LP50 module."""
import numpy as np
import os
import base
import attrib
import datetime


class LP50(base.Component):
    """Calculates the LP50 for a margin of safety analysis."""
    # RELEASES
    VERSION = base.VersionCollection(
        base.VersionInfo("2.2.6", "2023-09-12"),
        base.VersionInfo("2.2.5", "2023-09-11"),
        base.VersionInfo("2.2.4", "2021-12-10"),
        base.VersionInfo("2.2.3", "2021-11-18"),
        base.VersionInfo("2.2.2", "2021-10-19"),
        base.VersionInfo("2.2.1", "2021-10-12"),
        base.VersionInfo("2.2.0", "2021-10-12"),
        base.VersionInfo("2.1.2", "2021-10-11"),
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
    VERSION.roadmap.extend(())

    # CHANGELOG
    VERSION.added("1.4.0", "components.LP50 component")
    VERSION.changed("2.0.0", "First independent release")
    VERSION.added("2.0.1", "Changelog and release history")
    VERSION.added("2.0.2", ".gitignore")
    VERSION.changed("2.0.3", "Scale of `Reaches` input")
    VERSION.added("2.0.4", "Base documentation")
    VERSION.added("2.1.0", "Updated runtime environment to R version 4.1.1")
    VERSION.added("2.1.1", "Make use of generic types for class attributes")
    VERSION.added("2.1.2", "Replaced legacy format strings by f-strings")
    VERSION.fixed("2.2.0", "Added missing R-package dependencies")
    VERSION.fixed("2.2.1", "Added further missing R-package dependencies")
    VERSION.fixed("2.2.2", "Specified R library path")
    VERSION.changed("2.2.2", "Switched to Google-style docstrings")
    VERSION.changed("2.2.3", "Removed multiplication factor and reaches inputs")
    VERSION.changed("2.2.3", "Reports element names of outputs")
    VERSION.changed("2.2.4", "Specifies offset of outputs")
    VERSION.added("2.2.5", "Information on runtime environment")
    VERSION.changed("2.2.6", "Extended module information for R runtime environment")
    VERSION.added("2.2.6", "Creation of repository info during documentation")
    VERSION.added("2.2.6", "Repository info to R runtime environment")

    def __init__(self, name, observer, store):
        """
        Initializes a LP50 component.

        Args:
            name: The name of the component.
            observer: The default observer of the component.
            store: The default store of the component.
        """
        super(LP50, self).__init__(name, observer, store)
        self._module = base.Module("R", "4.1.1", "R-4.1.1", "R-4.1.1/README", None, True, "R-4.1.1/doc/NEWS")
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

        Returns:
            Nothing.
        """
        processing_path = self._inputs["ProcessingPath"].read().values
        reaches = self.inputs["Values"].describe()["element_names"][1]
        simulation_start = self._inputs["SimulationStart"].read().values
        self.prepare_module_inputs(processing_path, reaches.get_values(), simulation_start)
        self.run_module(processing_path)
        self.read_module_outputs(processing_path, reaches, simulation_start)
        return

    def prepare_module_inputs(self, processing_path, reaches, simulation_start):
        """
        Prepares the input data required by the LP50 module.

        Args:
            processing_path: The working directory used by the module.
            reaches: The identifiers of the reaches being processed.
            simulation_start: The first day of the simulation.

        Returns:
            Nothing.
        """
        os.makedirs(processing_path)
        effects = self._inputs["Values"].read().values
        multiplication_factors = self.inputs["Values"].describe()["element_names"][2].get_values()
        with open(os.path.join(processing_path, "values.csv"), "w") as f:
            f.write("year,reach,factor,value\n")
            for index, value in np.ndenumerate(effects):
                f.write(
                    f"{simulation_start.year + index[0]},{reaches[index[1]]},{multiplication_factors[index[2]]},"
                    f"{value}\n"
                )
        return

    def run_module(self, processing_path):
        """
        Runs the module.

        Args:
            processing_path: The working directory of the module.

        Returns:
            Nothing.
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
            self.default_observer,
            {"R_LIBS_USER": os.path.join(os.path.dirname(__file__), "R-4.1.1", "library")}
        )
        return

    def read_module_outputs(self, processing_path, reaches, simulation_start):
        """
        Reads the module's outputs and stores them in the Landscape model store.

        Args:
            processing_path: The working directory of the module.
            reaches: The identifiers of the reaches considered.
            simulation_start: The first day of the simulation.

        Returns:
            Nothing.
        """
        minimum_report_value = self._inputs["MinimumReportValue"].read().values
        maximum_report_value = self._inputs["MaximumReportValue"].read().values
        error_report_value = self._inputs["ErrorReportValue"].read().values
        lp50 = np.zeros((self._inputs["Values"].describe()["shape"][:2]))
        reach_ids = list(reaches.get_values())
        with open(os.path.join(processing_path, "lp50.csv")) as f:
            data = f.readlines()
        for record in [x[:-1].split(",") for x in data[1:]]:
            time_index = simulation_start.year - int(record[0])
            space_index = reach_ids.index(int(record[1]))
            value = float(record[2])
            if value == -997:
                value = minimum_report_value
            elif value == -998:
                value = maximum_report_value
            elif value == -999:
                value = error_report_value
            lp50[time_index, space_index] = value
        self._outputs["LP50"].set_values(lp50, element_names=(None, reaches), offset=(simulation_start.year, None))
        return
