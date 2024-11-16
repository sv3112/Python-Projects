"""
Bicycle Rental Management - Bicycle Rental Module
This module allows the users to rent bicycles based on Membership and Rental limits.
It includes the following functionality:
    1. Check bicycle availability and rental status.
    2. Confirm rental and receive rental details, including rental and expected return dates.
    3. Record each rental in the database for tracking.
"""

import sqlite3  # SQLite for database operations
from datetime import datetime, timedelta  # To work with dates and times
from membershipManager import load_memberships  # Function to load membership data
from bikeSearch import create_connection  # Function to create a database connection

# Load membership data from the membership manager
memberships = load_memberships()


def is_member_valid(member_id):
    """
    Check if a member's membership is valid based on the membership end date.
    
    Args:
        member_id (str): The unique identifier of the member.
    
    Returns:
        bool: True if the member is valid (i.e., membership is active and not expired).
        str: Error message if the member is invalid.
    """
    # Retrieve the member data using the provided member_id
    member_data = memberships.get(str(member_id))

    # Check if member data is missing or incomplete
    if not member_data:
        return False, f"Error: Member ID {member_id} not found or invalid."

    # Check if the membership end date exists and if it is expired
    if 'MembershipEndDate' not in member_data:
        return False, f"Error: Missing 'MembershipEndDate' for member ID {member_id}."
    if member_data['MembershipEndDate'] <= datetime.now():
        return False, f"Alert: Membership for Member ID {member_id} has expired."

    return True, ""  # Return True if valid membership


def has_reached_rental_limit(cursor, member_id):
    """
    Check if a member has reached their rental limit.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        member_id (str): The unique identifier of the member.
    
    Returns:
        bool: True if the member has reached their rental limit, False otherwise.
    """
    # Query the database to count the number of bicycles rented by this member
    cursor.execute("SELECT COUNT(*) FROM Bicycle_Rental_Data WHERE Member_ID = ?", (member_id,))
    rented_count = cursor.fetchone()[0]  # Get the count of rented bicycles

    # Get the rental limit from the membership data
    rental_limit = memberships.get(str(member_id), {}).get('RentalLimit', 0)

    # If the rented count is greater than or equal to the rental limit, return True
    return rented_count >= rental_limit


def is_bicycle_available(cursor, bicycle_id):
    """
    Check if the requested bicycle is available for rent based on its status.
    
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        bicycle_id (str): The unique identifier of the bicycle.
    
    Returns:
        tuple: A tuple containing bicycle details (status, brand, type, rental rate) if available.
               None if the bicycle is unavailable.
    """
    # Query the database to retrieve the bicycle's current status and other details
    cursor.execute("SELECT Status, Brand, Type, Rental_Rate FROM Bicycle_Info_Data WHERE ID = ?", (bicycle_id,))
    result = cursor.fetchone()

    if result:
        status = result[0]  # Get the bicycle status
        # Check if the bicycle is available for rent
        if status == 'Available':
            return result  # Return the bicycle details (status, brand, type, rental rate)
        elif status == 'Under maintenance':
            return "Alert: The selected bicycle can't be rented because it is under maintenance."
        elif status == 'Rented':
            return "Alert: This bicycle is already rented. Please try another."
        elif status == 'Unavailable':
            return "Alert: This bicycle is Unavailable. Please try another."
    return "Error: Bicycle ID not found."  # If bicycle not found in the database


def rent_bicycle(member_id, bicycle_id, rental_days):
    """
    Rent a bicycle to a member if all conditions are met: valid membership, rental limit not reached,
    and the bicycle is available. Updates rental information in the database.

    Args:
        member_id (str): The unique identifier of the member.
        bicycle_id (str): The unique identifier of the bicycle.
        rental_days (int): The number of days the bicycle will be rented.
    
    Returns:
        str: A confirmation message or error message based on the outcome of the rental process.
    """
    try:
        # Establish a database connection and create a cursor to interact with the database
        with create_connection() as connection:
            cursor = connection.cursor()

            # Validate the membership of the member
            is_valid, error_message = is_member_valid(member_id)
            if not is_valid:
                return error_message  # Return the error message if the member is invalid

            # Check if the requested bicycle is available for rent
            bicycle_info = is_bicycle_available(cursor, bicycle_id)
            if isinstance(bicycle_info, str):
                return bicycle_info  # Return the error message if the bicycle is not available

            # Validate rental days input
            if rental_days <= 0:
                return "Error: Rental duration must be at least 1 day."

            # Calculate the rental and return dates
            rental_date = datetime.now().strftime('%Y-%m-%d')
            return_date = (datetime.now() + timedelta(days=rental_days)).strftime('%Y-%m-%d')

            # Check if the member has already reached their rental limit
            if has_reached_rental_limit(cursor, member_id):
                return "Notice: You have reached your rental limit. Please return a bicycle before renting another."

            # If the bicycle is available, update the rental information in the database
            cursor.execute("SELECT * FROM Bicycle_Rental_Data WHERE Bicycle_ID = ?", (bicycle_id,))
            existing_rental = cursor.fetchone()

            if existing_rental:
                # If the bicycle is already rented, update the rental record
                cursor.execute("""
                    UPDATE Bicycle_Rental_Data 
                    SET Member_ID = ?, Rental_Date = ?, Return_Date = ? 
                    WHERE Bicycle_ID = ? 
                """, (member_id, rental_date, return_date, bicycle_id))
                update_message = "Rental details updated successfully."
            else:
                # If no rental record exists, insert a new rental record
                cursor.execute(
                    "INSERT INTO Bicycle_Rental_Data (Bicycle_ID, Rental_Date, Return_Date, Member_ID) VALUES (?, ?, ?, ?)",
                    (bicycle_id, rental_date, return_date, member_id)
                )
                update_message = "Rental details added successfully."

            # Update the bicycle status to 'Rented' in the database
            cursor.execute("UPDATE Bicycle_Info_Data SET Status = 'Rented' WHERE ID = ?", (bicycle_id,))

            # Commit the transaction to save the changes
            connection.commit()

            # Retrieve the bicycle details for confirmation message
            brand, type_, rental_rate = bicycle_info[1], bicycle_info[2], bicycle_info[3]

            # Prepare a detailed confirmation message with the bicycle ID
            confirmation_message = f"{'Rental Confirmation'}:\n{'-'*115}\n"
            confirmation_message += f"{'Bicycle Details'}:\n"
            confirmation_message += f"Bicycle ID: {bicycle_id}\n"
            confirmation_message += f"Brand: {brand}\nType: {type_}\n{'-'*115}\n"
            confirmation_message += f"{'Rental Information'}:\n"
            confirmation_message += f"Rental Rate: {rental_rate}\n"
            confirmation_message += f"Start Date: {rental_date}\n"
            confirmation_message += f"Expected Return Date: {return_date}\n"
            confirmation_message += f"\n{update_message}"

            return confirmation_message  # Return the confirmation message after successful rental

    except Exception as e:
        # If any exception occurs, return a generic error message
        return f"An error occurred during the rental process: {e}"
