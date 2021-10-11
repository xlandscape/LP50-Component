## Table of Contents
* [About the project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
  * [Inputs](#inputs)
  * [Outputs](#outputs)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)


## About the project
Calculates the LP50 for a margin of safety analysis.  
This is an automatically generated documentation based on the available code and in-line documentation. The current
version of this document is from 2021-10-11.  

### Built with
* Landscape Model core version 1.8
* MarginOfSafety R script version 1.1 


## Getting Started
The component can be used in any Landscape Model based on core version 1.8 or newer. See the Landscape
Model core's `README` for general tips on how to add a component to a Landscape Model.

### Prerequisites
A model developer that wants to add the `IndEffect_LP50_StepsRiverNetwork_SD_Species1` component to a Landscape Model needs to set up the general 
structure for a Landscape Model first. See the Landscape Model core's `README` for details on how to do so.

### Installation
1. Copy the `LP50` component into the `model\variant` sub-folder.
2. Make use of the component by including it into the model composition using `module=LP50` and 
   `class=LP50`. 


## Usage
The following gives a sample configuration of the `IndEffect_LP50_StepsRiverNetwork_SD_Species1` component. See [inputs](#inputs) and 
[outputs](#outputs) for further details on the component's interface.
```xml
<IndEffect_LP50_StepsRiverNetwork_SD_Species1 module="LP50" class="LP50" enabled_expression="'$(RunStepsRiverNetwork)'
== 'true' and '$(RunLGuts)' == 'true'">
    <ProcessingPath>
$(_MCS_BASE_DIR_)\$(_MC_NAME_)\processing\effect\ind_lp50_steps_sd_$(Species1)
    </ProcessingPath>
    <Values>
<FromOutput component="IndEffect_StepsRiverNetwork_SD_Species1" output="GutsSurvivalReaches" />
    </Values>
<MultiplicationFactors type="list[float]" unit="1">$(MultiplicationFactors)</MultiplicationFactors>
    <Reaches>
<FromOutput component="IndEffect_StepsRiverNetwork_SD_Species1" output="Reaches" />
    </Reaches>
    <SimulationStart
type="date">$(SimulationStart)</SimulationStart>
    <MinimumReportValue type="float" unit="1">0</MinimumReportValue>
<MaximumReportValue type="float" unit="1">100</MaximumReportValue>
    <ErrorReportValue type="float"
unit="1">-99</ErrorReportValue>
</IndEffect_LP50_StepsRiverNetwork_SD_Species1>
```

### Inputs
#### ProcessingPath
The working directory for the module. It is used for all files prepared as module inputs
or generated as (temporary) module outputs.  
`ProcessingPath` expects its values to be of type `str`.
Values of the `ProcessingPath` input may not have a physical unit.
Values have to refer to the `global` scale.

#### Values
The response values to which the regression function is fitted.  
`Values` expects its values to be of type `ndarray`.
The physical unit of the `Values` input values is `1`.
Values have to refer to the `time/year, space/base_geometry, other/factor` scale.

#### MultiplicationFactors
The applied multiplication factors leading to the different [#Values](#Values).  
`MultiplicationFactors` expects its values to be of type `list`.
The physical unit of the `MultiplicationFactors` input values is `1`.
Values have to refer to the `global` scale.

#### Reaches
The numeric identifiers for individual reaches (in the order of the [#Values](#Values) 
input) that apply scenario-wide.  
`Reaches` expects its values to be of type `list`.
Values have to refer to the `space/base_geometry` scale.

#### SimulationStart
The first time step for which values are provided.  
`SimulationStart` expects its values to be of type `date`.
Values have to refer to the `global` scale.

#### MinimumReportValue
If no convergence during fitting was achieved because all values were <0.1, this value is
reported instead.  
`MinimumReportValue` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `MinimumReportValue` input values is `1`.

#### MaximumReportValue
If no convergence during fitting was achieved because all values were >0.99, this value
is reported instead.  
`MaximumReportValue` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `MaximumReportValue` input values is `1`.

#### ErrorReportValue
If fitting was not possible because an error occurred, this value is reported.  
`ErrorReportValue` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `ErrorReportValue` input values is `1`.

### Outputs
#### LP50
The calculated LP50 values.  
Values are expectedly of type `ndarray`.
Individual array elements have a type of `float`.
Value representation is in a 2-dimensional array.
Dimension 1 spans the same years as the [Values](#Values) input.
Dimension 2 spans the same reaches as the [Values](#Values) input.
The values apply to the following scale: `time/year, space/base_geometry`.
The physical unit of the values is `1`.


## Roadmap
The following changes will be part of future `LP50` versions:
* Better error handling ([#2](https://gitlab.bayer.com/aqrisk-landscape/lp50-component/-/issues/2))


## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)). Also consult the `CONTRIBUTING` 
document for more information.


## License
Distributed under the CC0 License. See `LICENSE` for more information.


## Contact
Sascha Bub (component & module) - sascha.bub@gmx.de  
Thorsten Schad (component) - thorsten.schad@bayer.com  
Hans Baveco (module) - hans.baveco@wur.nl  


## Acknowledgements
* [data.table](https://cran.r-project.org/web/packages/data.table)  
* [NumPy](https://numpy.org)  
* [R](https://cran.r-project.org)  
* [drc](https://cran.r-project.org/web/packages/drc/index.html)  
