import vtk



def getVtkImageData(nx, ny, nz=1, ox=0, oy=0 ,oz=0, sx=1, sy=1, sz=1, ghostLvl=0):
  grid = vtk.vtkImageData()
  grid.SetDimensions(nx,ny,nz)
  grid.SetSpacing(sx,sy,sz)
  grid.SetOrigin(ox,oy,oz)
  return grid