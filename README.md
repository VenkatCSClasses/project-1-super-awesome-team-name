# Diagrams

## Use-Case Diagram
![Project Use-Case Diagram](/images/usecase_diagram.png)

## Class Diagram
![Project Class Diagram](/images/class_diagram.png)


# Project Details

## Project 01-03
The three use cases that are going to be implemented are:
- Login/Logout
- Deposit
- Withdraw

## Work Distribution
- Abe: CLI and Login Implementation, database setup and api endpoints
- Andrew: checking_account, savings_account, bank, and transaction classes 
- Dylan: user interface and customer class
- Cameron: Deposit + Withdraw tests




## Coding Agent Usage
The areas where coding agents were utilized in this project were:
- Generating docstrings from method/class stubs in the src folder
- Assisting in writing in-depth tests in certain test classes
    - Helping with equivalence classes/boundary cases


# Setup & Running

## Installation
```sh
uv tool install ruff
uv tool install rust-just
uv tool update-shell
uv sync
```

## Installing Database
```sh
just install
```

## Running the server
```sh
just server-dev
```

## Running the CLI
```sh
just cli [COMMAND]
```

## Running tests
```sh
just test
```