pip install -r requirements.txt //
uvicorn app.main:app --reload //


Docker:
docker-compose build
docker-compose up


SQLITE:
For ctrl + shift + P Quick Query
INSERT INTO Users (username, password, role, group_id) VALUES ('admin', 'admin_password', 'Admin', NULL);
DROP TABLE table_name;
DELETE FROM table_name;
