@echo off
pip install gradio==3.50.2
pip install plotly

mkdir C:\ProgramFiles\AdventureTeamBarrios

move * C:\ProgramFiles\AdventureTeamBarrios

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\MyShortcut.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\ProgramFiles\AdventureTeamBarrios\front-end\web.py" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs
del CreateShortcut.vbs