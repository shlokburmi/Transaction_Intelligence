"""
Reward360 Transaction Intelligence Engine — Merchant Dictionary

Tier 1 resolution uses this mapping to quickly identify merchants from
cleaned transaction strings. Contains aliases (keys) mapped to their
canonical merchant names (values).

Keys must be uppercase since the preprocessor uppercases transactions.
"""

MERCHANT_ALIASES = {
    # Global Tech / E-commerce
    "AMZN": "Amazon",
    "AMAZN": "Amazon",
    "AMAZON": "Amazon",
    "AWS": "Amazon Web Services",
    "GOOGLE": "Google",
    "GSUITE": "Google",
    "APPLE": "Apple",
    "APL": "Apple",
    "MSFT": "Microsoft",
    "MICROSOFT": "Microsoft",
    "NETFLIX": "Netflix",
    "NFLX": "Netflix",
    "SPOTIFY": "Spotify",
    
    # Food & Dining
    "STARBUCKS": "Starbucks",
    "SBUX": "Starbucks",
    "MCDONALDS": "McDonald's",
    "MCD": "McDonald's",
    "KFC": "KFC",
    "DOMINOS": "Domino's Pizza",
    "PIZZA HUT": "Pizza Hut",
    "BURGER KING": "Burger King",
    "SUBWAY": "Subway",
    "BLUE TOKAI": "Blue Tokai Coffee",
    "THIRD WAVE": "Third Wave Coffee",
    "NANDOS": "Nando's",

    # Indian Aggregators & Delivery
    "SWIGGY": "Swiggy",
    "SWIGY": "Swiggy",
    "ZOMATO": "Zomato",
    "BLINKIT": "Blinkit",
    "ZEPTO": "Zepto",
    "DUNZO": "Dunzo",
    "BIGBASKET": "BigBasket",
    "BBASKET": "BigBasket",
    "INSTAMART": "Swiggy Instamart",

    # Ride Hailing & Travel
    "UBER": "Uber",
    "OLA": "Ola Cabs",
    "OLACABS": "Ola Cabs",
    "RAPIDO": "Rapido",
    "MAKEMYTRIP": "MakeMyTrip",
    "MMT": "MakeMyTrip",
    "GOIBIBO": "Goibibo",
    "YATRA": "Yatra",
    "IRCTC": "IRCTC",
    "CLEARTRIP": "Cleartrip",
    "BOOKMYSHOW": "BookMyShow",
    "BMS": "BookMyShow",
    "AIRASIA": "AirAsia",
    "INDIGO": "IndiGo",
    "VISTARA": "Vistara",

    # Retail / Shopping / Groceries
    "DMART": "DMart",
    "RELIANCE FRESH": "Reliance Fresh",
    "RELIANCE SMART": "Reliance Smart",
    "MORE RETAIL": "More Supermarket",
    "MORE MEGA": "More Supermarket",
    "SPENCERS": "Spencer's Retail",
    "PANTALOONS": "Pantaloons",
    "MAX RETAIL": "Max Fashion",
    "LIFESTYLE": "Lifestyle",
    "SHOPPERS STOP": "Shoppers Stop",
    "MYNTRA": "Myntra",
    "FLIPKART": "Flipkart",
    "AJIO": "Ajio",
    "NYKAA": "Nykaa",

    # Fuel / Auto
    "IOCL": "Indian Oil",
    "INDIANOIL": "Indian Oil",
    "BPCL": "Bharat Petroleum",
    "BHARAT PETROLEUM": "Bharat Petroleum",
    "HPCL": "Hindustan Petroleum",
    "HINDUSTAN PET": "Hindustan Petroleum",
    "SHELL": "Shell",
    "NAYARA": "Nayara Energy",

    # Telecom / Utilities
    "JIO": "Reliance Jio",
    "RELIANCE JIO": "Reliance Jio",
    "AIRTEL": "Airtel",
    "BHARTI AIRTEL": "Airtel",
    "VI": "Vodafone Idea",
    "VODAFONE": "Vodafone Idea",
    "BSNL": "BSNL",
    "BESCOM": "BESCOM",
    "TATA POWER": "Tata Power",
    "ADANI ELECT": "Adani Electricity",
    
    # Financial / Payments
    "PAYTM": "Paytm",
    "PHONEPE": "PhonePe",
    "CRED": "CRED",
    "GOOGLE PAY": "Google Pay",
    "GPY": "Google Pay",
    
    # Fashion Brands
    "ZARA": "Zara",
    "H&M": "H&M",
    "RARE RABBIT": "Rare Rabbit",
    "LEVIS": "Levi's",
    "MARKS & SPENCER": "Marks & Spencer",
    "MARKS AND SPENCER": "Marks & Spencer",
}

# Generate a list of unique canonical merchant names for fuzzy matching
CANONICAL_MERCHANTS = list(set(MERCHANT_ALIASES.values()))
