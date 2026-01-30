rd /S /Q .\dist\CamtrawlBrowser
rd /S /Q .\build\CamtrawlBrowser
pyinstaller --windowed --icon=resources\fish.ico --version-file=version.txt CamtrawlBrowser.py
md .\dist\CamtrawlBrowser\resources
xcopy /E resources .\dist\CamtrawlBrowser\resources

