import psycopg2 as ps

def postgres_insert(temp_file, table, table_col):
    """
    Inserts data from a CSV file into a PostgreSQL database table.

    Args:
    - temp_file (str): Path to the CSV file containing the data to be inserted.
    - table (str): Name of the PostgreSQL database table.
    - table_col (str): Comma-separated column names for the PostgreSQL database table.

    Returns:
    - None: Prints information about the insertion process.

    Note:
    This function establishes a connection to the PostgreSQL database, performs the data insertion using the
    PostgreSQL COPY command, and prints the number of rows inserted. In case of an error, it prints the error message
    and rolls back the transaction.

    Example:
    ```
    postgres_insert("/path/to/data.csv", "example_table", "col1, col2, col3")
    ```

    """

    # Open the CSV file for reading
    f = open(temp_file, 'r')

    # Establish a connection to the PostgreSQL database
    connection = ps.connect(database="xxxxxxx", user="xxxxxx", password="xxxxxxx", host="xx.xxx.xxx.xx", port="5432")

    # Create a cursor object for executing SQL commands
    cur = connection.cursor()

    # Define the COPY command to insert data into the PostgreSQL table
    cmd = f'COPY {table} ({table_col}) FROM STDIN DELIMITER \',\';'

    try:
        # Execute the COPY command to insert data
        cur.copy_expert(cmd, f)
        print(f" {temp_file}  >>> Inserted Rows = {cur.rowcount}", "\n\n")

        # Commit the changes to the database
        connection.commit()

        # Close the CSV file
        f.close()

    except (Exception, ps.DatabaseError) as error:
        # Handle errors by rolling back the transaction and printing the error message
        print("Error: ", error, "\n\n")
        connection.rollback()
        cur.close()
        f.close()
        return 1

    # Close the cursor
    cur.close()
