# Goals



# Dependencies

- PDI 1.0.0 
- Adios2
- Sensei 3.2 with ParaView 5.7 or ParaView 5.8



# Running example on Jureca:

- Start ParaView 5.8
  - open port to accept Catalyst connection
- Change `example/allinputsgridwriter2.py:102`
  - set the nodename of the node running paraview
  - change the port if Catalyst is not listening on port 22222
- execute `example/run_example.sh` 
  - needs to be on a node where srun can be used
  - needs to be able to access open port of node running paraview



