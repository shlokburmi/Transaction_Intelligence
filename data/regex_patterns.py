"""
Reward360 Transaction Intelligence Engine — Regex Patterns

Tier 2 resolution uses these compiled patterns.
Patterns are grouped by purpose. The matcher tries specific patterns before generic ones.
"""

import re

# 1. Payment Processor Prefixes
# These are used by the preprocessor to strip noise before Tier 1 matching.
# Matches: "SQ *", "PAYPAL *", "CRV*", "TST*", "CHK*" etc.
PROCESSOR_PREFIX_PATTERN = re.compile(
    r"^(?:SQ|PAYPAL|CRV|TST|CHK|POS|UPI|NFS|IMPS|NEFT|RTGS)\s*\*?\s*-?\s*",
    re.IGNORECASE
)

# 2. Location and ID Suffixes
# Used by the preprocessor to clean the tail of the string.
# Matches things like " IN", " US", " BLR", or alphanumeric IDs like "*2H4XK"
SUFFIX_PATTERN = re.compile(
    r"(?:\s+(?:IN|US|UK|JP|BLR|MUM|DEL|HYD|CHE))?\s*(?:[\*\#\/]\w+)?\s*$",
    re.IGNORECASE
)

# 3. Merchant-Specific Extraction Patterns (Tier 2)
# These extract the merchant name even if there is surrounding noise.
# We map the regex group match to the canonical merchant name.
MERCHANT_PATTERNS = [
    # (Regex pattern, Canonical Merchant Name)
    (re.compile(r"UBER\s*\*?\s*EATS", re.IGNORECASE), "Uber Eats"),
    (re.compile(r"UBER\s*\*?\s*(TRIP|RIDE)?", re.IGNORECASE), "Uber"),
    (re.compile(r"IRCTC.*?(RAIL|TRAIN|TKT)", re.IGNORECASE), "IRCTC"),
    (re.compile(r"AMZN\s+MKT?P?", re.IGNORECASE), "Amazon"),
    (re.compile(r"AMAZON\s+(PRIME|PAY|RETAIL)", re.IGNORECASE), "Amazon"),
    (re.compile(r"SWIGGY.*?(INSTAMART)?", re.IGNORECASE), "Swiggy"), # Might be overridden by dictionary if exact
    (re.compile(r"ZOMATO.*?(ONLINE)?", re.IGNORECASE), "Zomato"),
    (re.compile(r"OLA\s*(CABS|POSTPAID)?", re.IGNORECASE), "Ola Cabs"),
    (re.compile(r"AIRTEL.*?(PREPAID|POSTPAID|BROADBAND|XSTREAM)", re.IGNORECASE), "Airtel"),
    (re.compile(r"JIO.*?(PREPAID|POSTPAID|FIBER)", re.IGNORECASE), "Reliance Jio"),
    (re.compile(r"MCDONALD.*?S?", re.IGNORECASE), "McDonald's"),
]

# 4. Generic Structural Patterns (Tier 2 Fallback)
# These capture everything after a known prefix if the preprocessor didn't catch it
# e.g., "PAYTM*SOME MERCHANT" -> "SOME MERCHANT"
STRUCTURAL_PATTERNS = [
    re.compile(r"^(?:PAYTM|PHONEPE|RAZORPAY|CCAVENUE|PAYU)\s*\*?\s*-?\s*(.+)$", re.IGNORECASE)
]
