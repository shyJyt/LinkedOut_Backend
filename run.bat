@echo off

if "%1%" == "run" (
    python manage.py runserver 0.0.0.0:8000
) else if "%1%" == "migrate" (
    python manage.py migrate
) else if "%1%" == "make" (
    python manage.py makemigrations
) else (
    echo "Usage: run.bat [run|migrate|make]")