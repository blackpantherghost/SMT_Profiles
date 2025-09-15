fn scv3_fn_CloseScript =
(
	try cui.unRegisterDialogBar scv3_ro_MainScript catch()
	rolloutArr = #(scv3_ro_MainScript, scvHelp, scvSetting, scvExtra, scv3_ro_About, scv3_ro_Active)
	for rol in rolloutArr do try destroyDialog rol catch()
)

scv3_fn_CloseScript()

scv3_va_InstallPath = (getdir(#userScripts) + @"\D95 DESIGN\Smart Camera View 3")
scv3_va_ScriptPath = pathConfig.removePathLeaf (getSourceFileName())
scv3_va_OrgFolder = scv3_va_ScriptPath + @"\Smart Camera View 3"

--DETELE FOLDER WITH DOS COMMAND
fn scv3_fn_DeleteFolder folderPath: =
(
	sioDir = dotNetClass "System.IO.Directory"
	if (SIODir.Exists folderPath) do SIODir.Delete (folderPath) true
)
	
fn scv3_fn_RemoveSettings = try deleteFile (getdir(#plugcfg_ln) + "\\scv3_setting.ini") catch()
	
fn scv3_fn_RemoveFiles =
(
	try scv3_fn_DeleteFolder folderPath: scv3_va_InstallPath catch()
	try deleteFile (getdir(#userMacros) + "\\D95 DESIGN-SmartCameraView3.mcr") catch()
	try deleteFile (getdir(#userIcons) + "\\SmartCameraView3_16i.bmp") catch()
	try deleteFile (getdir(#userIcons) + "\\SmartCameraView3_24i.bmp") catch()
	try deleteFile  (getdir(#userIcons) + "\\SmartCameraView3_16a.bmp") catch()
	try deleteFile  (getdir(#userIcons) + "\\SmartCameraView3_24a.bmp") catch()
)

fn scv3_fn_CopyFiles = 
(
	filein (scv3_va_ScriptPath + "\\scv3_macro.mcr")
	copyFile (scv3_va_ScriptPath + "\\SmartCameraView3_16i.bmp") (getdir(#userIcons) + "\\SmartCameraView3_16i.bmp")
	copyFile (scv3_va_ScriptPath + "\\SmartCameraView3_24i.bmp") (getdir(#userIcons) + "\\SmartCameraView3_24i.bmp")
	copyFile (scv3_va_ScriptPath + "\\SmartCameraView3_16a.bmp") (getdir(#userIcons) + "\\SmartCameraView3_16a.bmp")
	copyFile (scv3_va_ScriptPath + "\\SmartCameraView3_24a.bmp") (getdir(#userIcons) + "\\SmartCameraView3_24a.bmp")
	HiddenDOSCommand ("xcopy \"" + scv3_va_OrgFolder + "\" \"" + scv3_va_InstallPath + "\" /e /c /i /y")
)

rollout scv3_ro_Install "Smart Camera View 3"
(
	label scv3_ui_Info ""
	group ""
	(
		button scv3_ui_InstallScript 		"Install" 		align:#center width: 80 offset:[0,-7] across:2
		button scv3_ui_UninstallScript 		"Uninstall" 	align:#center width: 80 offset:[0,-7]
	)

	on scv3_ui_InstallScript pressed do 
	(
		scv3_fn_RemoveFiles()
		filein (scv3_va_ScriptPath + "\\scv3_macro.mcr")
		try makeDir scv3_va_InstallPath catch (messageBox "Script encountered an unknown error when extracting the installation file, please try again!" title:"Smart Camera View 3")
		if doesFileExist (getdir(#plugcfg_ln) + "\\scv3_setting.ini") then (if querybox "Do you want to reset the settings?" title:"Smart Camera View 3" then scv3_fn_RemoveSettings())
		scv3_fn_CopyFiles()
		colorMan.reinitIcons()
		destroydialog scv3_ro_Install
		messagebox "Installed! Thanks for your purchase!" title:"Smart Camera View 3"
		
		try filein (scv3_va_InstallPath  + "\\Smart_Camera_View_3.mse") catch()
		
	)

	on scv3_ui_UninstallScript pressed do 
	(
		scv3_fn_RemoveFiles()
		if doesFileExist (getdir(#plugcfg_ln) + "\\scv3_setting.ini") then (if querybox "Do you want to remove the settings?" title:"Smart Camera View 3" then scv3_fn_RemoveSettings())
		colorMan.reinitIcons()
		destroydialog scv3_ro_Install
		try scv3_fn_DeleteFolder folderPath: scv3_va_InstallPath catch()
		messagebox "Uninstalled! Restart 3dsMax to take effect!" title:"Smart Camera View 3"
	)
)

createdialog scv3_ro_Install 200 100