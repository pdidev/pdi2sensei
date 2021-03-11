#! /bin/bash

echo "To Run example start Paraview 5.8 on the same node and open a Catalyst Connection."



. ../modules.jureca
srun -n3 python3 example.py pycall__sensei_mpi.yml &
srun -n2 python3 Endpoint.py


