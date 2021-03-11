from pdi2sensei.Endpoint import Endpoint 


endPoint = Endpoint("adios.cfg")
endPoint.addCatalystScript("allinputsgridwriter.py")
endPoint.startEndpoint()