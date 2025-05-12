#!/usr/bin/env python
"""
Script to populate the database with legal terms from our comprehensive dictionary.
Run this script to ensure the legal jargon translator has a complete database of terms.
"""

import sys
from app import app, db
from models import LegalTerm
from legal_terms_database import LEGAL_TERMS

def populate_legal_terms():
    """Populate the database with legal terms from the dictionary."""
    print("Starting to populate legal terms database...")
    
    # Count of terms added and existing
    added_count = 0
    existing_count = 0
    
    # Add each term to the database if it doesn't already exist
    with app.app_context():
        for term, explanation in LEGAL_TERMS.items():
            # Check if term already exists
            existing_term = LegalTerm.get_term(term)
            
            if not existing_term:
                # Add the new term
                try:
                    LegalTerm.create_term(
                        term=term,
                        simple_explanation=explanation['simple_explanation'],
                        fun_explanation=explanation['fun_explanation'],
                        cartoon_description=explanation['cartoon_description'],
                        ai_generated=False,  # These are our predefined terms
                        verified=True        # These are verified as accurate
                    )
                    added_count += 1
                    print(f"Added term: {term}")
                except Exception as e:
                    print(f"Error adding term '{term}': {str(e)}")
            else:
                existing_count += 1
    
    print(f"Finished populating database.")
    print(f"Terms added: {added_count}")
    print(f"Terms already existing: {existing_count}")
    print(f"Total terms in dictionary: {len(LEGAL_TERMS)}")

if __name__ == "__main__":
    populate_legal_terms()