"""
Reward360 Transaction Intelligence Engine — Category Mapper

Maps a resolved canonical merchant name to its spending category using the DB.
If the merchant is not in the database, returns None.
"""

from typing import Optional
from data.category_mapping import CATEGORY_MAP

class CategoryMapper:
    @staticmethod
    def get_category(merchant_name: str) -> Optional[str]:
        """
        Look up the category for a given merchant name.
        Handles partial matches (e.g., 'Amazon Prime' -> 'Amazon').
        
        Returns:
            The category string if found, otherwise None.
        """
        if not merchant_name:
            return None
            
        # 1. Exact lookup
        if merchant_name in CATEGORY_MAP:
            return CATEGORY_MAP[merchant_name]
            
        # 2. Substring fallback (e.g., "Amazon Web Services" -> check if "Amazon" is in map)
        # This is basic partial matching for compound names
        for known_merchant, category in CATEGORY_MAP.items():
            if known_merchant in merchant_name:
                return category
                
        # Not found in our mapping
        return None
