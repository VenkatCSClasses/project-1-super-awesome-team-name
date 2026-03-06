from bank import Bank

# Shared in-memory bank state for all route modules.
bank = Bank.load_from_file()
