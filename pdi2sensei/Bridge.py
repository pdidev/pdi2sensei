import pdi2sensei


class Bridge:
  """Class mamaging the connection to Sensei, allowing to pass on data and mesh information"""
  
  def __init__(self, adiosFile):
    """Init method setting needed variables to their initial state"""
    self._dataAdaptors = [pdi2sensei.data_adaptor()]
    self._analysis_adaptor = pdi2sensei.analysis_adaptor()
    self._analysis_adaptor.initialize('adios2', args = 'engineName=SST,filename=' + str(adiosFile))
    self.__adiosFile__ = adiosFile
    self._timestep=0
    self._time=0.0
    self._lastTime=self._time

  def addMesh(self, mesh):
    """Add a mesh that describes the spacial distribution of the data that is provided to this bridge.
    The mesh is described using the VTK data model, therefore a VTK mesh needs to be provided. 
    This can be generated, either using VTK functions, or by using the functions provided in pdi2sensei.utility
    """
    self._dataAdaptors[0].set_geometry(mesh)

  def addDataForTimeStep(self, EveryXTimesteps, data, name):
    """This function lets you add an data array, that will be included in the update EveryXTimesteps and can be identified by the provided name"""
    if self._timestep % int(EveryXTimesteps) == 0:
        self.__addData__(data, name, 0)

  def addDataForTime(self, time, EveryXTimes, data, name):
    """This function lets you add an data array, that will be included in the update if the time variable increased by at least EveryXTimes and can be identified by the provided name"""
    if time - EveryXTimes > self._lastTime:
        self._lastTime = self._time
        self.__addData__(data, name, 0)
        
  def __addData__(self, data, name, AdaptorNum):
    """method that actualy adds the data if the public function's tests are true"""
    self._dataAdaptors[AdaptorNum].set_array(data, name)
    
  def update(self, time = 0.0):
    """This function executes all the necessary changes and transmitts them down the choosen in situ pipeline"""
    self._time = time
    for adapter in self._dataAdaptors:
        self._analysis_adaptor.update(adapter, self._timestep, self._time)
    self._timestep = self._timestep + 1
