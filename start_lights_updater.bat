ECHO OFF
CLS
:MENU
SET do_this=4
SET run_param=
ECHO.
ECHO ...................................................
ECHO Default behavior on just pressing Enter is to exit!
ECHO ...................................................
ECHO 1. Run conversion
ECHO 2. Undo conversion
ECHO 3. Remove backups
ECHO 4. Quits this
ECHO ...................................................
ECHO ...................................................
set /p do_this="Please enter what I should do: "
ECHO Youre choice: %do_this%

IF %do_this% == 4 (
CLS
EXIT)

IF %do_this% == 1 (
ECHO Running conversion...
CALL python lights_updater.py
CLS
GOTO MENU
)

IF %do_this% == 2 (
SET "run_param=-u"
ECHO Running undo..........
CALL python lights_updater.py %%run_param%%
CLS
GOTO MENU
)

IF %do_this% == 3 (
SET "run_param=-r"
ECHO Removing backups.....
CALL python lights_updater.py %%run_param%%
CLS
GOTO MENU
)
