import pdi2sensei


class Bridge:
  
  def __init__(self, adiosFile):
    self._dataAdaptors = [pdi2sensei.data_adaptor()]
    self._analysis_adaptor = pdi2sensei.analysis_adaptor()
    self._analysis_adaptor.initialize('adios2', args = 'engineName=SST,filename=' + str(adiosFile))
    self.__adiosFile__ = adiosFile
    self._timestep=0
    self._time=0.0
    self._lastTime=self._time

  def addMesh(self, mesh):
    self._dataAdaptors[0].set_geometry(mesh)

  def addDataForTimeStep(self, EveryXTimesteps, data, name):
    if self._timestep % int(EveryXTimesteps) == 0:
        self.__addData__(data, name, 0)

  def addDataForTime(self, time, EveryXTimes, data, name):
    if time - EveryXTimes > self._lastTime:
        self._lastTime = self._time
        self.__addData__(data, name, 0)
        
  def __addData__(self, data, name, AdaptorNum):
    self._dataAdaptors[AdaptorNum].set_array(data, name)
    
  def update(self, time = 0.0):
    self._time = time
    for adapter in self._dataAdaptors:
        self._analysis_adaptor.update(adapter, self._timestep, self._time)
    self._timestep = self._timestep + 1
