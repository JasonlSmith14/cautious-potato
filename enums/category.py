from enum import Enum


class CategoryEnum(str, Enum):
    food = "food"
    transfer = "transfer"
    groceries = "groceries"
    rent = "rent"
    utilities = "utilities"
    transport = "transport"
    entertainment = "entertainment"
    health = "health"
    education = "education"
    shopping = "shopping"
    subscriptions = "subscriptions"
    travel = "travel"
    income = "income"
    investment = "investment"
    insurance = "insurance"
    fees = "fees"
    charity = "charity"
    miscellaneous = "miscellaneous"
    unknown = "unknown"
