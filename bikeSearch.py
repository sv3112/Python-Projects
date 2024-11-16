"""
Bicycle Rental Management - Bicycle Search Module
This module allows the users to search for bicycles based on specific criteria:
    1. Brand: Search for bicycles by brand name
    2. Type: Filter bicycles by type (e.g., mountain, road)
    3. Frame Size: Search based on the frame size of the bicycle
    Additionally, it includes functionality to visualize bicycle status data through bar charts.
"""

import sqlite3  # SQLite for database operations
import matplotlib.pyplot as plt  # Matplotlib for plotting data

def create_connection():
    """
    Establishes a connection to the SQLite database.

    This function attempts to connect to the 'BicycleRental.db' SQLite database. 
    If the connection is successful, it returns the connection object.
    If the connection fails, it catches the error and prints an error message, returning None.

    Returns:
        sqlite3.Connection: The connection object if successful, None otherwise.
    """
    try:
        conn = sqlite3.connect('BicycleRental.db')  # Connect to the database
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


def search_bicycles(conn, search_terms):
    """
    Searches for bicycles in the database based on the provided search criteria.

    This function dynamically builds a SQL query using the `search_terms` dictionary. 
    It applies case-insensitive matching using the `LOWER()` function for each search term 
    and uses the SQL `LIKE` operator for partial matching.

    Args:
        conn (sqlite3.Connection): The database connection object.
        search_terms (dict): A dictionary of search criteria, where keys are column names 
                              (e.g., 'Brand', 'Type') and values are the search terms.

    Returns:
        list: A list of bicycles that match the search criteria, or an empty list if no results are found.
    """
    try:
        if conn is None:
            print("Database connection is not established.")
            return []

        cursor = conn.cursor()

        # Build the base query for searching bicycles
        query = "SELECT * FROM bicycle_Info_Data WHERE "
        conditions = []  # Holds individual query conditions
        values = []  # Holds the corresponding search values

        # Dynamically build query conditions based on the search terms
        for key, value in search_terms.items():
            conditions.append(f"LOWER({key}) = LOWER(?)")  # Make search case-insensitive
            values.append(value.strip())  # Ensure there are no leading/trailing spaces in the search term

        # Combine conditions with AND, or return all rows if no conditions are specified
        query += " AND ".join(conditions) if conditions else "1=1"

        # Execute the query
        cursor.execute(query, values)
        results = cursor.fetchall()

        if not results:
            print("No bicycles found matching the search criteria.")
            return []

        return results  # Return the list of results
    except Exception as e:
        print(f"Error in search_bicycles: {e}")
        return []
    finally:
        cursor.close()  # Close the cursor to release the database connection


def show_status_chart(status_count, title):
    """
    Displays a bar chart showing the count of bicycles for each status (e.g., Available, Rented, Under maintenance).

    This function uses Matplotlib to create a bar chart where each status is represented by a colored bar. 
    The `status_count` dictionary contains the status types as keys and their respective counts as values.

    Args:
        status_count (dict): A dictionary where the keys are bicycle statuses 
                              (e.g., 'Available', 'Rented') and the values are the counts.
        title (str): The title to display on the chart.

    Returns:
        None: The function does not return any value. It displays the chart.
    """
    # Extract the list of statuses and their corresponding counts
    statuses = list(status_count.keys())
    counts = list(status_count.values())

    # Define the colors associated with each status
    color_map = {
        'Available': 'green',           # Green for Available bicycles
        'Rented': 'red',                # Red for Rented bicycles
        'Under maintenance': 'orange'   # Orange for bicycles under maintenance
    }
    
    # Map the statuses to their respective colors (default to 'gray' if status is not known)
    colors = [color_map.get(status, 'gray') for status in statuses]

    # Create a bar chart
    bars = plt.bar(statuses, counts, color=colors)

    # Label the axes and title the chart
    plt.xlabel('Bicycle Status')
    plt.ylabel('Number of Bicycles')
    plt.title(title.title())  # Capitalize the title for uniformity
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility

    # Add the count values above each bar for clarity
    for bar in bars:
        yval = bar.get_height()  # Get the height (count) of each bar
        plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), 
                 ha='center', va='bottom')  # Position text at the top of the bar

    # Adjust layout to prevent overlap and display the plot
    plt.tight_layout()
    plt.show()
