# Diagrams

## Use-Case Diagram
![Project Use-Case Diagram](/images/usecase_diagram.png)

## Class Diagram
![Project Class Diagram](/images/class_diagram.png)

# Project Progress

## Project 01-03
The three use cases that are going to be implemented are:
- Login/Logout
- Deposit
- Withdraw

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