"""
Bicycle Rental Management - SQLite Database Module (Updated for 3NF)
This module provides functions to interact with the BicycleRental.db SQLite database.
It includes:
    * Reading from and writing to the database
    * Importing and exporting data to and from CSV files

The primary function, `setup_database`, creates necessary tables (`Bicycle_Info_Data`, 
`Bicycle_Rental_Data`, `Bicycle_Condition`, and `Member`) and imports bicycle and rental 
data from external text files, while cleaning and validating the data before insertion.

This module does the following:
1. Creates the necessary tables to meet 3NF.
2. Reads data from external files (`Bicycle_Info.txt` and `Rental_History.txt`).
3. Validates and cleans the data.
4. Inserts the cleaned data into the database.
"""

import sqlite3  # For database operations (connecting, executing queries)
import os  # For file operations (checking file existence)

# Define the file paths for the bicycle information and rental data
Bicycle_info_Datafiles = '/Users/24COP501_F416664/Bicycle_Info.txt'
Bicycle_rental_Datafiles = '/Users/24COP501_F416664/Rental_History.txt'


def setup_database():
    """
    Sets up the SQLite database by creating necessary tables and inserting data.

    This function connects to the SQLite database, creates tables (`Bicycle_Info_Data`, 
    `Bicycle_Rental_Data`, `Bicycle_Condition`, `Member`) if they do not exist, and inserts 
    data into these tables from external text files. It also validates and cleans the data before 
    insertion.

    Returns:
        None
    """
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('BicycleRental.db', timeout=30)
    cursor = conn.cursor()

    # Create the Bicycle Condition table if it does not exist
    create_Bicycle_Condition_table = ''' 
        CREATE TABLE IF NOT EXISTS Bicycle_Condition (
            Condition_ID INTEGER PRIMARY KEY,
            Condition_Name TEXT UNIQUE
        )
    '''
    cursor.execute(create_Bicycle_Condition_table)  # Execute the query to create the table
    print("Bicycle_Condition table created")

    # Create the Bicycle Info table if it does not exist
    create_Bicycle_info_table = ''' 
        CREATE TABLE IF NOT EXISTS Bicycle_Info_Data (
            ID INTEGER PRIMARY KEY,
            Brand TEXT,
            Type TEXT,
            Frame_Size TEXT,
            Rental_Rate TEXT,
            Purchase_Date TEXT,
            Condition TEXT,
            Status TEXT
        )
    '''
    cursor.execute(create_Bicycle_info_table)  # Execute the query to create the table
    print("Bicycle_Info_Data table created")

    # Create the Member table if it does not exist
    create_Member_table = ''' 
        CREATE TABLE IF NOT EXISTS Member (
            Member_ID INTEGER PRIMARY KEY,
            Name TEXT,
            Email TEXT,
            Phone TEXT
        )
    '''
    cursor.execute(create_Member_table)  # Execute the query to create the table
    print("Member table created")

    # Create the Bicycle Rental table if it does not exist
    create_Bicycle_Rental_table = '''
        CREATE TABLE IF NOT EXISTS Bicycle_Rental_Data(
            Rental_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Bicycle_ID INTEGER,
            Rental_Date TEXT,
            Return_Date TEXT,
            Member_ID INTEGER,
            FOREIGN KEY (Bicycle_ID) REFERENCES Bicycle_Info_Data(ID)
        )
    '''
    cursor.execute(create_Bicycle_Rental_table)  # Execute the query to create the table
    print("Bicycle_Rental_Data table created")
    
    # Check if the Bicycle_Info.txt file exists
    if not os.path.exists(Bicycle_info_Datafiles):
        print(f"Error: File '{Bicycle_info_Datafiles}' not found.")
        return

    # Check if the Rental_History.txt file exists
    if not os.path.exists(Bicycle_rental_Datafiles):
        print(f"Error: File '{Bicycle_rental_Datafiles}' not found.")
        return


    def validate_and_clean_data(row):
        """
        Validates and cleans a single row of bicycle data before insertion into the database.

        This function:
        - Ensures that the rental rate has the suffix '/day'.
        - Converts the purchase date to the format 'YYYY-MM-DD'. If the date is invalid, sets it to None.

        Args:
            row (list): A list containing data for a single bicycle record.

        Returns:
            list: A cleaned and validated row ready for insertion into the database.
        """
        cleaned_data = row.copy()

        # Clean rental rate
        rental_rate = cleaned_data[4].strip()
        if not rental_rate.endswith('/day'):
            rental_rate += '/day'  # Ensure the rental rate ends with '/day'
        cleaned_data[4] = rental_rate

        # Clean and validate purchase date
        purchase_date = cleaned_data[5].strip()
        try:
            day, month, year = purchase_date.split('/')
            cleaned_data[5] = f"{year}-{month}-{day}"  # Convert to 'YYYY-MM-DD' format
        except ValueError:
            cleaned_data[5] = None  # If date is invalid, set it to None

        return cleaned_data

    # Load bicycle information data from the specified file and insert it into the database
    with open(Bicycle_info_Datafiles, 'r') as file:
        next(file)  # Skip the header row
        for line in file:
            row = line.strip().split(',')  # Split the line by comma to get individual columns
            if len(row) == 8:  # Ensure that the row has the correct number of columns
                cleaned_row = validate_and_clean_data(row)  # Clean and validate the data
                # Insert the cleaned row into the Bicycle_Info_Data table
                cursor.execute('INSERT INTO Bicycle_Info_Data (ID, Brand, Type, Frame_Size, Rental_Rate, Purchase_Date, Condition, Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                    cleaned_row
                )

    # Commit the transaction after inserting all bicycle information data
    conn.commit()

    # Load bicycle rental data from the specified file and insert it into the database
    with open(Bicycle_rental_Datafiles, 'r') as file:
        next(file)  # Skip the header row
        for line in file:
            row = line.strip().split(',')  # Split the line by comma to get individual columns
            if len(row) == 4:  # Ensure that the row has the correct number of columns
                # Insert the rental data into the Bicycle_Rental_Data table
                cursor.execute('INSERT INTO Bicycle_Rental_Data (Bicycle_ID, Rental_Date, Return_Date, Member_ID) VALUES (?, ?, ?, ?)', row)

    # Commit the transaction after inserting all rental history data
    conn.commit()

    # Close the connection to the database
    conn.close()
