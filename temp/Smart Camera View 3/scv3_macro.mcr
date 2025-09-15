macroscript SmartCameraView3
category:"D95 DESIGN"
tooltip:"Smart Camera View 3"
buttontext:"SCV"
icon:#("SmartCameraView3" ,1)
(
	installPath = (getdir(#userScripts) + @"\D95 DESIGN\Smart Camera View 3")
	fn openScript = filein (installPath + "\\Smart_Camera_View_3.mse")
	openScript()
)