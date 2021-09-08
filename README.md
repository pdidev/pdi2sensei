**[Installation](#installation)** |
**[Example](#example)** |
**[Integrate pdi2sensei](#integrate-pdi2sensei)** |
**[Execution](#execution)** |
**[Getting help](#getting-help)** |

# [pdi2sensei](https://github.com/pdidev/pdi2sensei)


The goal of pdi2sensei is to enable simulations easier use of in situ methods. This goal is approached by using [ PDI ](https://pdi.julien-bigot.fr/master/) as the interface that is included in the simulation code. Afterward, this interface can be used to specify different I/O operations and enable in situ using pdi2sensei. These changes can be made in a separate file, that can be changed after building the simulation.

Using pdi2sensei removes the direct dependencies of the simulation code to the in situ libraries, reducing the difficulties for the simulation development. Furthermore, pdi2sensei employs an in transit model, therefore transporting the data to a different node, before doing the actual visualization on those extra nodes. To have a flexible solution with good transport mechanisms we use different libraries like [ SENSEI ](https://github.com/SENSEI-insitu/SENSEI) and  [ ADIOS2 ](https://adios2.readthedocs.io/en/latest/introduction/introduction.html). This may sound like a counterintuitive solution to make it easier, but in pdi2sensei we set the data transport and in situ visualization with [Catalyst from ParaView]((https://www.paraview.org/in-situ/)) as the default, so there is no need to make changes there, so this complexity does not touch the end-user.

PDI (PDI data interface) is a library interface for multiple different I/O libraries. PDI allows users to customize the data output of the simulation via a configuration file without recompiling the simulation or needing those libraries at build time. Here we are using PDI as our interface to the simulation and include an in transit / in situ solution as our PDI I/O configuration.

The following overview shows all the components, that are used in the default configuration:

<p align="center">
<img src=docs/overview.png title="Overview over all the components used for the Setup with two different jobs, one for the simulation and one for the visualization Endpoint" width="600" style="float:center"/>
</p>

Here you can see the in transit nature of this setup. In a High-Performance Computing(HPC) setting, you could run two jobs, one will run your simulation, while the other job (called endpoint) accepts the data from your simulation and processes it using those compute resources. 

Because pdi2sensei uses SENSEI as a middle layer, it is possible to change the used in situ libraries. The default way data leaves SENSEI, in this case, is one time through ADIOS2 and the other time through ParaView Catalyst. Using SENSEI with a different library needs a SENSEI build with support for that software, for example, LibSim support to use Visit.

---

## Installation

You will need to download [ pdi2sensei ](https://github.com/pdidev/pdi2sensei) and add it to your `PYTHONPATH`. Then it is avaiable to be used, but there are further dependencies, needed to build and use a simulation with this setup.

### Build dependencies for simulation

 - The build instructions for PDI can be found [ here ](https://pdi.julien-bigot.fr/master/Installation.html). You will need PDI at least in version 1.2.2, to have all the needed bug fixes.


### Runtime dependencies

For actually running a simulation with pdi2sensei, there are additional requirements:
- You will need [ ADIOS2 ](https://adios2.readthedocs.io/en/latest/setting_up/setting_up.html) with at least `ADIOS2_USE_SST` enabled.
- Additionally, you will need [ ParaView ](https://github.com/Kitware/ParaView/blob/master/Documentation/dev/build.md) with Catalyst support, enabling `PARAVIEW_CATALYST` and `PARAVIEW_CATALYST_PYTHON`.
  - The last official Sensei release (v3.2.1) only supports up ParaView 5.7
  - Support for newer versions of ParaView is already available in the [development branch](https://github.com/SENSEI-insitu/SENSEI/tree/develop) of sensei
- Furthermore [ Sensei ](https://github.com/SENSEI-insitu/SENSEI)  is needed. You will need to build Sensei, which has ADIOS2 and ParaView Catalyst enabled. Therefore setting `ENABLE_CATALYST`, `ENABLE_CATALYST_PYTHON` and `ENABLE_ADIOS2`. Sensei offers ADIOS2 support starting with version 3.2.0.
- As the last dependency you will need to download [ pdi2sensei ](https://github.com/pdidev/pdi2sensei) and add it to your `PYTHONPATH`



## Example

Running example on Jureca with live interactive visualization:

- Start ParaView 5.8
  - open port to accept Catalyst connection
- Change `example/allinputsgridwriter.py:102`
  - set the node name of the node running ParaView
  - change the port if ParaView is not listening on port 22222
- execute `example/run_example.sh` 
  - needs to be on a node where srun can be used
  - needs to be able to access open port of node running ParaView


## Integrate pdi2sensei

If you want to use pdi2sensei for your code a couple of steps need to be done:

- Install / load the dependencies of pdi2sensei
- [Include PDI in your simulation code](https://pdi.julien-bigot.fr/master/Hands_on.html)
- Write a configuration file for PDI that includes passing on the data to pdi2sensei
  - examples of a configuration file can be found in the `example/` folder
  - The configuration file should include:
    - A call to the pycall plugin
    - import pdi2sensei
    - initilize pdi2sensei Bridge
    - set a VTK mesh, describing the spatial distribution of your data (for common cases there are functions in pdi2sensei.utility to help with generating these meshes)
    - add the mesh to your bridge
    - add an event or data share from your simulation to add the data to the bridge
    - call the method execute from your bridge class
- Setup the visualization pipeline you wish to use with the [ParaView GUI(see Chapter 2.2)](https://www.mn.uio.no/astro/english/services/it/help/visualization/paraview/paraviewcatalystguide-5.8.1.pdf) and export it as a Catalyst script


## Execution

- The simulation is started normally, but pdi2sensei, SENSEI, and ADIOS2 need to be available in `LD_LIBRARY_PATH` and `PYTHONPATH`
- The Endpoint is started as a second job, here we need pdi2sensei, SENSEI, ADIOS2, and ParaView with Catalyst available in `LD_LIBRARY_PATH` and `PYTHONPATH`
  - `python3 pdi2sensei/endpoint.py`
    - You can change the used Catalyst script, by adding to/changing the list `catalyst_scripts` by including the path to your Catalyst script in the endpoint.py file


## Getting help

Further information can be found in `doc/FAQ.md`, `doc/pdi2sensei.pdf`

In case there are problems or further questions you can contact Christian Witzler using c.witzler@fz-juelich.de



