dropdb event_management_test
createdb event_management_test
psql event_management_test < setup.psql
python test_app.py