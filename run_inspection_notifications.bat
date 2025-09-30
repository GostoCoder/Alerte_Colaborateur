@echo off
REM Exécute le script Python src\inspection_notifications.py depuis la racine du dépôt
REM Usage: double-cliquer ou exécuter depuis une invite de commandes Windows

SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Utilise py si disponible (préféré), sinon python3, sinon python
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 src\inspection_notifications.py %*
) else (
  where python3 >nul 2>&1
  if %ERRORLEVEL%==0 (
    python3 src\inspection_notifications.py %*
  ) else (
    python src\inspection_notifications.py %*
  )
)

if %ERRORLEVEL% neq 0 (
  echo Script termine avec code d'erreur %ERRORLEVEL%
) ELSE (
  echo Script termine avec succès
)

pause
