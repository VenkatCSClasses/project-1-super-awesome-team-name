# BankOS
## A simple Bank Account Management TUI

For installation instructions, please refer to [INSTALLATION.md](INSTALLATION.md).
For information on how to use the project, please refer to [USAGE.md](USAGE.md).

# Diagrams
## Use-Case Diagram
![Project Use-Case Diagram](/images/usecase_diagram.png)

## Class Diagram
![Project Class Diagram](/images/class_diagram.png)

## Stage Diagram
![Project State Diagram](/images/state_diagram.png)


# Project Details

## Project 01-03
The three use cases that are going to be implemented are:
- Login/Logout
- Deposit
- Withdraw

## Work Distribution
- Abe: TUI and Login Implementation, database setup and api endpoints, bank class, and README/USAGE/INSTALLATION documentation
- Andrew: checking_account class; savings_account and transaction classes/tests; custom exceptions; json saving/reading
- Dylan: customer, teller, user classes & tests; bank tests; 
- Cameron: checking_account tests; finalized state & class diagrams

## Coding Agent Usage
The areas where coding agents were utilized in this project were:
- Generating docstrings from method/class stubs in the src folder
- Assisting in writing in-depth tests in certain test classes
    - Helping with equivalence classes/boundary cases
- Speeding up development of the terminal user interface
- General debugging assistance
- Copilot auto completions and suggestions across the codebase


## Dependencies Used (installed via uv):
- **Textual**: Used for building the terminal user interface (TUI) of the application. 
- **FastAPI**: Used for building the backend API that the TUI interacts with. 
- **HTTPX**: Used for making async HTTP requests to the FastAPI backend from the TUI.
- **PyJWT**: Used for handling JSON Web Tokens (JWT) for authentication and authorization in the application.
- **Argon2-cffi**: Used for securely hashing user passwords before storing them in the database.
- **pyfiglet**: Used for rendering ASCII art text for the TUI. 
- **pytest**: Used for writing and running tests for the application. 
- **Also, any other dependenices the above packages required**