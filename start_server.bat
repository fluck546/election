@echo off
:: Prompt the user to enter a new private key
set /p new_key=Please enter the new private_key: 

:: Set the path to the config.ini file
set config_file=config.ini

:: Replace the private_key value in the config.ini file
for /f "tokens=1,2 delims==" %%A in ('findstr /i "^private_key" "%config_file%"') do (
    set old_key=%%B
)

:: Use PowerShell to update the private_key in the config.ini file
powershell -Command "(Get-Content '%config_file%') -replace 'private_key = %old_key%', 'private_key = %new_key%' | Set-Content '%config_file%'"

:: Run the Python manage.py runserver command
python manage.py runserver