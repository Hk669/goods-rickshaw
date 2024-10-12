```sh

./venv/Scripts/activate
cd logistics_platform
python manage.py runserver

```


### Redis

- Check for the Redis Access Control in the `render.com`, for the access in the production when deployment.
- render is restrcited to only 50 connections

## Install PostGres and POSTGIS Extension
- [link](https://computingforgeeks.com/how-to-install-postgresql-13-on-ubuntu/)
- Setup the Database
    ```sh
            sudo -u postgres psql
            CREATE DATABASE logistics_db;

            psql -d postgis_db
            CREATE EXTENSION postgis;
    ```
- The above will setup the postgis extension in the `logistics_db`.
