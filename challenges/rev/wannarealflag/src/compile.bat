@echo off
cl wannarealflag.c /Fe:../handout/wannarealflag.exe /link user32.lib wininet.lib
if exist wannarealflag.obj del wannarealflag.obj
echo compile complete, wannarealflag.exe created in ../handout directory
