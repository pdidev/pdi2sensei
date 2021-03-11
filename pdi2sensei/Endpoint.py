from mpi4py import *
from multiprocessing import Process,Lock,Value
from sensei import VTKDataAdaptor,ADIOS2DataAdaptor, \
  ADIOS2AnalysisAdaptor,BlockPartitioner,PlanarPartitioner,CatalystAnalysisAdaptor
import sys,os
import numpy as np
import vtk, vtk.util.numpy_support as vtknp
from time import sleep

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
n_ranks = comm.Get_size()

def _error_message(msg):
  sys.stderr.write('ERROR[%d] : %s\n'%(rank, msg))

def _status_message(msg, io_rank=0):
  if rank == io_rank:
    sys.stderr.write('STATUS[%d] : %s\n'%(rank, msg))

def _check_array(array):
  # checks that array[i] == i
  test_array = vtknp.vtk_to_numpy(array)
  n_vals = len(test_array)
  base_array = np.empty(n_vals, dtype=test_array.dtype)
  i = 0
  while i < n_vals:
    base_array[i] = i
    i += 1
  ids = np.where(base_array != test_array)[0]
  if len(ids):
    error_message('wrong values at %s'%(str(ids)))
    return -1
  return 0

def _read_data(fileName, method, scriptPaths):
  # initialize the data adaptor
  _status_message('initializing ADIOS2DataAdaptor file=%s method=%s'%(fileName,method))
  da = ADIOS2DataAdaptor.New()
  da.SetReadEngine(method)
  da.SetFileName(fileName)
  da.SetPartitioner(BlockPartitioner.New())
  da.OpenStream()
  
  AnalysisAdaptor = CatalystAnalysisAdaptor.New()
  for script in scriptPaths:
    AnalysisAdaptor.AddPythonScriptPipeline(script)
  
  # process all time steps
  n_steps = 0
  retval = 0
  while True:
    # get the time info
    t = da.GetDataTime()
    it = da.GetDataTimeStep()
    _status_message('received step %d time %0.1f'%(it, t))

    # get the mesh info
    nMeshes = da.GetNumberOfMeshes()
    _status_message('receveied %d meshes'%(nMeshes))
    
    AnalysisAdaptor.Execute(da)

    n_steps += 1
    if (da.AdvanceStream()):
      break

  # close down the stream
  da.CloseStream()
  _status_message('closed stream after receiving %d steps'%(n_steps))
  AnalysisAdaptor.Finalize()
  return retval

class Endpoint:
  
  def __init__(self, adiosFile):
    self._fileName = adiosFile
    self._method = "SST"
    self._scriptPaths = []
  
  def addCatalystScript(self, scriptPath):
    self._scriptPaths.append(scriptPath)

  def startEndpoint(self):
    ierr = _read_data(self._fileName, self._method, self._scriptPaths)
    if ierr:
      _error_message('read failed')

    # return the error code
    return ierr
