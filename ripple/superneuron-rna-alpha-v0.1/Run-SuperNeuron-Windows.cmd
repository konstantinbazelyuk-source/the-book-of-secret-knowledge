@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
 echo Python launcher py.exe was not found. Install Python 3.10 or later.
 exit /b 1
)
py -3 serve.py --fasta data\RHO_NM_000539.3_mirror.fasta --genes data\ncbi_genes
endlocal
