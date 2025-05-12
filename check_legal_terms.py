#!/usr/bin/env python
"""
Script to check how many legal terms are in the database
"""

from app import app
from models import LegalTerm

with app.app_context():
    # Count total terms in database
    terms_count = LegalTerm.query.count()
    print(f"Total legal terms in database: {terms_count}")
    
    # Get some sample terms 
    sample_terms = LegalTerm.query.order_by(LegalTerm.search_count.desc()).limit(5).all()
    print("\nSample terms:")
    for term in sample_terms:
        print(f"- {term.term} (search count: {term.search_count})")
    
    # Check if specific important terms exist
    important_terms = ["habeas corpus", "voir dire", "pro se", "prima facie", "fruit of the poisonous tree"]
    print("\nChecking for important terms:")
    for term_name in important_terms:
        term = LegalTerm.get_term(term_name)
        if term:
            print(f"- '{term_name}' exists in database")
        else:
            print(f"- '{term_name}' NOT FOUND in database")