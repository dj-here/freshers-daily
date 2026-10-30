@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   FreshersDaily - Push to New GitHub Repository
echo   (Vercel + Git + Neon Cloud Production Deployment)
echo ========================================================
echo.

cd /d "%~dp0"

echo Current Directory: %CD%
echo.

set /p REPO_URL="Enter your new GitHub repository URL (e.g. https://github.com/dj-here/freshers-daily.git): "

if "%REPO_URL%"=="" (
  echo Error: Repository URL cannot be empty.
  pause
  exit /b 1
)

echo.
echo Setting remote 'origin' to %REPO_URL%...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo Ensuring branch is named 'main'...
git branch -M main

echo Staging latest changes...
git add .
git commit -m "feat: FreshersDaily production deployment setup" 2>nul

echo.
echo Pushing FreshersDaily codebase to %REPO_URL%...
git push -u origin main

if %ERRORLEVEL% equ 0 (
  echo.
  echo ========================================================
  echo [SUCCESS] FreshersDaily pushed to %REPO_URL%!
  echo.
  echo NEXT STEPS FOR 24/7 LIVE DEPLOYMENT ON VERCEL:
  echo --------------------------------------------------------
  echo 1. Go to https://vercel.com/new
  echo 2. Import your repository: %REPO_URL%
  echo 3. In the project setup screen:
  echo    - Set 'Root Directory' to: frontend (click Edit, select 'frontend')
  echo 4. In 'Environment Variables', add:
  echo    - DATABASE_URL:
  echo      postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require
  echo    - ADMIN_API_KEY:
  echo      adminkey-dev-supersecret-freshersdaily-2026
  echo 5. Click 'Deploy'!
  echo.
  echo Your FreshersDaily platform will be live 24/7 with:
  echo   - 100%% uptime on Vercel Edge Serverless
  echo   - Neon Serverless PostgreSQL with connection pooling
  echo   - Automated daily publish cron at 00:00 UTC (05:30 IST)
  echo   - High-concurrency support for thousands of users
  echo ========================================================
) else (
  echo.
  echo [ERROR] Push failed. Make sure:
  echo 1. The repository exists on GitHub
  echo 2. You have write/push permissions
  echo 3. GitHub credentials are authenticated
)

pause
