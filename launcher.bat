@setlocal
@cd /d %~dp0
@pipenv run convert %1
@pause