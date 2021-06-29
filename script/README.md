# mysql-table-setup
A Python script to create and populate a MySQL table with data from a CSV file.

To run the script: 
1. Edit the field names, data types, and data in the `data.csv` file.
2. Run the `setup.py` script
    ```bash
    python setup.py '{"host": "<host>", "database": "<database>", "user": "<user>", "password": "<password>"}' "<table_name>"
    ```
