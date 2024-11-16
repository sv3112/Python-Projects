"""
Bicycle Rental Management - Bicycle Rental Module
This module manages the bicycle rental process, allowing users to return bicycles, 
calculate late fees, and apply damage charges if applicable.

It includes the following functionality:
    1. Check if a bicycle is rented.
    2. Retrieve rental details for a bicycle.
    3. Parse date strings into datetime objects.
    4. Process bicycle returns, including late fee calculations and damage charges.
"""

import sqlite3  # SQLite for database operations
from datetime import datetime  # To work with dates and times
from bikeSearch import create_connection  # Import the database connection function from bikeSearch


def is_bicycle_rented(cursor, bicycle_id):
    """
    Checks if the bicycle with the given ID is currently rented.

    Args:
        cursor (sqlite3.Cursor): A cursor object used to interact with the database.
        bicycle_id (int): The unique ID of the bicycle to check.

    Returns:
        tuple or None: Returns a tuple (Status, Rental_Rate) if the bicycle is rented, 
                        or None if the bicycle is not rented or the ID is invalid.
    """
    # Query the database to check the current status and rental rate of the bicycle
    cursor.execute("SELECT Status, Rental_Rate FROM Bicycle_Info_Data WHERE ID = ?", (bicycle_id,))
    result = cursor.fetchone()

    # If the bicycle is rented, return its status and rental rate
    return result if result and result[0] == 'Rented' else None  # Return None if the bike is not rented


def get_rental_details(cursor, bicycle_id):
    """
    Retrieves rental details for the given bicycle ID.

    Args:
        cursor (sqlite3.Cursor): A cursor object used to interact with the database.
        bicycle_id (int): The unique ID of the bicycle to get rental details for.

    Returns:
        tuple: A tuple containing the rental date (Rental_Date).
    """
    # Query the rental data for the bicycle to get the rental date
    cursor.execute("SELECT Rental_Date FROM Bicycle_Rental_Data WHERE Bicycle_ID = ?", (bicycle_id,))
    return cursor.fetchone()  # Return the rental date as a tuple


def parse_date(date_str):
    """
    Tries to parse a date string in both '%d/%m/%Y' and '%Y-%m-%d' formats.
    
    Args:
        date_str (str): The date string to be parsed.
    
    Returns:
        datetime: The parsed datetime object.
    
    Raises:
        ValueError: If the date cannot be parsed in either format.
    """
    if not date_str:
        raise ValueError("Date string is empty or None.")

    try:
        # Try parsing with the format '%d/%m/%Y' (day/month/year)
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        # If parsing fails, try '%Y-%m-%d' (year-month-day)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # If both formats fail, raise an exception
            raise ValueError(f"Invalid date format: {date_str}. Expected formats are 'DD/MM/YYYY' or 'YYYY-MM-DD'.")


def return_bicycle(bicycle_id, damage_charge=0.0):
    """
    Process the return of a rented bicycle, calculate late fees if applicable, and update records.
    
    Args:
        bicycle_id (int): The ID of the bicycle being returned.
        damage_charge (float): Optional charge for bicycle damage, default is 0.0.
    
    Returns:
        str: A summary message about the return process, including rental information, late fees, and total charge.
    """
    try:
        # Establish a connection to the database and create a cursor
        with create_connection() as connection:
            cursor = connection.cursor()

            # Retrieve rental status and rental rate for the bicycle
            cursor.execute("SELECT Status, Rental_Rate FROM Bicycle_Info_Data WHERE ID = ?", (bicycle_id,))
            result = cursor.fetchone()

            if not result:
                return "Error: Bicycle not found in the system."

            status, rental_rate = result

            # Check if the bicycle is rented, proceed only if rented
            if status != 'Rented':
                return f"Error: Bicycle with ID {bicycle_id} is not currently rented."

            # Retrieve rental record (rental date, expected return date, and member ID)
            cursor.execute("""
                SELECT Bicycle_Rental_Data.Rental_Date, Bicycle_Rental_Data.Return_Date, 
                       Bicycle_Rental_Data.Member_ID
                FROM Bicycle_Rental_Data
                WHERE Bicycle_Rental_Data.Bicycle_ID = ?
            """, (bicycle_id,))
            rental_record = cursor.fetchone()

            if not rental_record:
                return "Error: No rental record found for this bicycle."

            rental_date, expected_return_date, member_id = rental_record
            # Parse dates using the improved parse_date function
            rental_date = parse_date(rental_date)
            expected_return_date = parse_date(expected_return_date)

            # Calculate late fees if applicable (based on expected return date)
            actual_return_date = datetime.now()  # Get the current date as the actual return date
            late_days = max((actual_return_date - expected_return_date).days, 0)
            
            # Clean rental rate and calculate late fee
            rental_rate_cleaned = float(rental_rate.replace('£', '').replace('/day', '').strip())  # Clean rental rate
            late_fee = late_days * rental_rate_cleaned if late_days > 0 else 0  # Base late fee calculation

            # Add an additional £5 surcharge per day late
            surcharge_fee = late_days * 5  # Surcharge per day
            late_fee += surcharge_fee  # Add surcharge to the late fee

            # Update the rental record with the actual return date
            cursor.execute("""
                UPDATE Bicycle_Rental_Data 
                SET Return_Date = ?
                WHERE Bicycle_ID = ?
            """, (actual_return_date.strftime('%Y-%m-%d'), bicycle_id))
            
            # Mark the bicycle as 'Available' after it is returned
            cursor.execute("UPDATE Bicycle_Info_Data SET Status = 'Available' WHERE ID = ?", (bicycle_id,))
            
            connection.commit()

            # Prepare the result message for the return process
            result_message = "-" * 115 + "\n"
            result_message += f"Return Process Completed for Bicycle ID: {bicycle_id}\n"
            result_message += "-" * 115 + "\n"
            result_message += f"Current Rental Rate: £{rental_rate_cleaned:.2f}"
            result_message += f"\nRental Period: Rented on {rental_date.strftime('%Y-%m-%d')}: Returned on {actual_return_date.strftime('%Y-%m-%d')}\n"
            result_message += f"Expected Return Date: {expected_return_date.strftime('%Y-%m-%d')}\n"
            result_message += "-" * 115 + "\n"
            if late_days > 0:
                result_message += f"Notice: Late Fee for {late_days} overdue days: £{late_fee:.1f} (Includes £{surcharge_fee:.1f} surcharge)\n\n"
            else:
                result_message += "Returned on time. No late fee incurred.\n\n"
            
            # Calculate the total charge
            total_charge = late_fee + damage_charge

            # If damage charge is provided, update the bicycle condition
            if damage_charge > 0:
                result_message += f"Damage Charge: £{damage_charge:.2f}\n"
                cursor.execute("UPDATE Bicycle_Info_Data SET Condition = 'Damaged', Status = 'Unavailable' WHERE ID = ?", (bicycle_id,))
                connection.commit()
                result_message += "Bicycle marked as 'Damaged'.\n"
            else:
                result_message += "The bicycle has been successfully marked as 'Available'.\n"

            result_message += "-" * 115 + "\n"
            result_message += f"Total Amount Due: £{late_fee:.1f} (Late Fee) + £{damage_charge:.2f} (Damage Charge) = £{total_charge:.1f}\n"
            result_message += "-" * 115 + "\n"

            # Return the result message to be displayed in the UI
            return result_message

    except Exception as e:
        # If any error occurs during the return process, return an error message
        return f"An error occurred during the return process: {str(e)}"
