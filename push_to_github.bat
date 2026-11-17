@echo off
echo ============================================
echo   OmniSave - GitHub Push Script
echo ============================================
echo.

:: Project folder
cd /d "C:\Users\devd1\Downloads\Projects\insta download"

:: Create .gitignore to skip unnecessary files
echo downloads/ > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo *.mp4 >> .gitignore
echo *.mp3 >> .gitignore

:: Create Procfile for Railway
echo web: gunicorn app:app > Procfile

:: Initialize git if not already done
if not exist ".git" (
    echo [1/5] Initializing Git repo...
    git init
) else (
    echo [1/5] Git repo already initialized.
)

:: Set remote URL (apni repo ka URL hai)
echo [2/5] Setting GitHub remote...
git remote remove origin 2>nul
git remote add origin https://github.com/wavewolf7-netizen/omnisaver.git

:: Add all files including folders
echo [3/5] Adding all files (templates, static, etc.)...
git add .

:: Commit
echo [4/5] Committing changes...
git commit -m "Full project upload - templates, static, all files"

:: Push
echo [5/5] Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ============================================
echo   DONE! Check your GitHub repo:
echo   https://github.com/wavewolf7-netizen/omnisaver
echo ============================================
pause
