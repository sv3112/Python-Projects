# Bicycle Rental Management System

## Requirements:
- **Python Version**: 3.11.5

## Overview:
The **Bicycle Rental Management System** is designed to help manage bicycle rentals, including searching for bicycles, renting and returning bicycles, as well as selecting bicycles to purchase based on available budget. The system integrates external data from Excel files into an SQLite database and uses a user-friendly interface to facilitate interaction.

Below is an overview of the system's modules:

## Modules Overview:

### 1. **Database.py**:
- **Purpose**: Handles reading data from Excel files and importing it into an SQLite database.
- **Functions**:
  - Creates necessary tables for storing bicycle and rental data.
  - Ensures that data is formatted correctly and inserted into the database.

### 2. **bikeSearch.py**:
- **Purpose**: Allows users to search for bicycles in the database based on criteria such as brand, frame size, and type.
- **Features**:
  - Displays the search results with availability status.
  - Provides a status chart showing whether bicycles are available for rent, rented, or out of service.

### 3. **bikeRent.py**:
- **Purpose**: Facilitates the bicycle rental process by allowing users to rent bicycles.
- **Functions**:
  - Users must provide membership details and select a bicycle from the available ones.
  - Dynamically calculates rental days and updates rental charges.

### 4. **bikeReturn.py**:
- **Purpose**: Manages the return process of rented bicycles.
- **Features**:
  - Records the return date of bicycles.
  - Calculates late fees if a bicycle is returned after the expected date.
  - Applies surcharge fees for each overdue day.
  - Calculates damage charges if the bicycle is returned with any damage.

### 5. **bikeSelect.py**:
- **Purpose**: Assists users in selecting bicycles to purchase based on available budget and preferences.
- **Functions**:
  - Retrieves bicycle data from the database and calculates recommendation scores.
  - Generates a purchase order based on the user's budget and preferences.
  - Uses a weighted scoring system to rank bicycles based on factors like popularity and condition.

## File Structure:
The system is divided into the following Python modules:

