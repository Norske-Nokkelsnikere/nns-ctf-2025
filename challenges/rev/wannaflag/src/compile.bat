@echo off
cl wannaflag.c /Fe:../handout/wannaflag.exe /link user32.lib wininet.lib /DEBUG:NONE /INCREMENTAL:NO
if exist wannaflag.obj del wannaflag.obj
echo compile complete, wannaflag.exe created in ../handout directory
