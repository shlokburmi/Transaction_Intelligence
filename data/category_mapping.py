"""
Reward360 Transaction Intelligence Engine — Category Mapping

Maps canonical merchant names to one of the VALID_CATEGORIES defined in config.py.
Used by the Category Mapper module after a merchant has been identified.
"""

CATEGORY_MAP = {
    # Shopping
    "Amazon": "Shopping",
    "Flipkart": "Shopping",
    "Myntra": "Shopping",
    "Ajio": "Shopping",
    "Nykaa": "Shopping",
    "Pantaloons": "Shopping",
    "Max Fashion": "Shopping",
    "Lifestyle": "Shopping",
    "Shoppers Stop": "Shopping",
    "Zara": "Shopping",
    "H&M": "Shopping",
    "Rare Rabbit": "Shopping",
    "Levi's": "Shopping",
    "Marks & Spencer": "Shopping",
    "Apple": "Shopping",

    # Dining
    "Starbucks": "Dining",
    "McDonald's": "Dining",
    "KFC": "Dining",
    "Domino's Pizza": "Dining",
    "Pizza Hut": "Dining",
    "Burger King": "Dining",
    "Subway": "Dining",
    "Blue Tokai Coffee": "Dining",
    "Third Wave Coffee": "Dining",
    "Nando's": "Dining",
    "Swiggy": "Dining",
    "Zomato": "Dining",

    # Groceries
    "Blinkit": "Groceries",
    "Zepto": "Groceries",
    "Dunzo": "Groceries",
    "BigBasket": "Groceries",
    "Swiggy Instamart": "Groceries",
    "DMart": "Groceries",
    "Reliance Fresh": "Groceries",
    "Reliance Smart": "Groceries",
    "More Supermarket": "Groceries",
    "Spencer's Retail": "Groceries",

    # Travel
    "Uber": "Travel",
    "Ola Cabs": "Travel",
    "Rapido": "Travel",
    "MakeMyTrip": "Travel",
    "Goibibo": "Travel",
    "Yatra": "Travel",
    "IRCTC": "Travel",
    "Cleartrip": "Travel",
    "AirAsia": "Travel",
    "IndiGo": "Travel",
    "Vistara": "Travel",

    # Entertainment
    "Netflix": "Entertainment",
    "Spotify": "Entertainment",
    "BookMyShow": "Entertainment",

    # Fuel
    "Indian Oil": "Fuel",
    "Bharat Petroleum": "Fuel",
    "Hindustan Petroleum": "Fuel",
    "Shell": "Fuel",
    "Nayara Energy": "Fuel",

    # Utilities
    "Reliance Jio": "Utilities",
    "Airtel": "Utilities",
    "Vodafone Idea": "Utilities",
    "BSNL": "Utilities",
    "BESCOM": "Utilities",
    "Tata Power": "Utilities",
    "Adani Electricity": "Utilities",
    
    # Software/Cloud
    "Microsoft": "Utilities",
    "Google": "Utilities",
    "Amazon Web Services": "Utilities",
}
