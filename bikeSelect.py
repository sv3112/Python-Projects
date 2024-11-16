"""
Bicycle Rental Management - Bicycle Select Module
This module allows the users to search bicycles for new purchase based on available cost and other factors.
It includes functions for retrieving bicycle data, calculating recommendation scores, and generating purchase orders.
"""

import sqlite3  # SQLite for database operations
from datetime import datetime  # For working with date and time
from bikeSearch import create_connection  # Import the database connection function from bikeSearch


def get_bicycle_data():
    """
    Retrieves bicycle data and information about currently rented bicycles from the database.

    This function queries the database to retrieve bicycle details such as ID, brand, type, rental rate, 
    purchase date, and condition. Additionally, it fetches the list of bicycle IDs that are currently rented 
    (i.e., their return date is NULL).

    Returns:
        tuple: A tuple containing two elements:
            - list: A list of tuples, each containing bicycle data (ID, Brand, Type, Rental_Rate, Purchase_Date, Condition).
            - list: A list of bicycle IDs that are currently rented (i.e., their return date is NULL).
    """
    # Establish a connection to the database and create a cursor
    connection = create_connection()  
    cursor = connection.cursor()
    
    try:
        # Retrieve bicycle details such as ID, brand, type, rental rate, purchase date, and condition
        cursor.execute("SELECT ID, Brand, Type, Rental_Rate, Purchase_Date, Condition FROM Bicycle_Info_Data;")
        bicycles = cursor.fetchall()  # List of all bicycles
        
        # Retrieve bicycle IDs that are currently rented (i.e., their return date is NULL)
        cursor.execute("SELECT Bicycle_ID FROM Bicycle_Rental_Data WHERE Return_Date IS NULL;")
        rented_bicycles = [row[0] for row in cursor.fetchall()]  # List of rented bicycle IDs
    except sqlite3.Error as e:
        # Handle any database errors
        print(f"An error occurred: {e}")
        bicycles = []  # Empty list in case of an error
        rented_bicycles = []  # Empty list in case of an error
    finally:
        # Ensure the database connection is closed
        connection.close()
    
    return bicycles, rented_bicycles


def calculate_scores(bicycles, rented_bicycles):
    """
    Calculate recommendation scores for each bicycle based on factors such as rental frequency, type popularity, 
    age of the bicycle, and its condition.

    This function evaluates bicycles by considering factors like the bicycle's age, condition, rental frequency, 
    and type popularity. It assigns a score to each bicycle based on these factors, which can be used for making 
    recommendations for purchasing.

    Parameters:
        bicycles (list): A list of tuples containing bicycle data (ID, Brand, Type, Rental_Rate, Purchase_Date, Condition).
        rented_bicycles (list): A list of IDs of bicycles that are currently rented.

    Returns:
        dict: A dictionary where the key is the bicycle ID, and the value is a dictionary containing:
            - 'Brand': Bicycle brand
            - 'Type': Bicycle type
            - 'Rental_Rate': Bicycle rental rate
            - 'Score': Calculated score based on popularity, condition, age, and rental frequency
            - 'Age': Bicycle age in months
            - 'Condition': Bicycle condition (e.g., 'Good', 'Poor')
            - 'Rental_Frequency': Number of times the bicycle has been rented (currently rented count)
    """
    recommendations = {}  # Dictionary to store recommendation data
    current_date = datetime.now()  # Current date to calculate bicycle age
    
    # Define popularity weights for different bicycle types (higher values indicate more popular types)
    type_popularity = {
        'Mountain Bike': 3,
        'Road Bike': 2,
        'Hybrid Bike': 1,
        'Electric Bike': 4,
        'City Bike': 5,
        'Single Gear Bike': 6
    }
    
    for bike in bicycles:
        bike_id, brand, type_, rental_rate, purchase_date, condition = bike
        
        # Clean the rental_rate string and convert it to a numeric value (e.g., "£15/day" to 15.0)
        rental_rate = float(rental_rate.replace('£', '').replace('/day', '').strip())
        
        # Calculate the age of the bicycle in months
        age = (current_date - datetime.strptime(purchase_date, '%Y-%m-%d')).days // 30
        
        # Calculate the rental frequency (how many times the bicycle is currently rented)
        rental_frequency = rented_bicycles.count(bike_id)

        # Scoring system:
        # - Higher rental frequency and type popularity add to the score
        # - Older bicycles and poor condition reduce the score
        score = (rental_frequency * 3) + (type_popularity.get(type_, 0) * 2) - (age * 1.5) - (1 if condition == 'Poor' else 0)
        
        # Store the recommendation data for each bicycle
        recommendations[bike_id] = {
            'Brand': brand,
            'Type': type_,
            'Rental_Rate': rental_rate,
            'Score': score,
            'Age': age,
            'Condition': condition,
            'Rental_Frequency': rental_frequency
        }
    
    return recommendations


def generate_purchase_order(recommendations, budget):
    """
    Generates a purchase order for bicycles based on their recommendation scores, within a given budget.

    This function selects bicycles with the highest recommendation scores and adds them to a purchase order, ensuring
    that the total cost does not exceed the specified budget. The function will stop adding bicycles once the budget is exhausted.

    Parameters:
        recommendations (dict): A dictionary of bicycle recommendations containing their scores and other details.
        budget (float): The total available budget for purchasing bicycles.

    Returns:
        tuple: A tuple containing two elements:
            - dict: A dictionary representing the purchase order with bicycle IDs as keys and their purchase details as values.
            - float: The total cost of the bicycles included in the purchase order.
    """
    purchase_order = {}  # Dictionary to store the purchase order
    total_cost = 0  # Variable to track the total cost of the bicycles ordered
    
    # Sort bicycles by their recommendation score in descending order (highest score first)
    for bike_id, info in sorted(recommendations.items(), key=lambda x: x[1]['Score'], reverse=True):
        if total_cost >= budget:
            break  # Stop if the budget is exhausted
        
        # Calculate how many units of this bicycle can be bought within the remaining budget
        quantity_to_order = min((budget - total_cost) // info['Rental_Rate'], 5)  # Limit to a maximum of 5 units per bike
        if quantity_to_order > 0:
            purchase_order[bike_id] = {
                'Brand': info['Brand'],
                'Type': info['Type'],
                'Quantity': quantity_to_order,
                'Cost': quantity_to_order * info['Rental_Rate']
            }
            total_cost += quantity_to_order * info['Rental_Rate']  # Update total cost
    
    return purchase_order, total_cost
