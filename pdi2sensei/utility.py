import vtk



def getVtkImageData(size, origin = [0,0,0], spacing=[1,1,1], ghostLvl=0):
  """Function building a VTKImageData as a mesh, accepting an array for size, origin and spacing
  All three arrays can contain 2 or three elements, either for a 2D or 3D case"""
  grid = vtk.vtkImageData()
  # in case of a two dimensional array
  if len(size) == 2:
    size = [size[0], size[1], 1]
    origin = [origin[0], origin[1], 0]
    spacing = [spacing[0], spacing[1], 1]
  grid.SetDimensions(size[0],size[1],size[2])
  grid.SetSpacing(spacing[0],spacing[1],spacing[2])
  grid.SetOrigin(origin[0],origin[1],origin[2])
  return grid
