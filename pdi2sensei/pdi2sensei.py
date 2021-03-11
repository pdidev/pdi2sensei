from mpi4py import *
import sensei
import vtk, vtk.util.numpy_support as vtknp
import numpy as np

#comm = MPI.COMM_WORLD
#rank = comm.Get_rank()
#n_ranks = comm.Get_size()
rank = 0
n_ranks = 1


def PyDebuggerOnRank(debugRank):
    if(rank == debugRank):
        import pdb
        pdb.set_trace()

def csv_str_to_dict(s):
    d = {}
    nvp=s.split(',')
    for nv in nvp:
        nv=nv.split('=')
        if len(nv) > 1:
            d[nv[0]] = nv[1]
        else:
            d[nv[0]] = None
    return d


def check_arg(dic, arg, dfl=None, req=True):
    if not arg in dic:
        if req and dfl is None:
            status('ERROR: %s is a required argument\n'%(arg))
            return False
        else:
            dic[arg] = dfl
            return True
    return True



class data_adaptor:
    def __init__(self):
        # data from sim
        self.arrays = {}
        self.grid = None
        # connect all the callbacks
        self.pda = sensei.ProgrammableDataAdaptor.New()
        self.pda.SetGetNumberOfMeshesCallback(self.get_number_of_meshes())
        self.pda.SetGetMeshMetadataCallback(self.get_mesh_metadata())
        self.pda.SetGetMeshCallback(self.get_mesh())
        self.pda.SetAddArrayCallback(self.add_array())
        self.pda.SetReleaseDataCallback(self.release_data())

    def __getattr__(self, *args):
        # forward calls to pda
        return self.pda.__getattribute__(*args)

    def base(self):
        return self.pda


    def set_array(self, vals, name):
        #print(name)
        #print(vals)
        arr = vtknp.numpy_to_vtk(vals.ravel(), 1)
        arr.SetName(name)
        self.arrays[name] = arr
        self.grid.GetPointData().AddArray(arr)
        #print(arr)

    def set_geometry(self, grid):        
        self.grid = grid

    def validate_mesh_name(self, mesh_name):
        if mesh_name != "field":
            raise RuntimeError('no mesh named "%s"'%(mesh_name))

    def get_number_of_meshes(self):
        def callback():
            return 1
        return callback

    def get_mesh_metadata(self):
        def callback(idx, flags):
            if idx != 0:
                raise RuntimeError('invalid mesh index %d'%(idx))
            md = sensei.MeshMetadata.New()
            md.MeshName = "field"
            md.MeshType = vtk.VTK_MULTIBLOCK_DATA_SET
            md.BlockType = vtk.VTK_IMAGE_DATA
            md.NumBlocks = n_ranks
            md.NumBlocksLocal = [1]
            md.BlockIds = [rank]
            md.BlockOwner = [rank]
            md.StaticMesh = 1
            md.NumArrays = 1
            md.ArrayName = ['main_field',]
            md.ArrayCentering = [vtk.vtkDataObject.POINT]
            md.ArrayType = [vtk.VTK_DOUBLE]
            md.ArrayComponents = [1]

            md.BlockNumCells = [self.grid.GetNumberOfCells()]
            md.BlockNumPoints =  [self.grid.GetNumberOfPoints()]
            md.BlockExtents = [self.grid.GetExtent()]
            md.BlockBounds = [self.grid.GetBounds()]
            md.BlockArrayRange =  [[[-1.,1.]]]
            return md
        return callback

    def get_mesh_name(self):
        def callback(idx):
            if idx != 0: raise RuntimeError('no mesh %d'%(idx))
            return 'field'
        return callback

    def get_number_of_arrays(self):
        def callback(mesh_name, assoc):
            self.validate_mesh_name(mesh_name)
            return len(self.arrays.keys()) \
                if assoc == vtk.vtkDataObject.POINT else 0
        return callback

    def get_array_name(self):
        def callback(mesh_name, assoc, idx):
            self.validate_mesh_name(mesh_name)
            return self.arrays.keys()[idx] \
                if assoc == vtk.vtkDataObject.POINT else 0
        return callback

    def get_mesh(self):
        def callback(mesh_name, structure_only):
            self.validate_mesh_name(mesh_name)
            # local bodies
            pd = self.grid
            if not structure_only:
                pass
            # global dataset
            mb = vtk.vtkMultiBlockDataSet()
            mb.SetNumberOfBlocks(n_ranks)
            mb.SetBlock(rank, pd)
            return mb
        return callback

    def add_array(self):
        def callback(mesh, mesh_name, assoc, array_name):
            self.validate_mesh_name(mesh_name)
            if assoc != vtk.vtkDataObject.POINT:
                raise RuntimeError('no array named "%s" in cell data'%(array_name))
            pd = mesh.GetBlock(rank)
            pd.GetPointData().AddArray(self.arrays[array_name])
        return callback

    def release_data(self):
        def callback():
            self.arrays = {}
            self.points = None
            self.cells = None
        return callback

class analysis_adaptor:
    def __init__(self):
        self.AnalysisAdaptor = None

    def initialize(self, analysis, args=''):
        self.Analysis = analysis
        args = csv_str_to_dict(args)
        # Libsim
        if analysis == 'libsim':
            imProps = sensei.LibsimImageProperties()
            self.AnalysisAdaptor = sensei.LibsimAnalysisAdaptor.New()
            self.AnalysisAdaptor.AddRender(1,'Pseudocolor', \
                'ids',False,False,(0.,0.,0.),(1.,1.,1.),imProps)
        # Catalyst
        if analysis == 'catalyst':
            if check_arg(args,'script'):
                self.AnalysisAdaptor = sensei.CatalystAnalysisAdaptor.New()
                self.AnalysisAdaptor.AddPythonScriptPipeline(args['script'])
        if analysis == 'adios2':
            engineName = 'SST'
            if check_arg(args, 'engineName'):
                engineName = args['engineName']
            filename = 'defaultAdiosFileName.cfg'
            if check_arg(args, 'filename'):
                filename = args['filename']
            self.AnalysisAdaptor = sensei.ADIOS2AnalysisAdaptor.New()
            self.AnalysisAdaptor.SetEngineName(engineName)
            self.AnalysisAdaptor.SetFileName(filename)
        # Libisim, etc
        elif analysis == 'configurable':
            if check_arg(args,'config'):
                self.AnalysisAdaptor = sensei.ConfigurableAnalysis.New()
                self.AnalysisAdaptor.Initialize(args['config'])

        if self.AnalysisAdaptor is None:
            status('ERROR: Failed to initialize "%s"\n'%(analysis))
            sys.exit(-1)

    def finalize(self):
        #self.DataAdaptor.ReleaseData()
        self.AnalysisAdaptor.Finalize()

    def update(self, DataAdaptor, timestep, time):

        #status('% 5d\n'%(i)) if i > 0 and i % 70 == 0 else None
        #status('.')
        DataAdaptor.SetDataTimeStep(timestep)
        DataAdaptor.SetDataTime(float(time))

        self.AnalysisAdaptor.Execute(DataAdaptor.base())

        DataAdaptor.ReleaseData()

def status(msg):
    sys.stderr.write(msg if rank == 0 else '')
