@echo off
setlocal enabledelayedexpansion

set /a i=1
:loop
set /a j=i+99
python repack.py -s !i! -e !j! -t repacked_pairs -o repack-!i!_!j!
set /a i+=100
if !i! leq 1000 goto loop

endlocal