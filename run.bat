@echo off
title Computer & Laptop Repair Service System
py repair_service\main.py
if errorlevel 1 (
    python repair_service\main.py
)
pause
