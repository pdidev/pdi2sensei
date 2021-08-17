# Goals

The goal of pdi2sensei is to enable simulations easier use of in situ methods. This goal is approached by using PDI as the interface that is included in the simulation code. Afterward, this interface can be used to specify different I/O operations and enable in situ using pdi2sensei. These changes can be made in a separate file, that can be changed after building the simulation.

Using pdi2sensei removes the direct dependencies of the simulation code to the in situ libraries, reducing the difficulties for the simulation development. Furthermore, pdi2sensei employs an in transit model, therefore transporting the data to a different node, before doing the actual visualization on those extra nodes. To have a flexible solution with good transport mechanisms we use different libraries like Sensei and Adios2. This may sound like a counterintuitive solution to make it easier, but in pdi2sensei we set the data transport and in situ visualization with Catalyst from ParaView as the default, so there is no need to make changes there, so this complexity does not touch the end-user.

# Dependencies

- PDI 1.0.0 
- Adios2
- Sensei 3.2 with ParaView 5.7 or ParaView 5.8


# Running example on Jureca with live interactive visualization:

- Start ParaView 5.8
  - open port to accept Catalyst connection
- Change `example/allinputsgridwriter2.py:102`
  - set the node name of the node running ParaView
  - change the port if Catalyst is not listening on port 22222
- execute `example/run_example.sh` 
  - needs to be on a node where srun can be used
  - needs to be able to access open port of node running ParaView


# Using pdi2sensei

If you want to use pdi2sensei for your code a couple of steps need to be done:

- Install / load the dependencies of pdi2sensei
- [Include PDI in your simulation code](https://pdi.julien-bigot.fr/master/Hands_on.html)
- Write a configuration file for PDI that includes passing on the data to pdi2sensei
- Setup the visualization pipeline you wish to use with the ParaView GUI and export it as a Catalyst script
- Start the simulation and the visualization Endpoint
