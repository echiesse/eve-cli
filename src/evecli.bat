@echo off

setlocal

if "%VIRTUAL_ENV%" == "" (
    activate
    set mustdeactivate=true
)

python evecli.py %*

if "%mustdeactivate%" == "true" deactivate

endlocal