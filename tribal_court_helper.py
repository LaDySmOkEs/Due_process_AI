"""
Tribal Court Helper - Module for handling cases in Court of Federal Regulations (CFR) and Tribal Courts
This module provides specialized functions for contract disputes with tribal entities,
focusing on sovereign immunity, jurisdiction, and specific procedural requirements.
"""

import logging
import os
from typing import Dict, List, Any, Optional

# Import our knowledge base
from legal_knowledge_base import get_document_strategy, get_legal_domain_info

def analyze_tribal_contract_case(description: str, contract_type: str = "general"):
    """
    Analyze a contract dispute with a tribal entity, focusing on jurisdictional
    and sovereign immunity considerations.
    
    Args:
        description: The case description
        contract_type: The type of contract (e.g., "construction", "services", "procurement")
        
    Returns:
        Dict with analysis of jurisdiction, sovereign immunity, and recommended approach
    """
    # Default analysis structure
    analysis = {
        "jurisdiction_analysis": {
            "likely_court": "Determine court jurisdiction (Tribal, CFR, or Federal)",
            "jurisdiction_factors": [
                "Contract contains forum selection clause",
                "Tribal entity has sovereign immunity",
                "Activity occurred on tribal land",
                "Federal law applies to contract terms"
            ],
            "recommended_approach": "Review contract for jurisdiction and sovereign immunity waiver provisions"
        },
        "sovereign_immunity": {
            "immunity_status": "Requires contract review to determine if waived",
            "waiver_factors": [
                "Express waiver in contract language",
                "Tribe's corporate charter may include waiver",
                "Federal law may limit immunity for certain activities"
            ],
            "immunity_strategy": "Focus on identifying if immunity was expressly waived in the contract"
        },
        "recommended_documents": [
            {
                "name": "Motion to Determine Jurisdiction",
                "purpose": "Establish proper court (tribal, federal, or state)",
                "timing": "Initial filing stage"
            },
            {
                "name": "Motion Regarding Sovereign Immunity",
                "purpose": "Address tribal immunity issues early in case",
                "timing": "Initial filing stage"
            },
            {
                "name": "Request for Contract Interpretation",
                "purpose": "Apply tribal custom and federal law to contract terms",
                "timing": "After jurisdiction is determined"
            }
        ],
        "precedent_cases": [
            {
                "case": "Kiowa Tribe of Oklahoma v. Manufacturing Technologies, Inc.",
                "citation": "523 U.S. 751 (1998)",
                "principle": "Tribal sovereign immunity extends to commercial activities off-reservation"
            },
            {
                "case": "C & L Enterprises, Inc. v. Citizen Band Potawatomi Tribe of Oklahoma",
                "citation": "532 U.S. 411 (2001)",
                "principle": "Clear arbitration provisions in contracts can constitute waiver of immunity"
            },
            {
                "case": "Michigan v. Bay Mills Indian Community",
                "citation": "572 U.S. 782 (2014)",
                "principle": "Reaffirmed tribal sovereign immunity for commercial activities"
            }
        ]
    }
    
    return analysis

def get_cfr_court_procedures():
    """
    Provides guidance on CFR Court procedures for contract disputes
    
    Returns:
        Dict with procedural steps and requirements
    """
    return {
        "filing_requirements": [
            "File complaint with CFR Court clerk (25 CFR § 11.801)",
            "Pay filing fee (typically $15-50 depending on court)",
            "Serve copy on tribal defendant according to court rules",
            "Include proof of exhaustion of tribal remedies if required"
        ],
        "procedural_stages": [
            "Initial filing and service",
            "Answer or motion phase (typically 20-30 days)",
            "Discovery period (if permitted by court)",
            "Pretrial conference",
            "Trial (typically more informal than federal court)",
            "Judgment and enforcement"
        ],
        "important_considerations": [
            "CFR Courts apply federal procedural rules with tribal customary law",
            "Limited discovery compared to federal courts",
            "Judges may be more familiar with tribal customs and expectations",
            "Appeal rights may be limited or different from federal courts"
        ]
    }

def format_tribal_contract_documents(case_description: str) -> List[Dict]:
    """
    Returns recommended document templates for tribal contract disputes
    
    Args:
        case_description: Description of the case
        
    Returns:
        List of document templates with strategic advice
    """
    # Get standard document strategies for contract cases
    tribal_documents = get_document_strategy("tribal_contract", "initial_stage")
    tribal_documents.extend(get_document_strategy("tribal_contract", "sovereign_immunity"))
    
    # Add CFR court specific guidance
    cfr_procedures = get_cfr_court_procedures()
    
    # Format documents with combined information
    formatted_docs = []
    for doc in tribal_documents:
        formatted_docs.append({
            "document_name": doc["document"],
            "strategic_purpose": doc["purpose"],
            "filing_timing": doc["timing"],
            "cfr_court_considerations": "Follows 25 CFR Part 11 requirements, emphasize any waiver of sovereign immunity"
        })
    
    return formatted_docs

def analyze_tribal_case(description: str, issue_type: str, court_type: str) -> Dict:
    """
    Comprehensive analysis of a case in tribal or CFR court
    
    Args:
        description: Case description
        issue_type: Type of legal issue
        court_type: Type of court
        
    Returns:
        Dictionary with case analysis
    """
    # Default to contract analysis if specific type not provided
    if 'contract' in issue_type.lower():
        return analyze_tribal_contract_case(description, "general")
    
    # Create a general analysis for non-contract cases
    analysis = {
        "jurisdiction_analysis": {
            "likely_court": "Tribal/CFR Court with possible federal oversight",
            "jurisdiction_factors": [
                "Activity occurred on tribal land",
                "Tribal membership status of parties",
                "Federal law implications",
                "Tribal sovereign powers"
            ],
            "recommended_approach": "Focus on jurisdiction and applicable law (tribal, federal, or both)"
        },
        "rights_assessment": [
            {
                "right_violated": "Tribal Due Process Rights",
                "explanation": "Analyze whether tribal procedures comply with federal standards",
                "severity": "Medium",
                "supporting_legal_principle": "Indian Civil Rights Act of 1968"
            }
        ],
        "case_law_suggestions": [
            {
                "case_name": "Santa Clara Pueblo v. Martinez",
                "year": "1978",
                "court": "U.S. Supreme Court",
                "relevance": "Established tribal sovereignty in internal matters with limited federal intervention",
                "principles": "Tribes have authority to regulate their internal affairs"
            },
            {
                "case_name": "Montana v. United States",
                "year": "1981",
                "court": "U.S. Supreme Court",
                "relevance": "Defined tribal authority over non-members on tribal lands",
                "principles": "Limits tribal authority over non-members except in specific situations"
            }
        ]
    }
    
    return analysis

def recommend_tribal_documents(description: str, issue_type: str, court_type: str) -> Dict:
    """
    Recommend documents for tribal or CFR court cases
    
    Args:
        description: Case description
        issue_type: Type of legal issue
        court_type: Type of court
        
    Returns:
        Dictionary with document recommendations
    """
    # For contract cases, use contract-specific documents
    if 'contract' in issue_type.lower():
        formatted_docs = format_tribal_contract_documents(description)
        
        # Format for the expected return structure
        return {
            "document_recommendations": [
                {
                    "document_type": doc["document_name"],
                    "importance": "Critical" if "sovereign immunity" in doc["strategic_purpose"].lower() else "High",
                    "rationale": doc["strategic_purpose"],
                    "key_elements": [
                        "Address tribal sovereignty considerations",
                        "Reference specific tribal laws or customs",
                        "Consider CFR court procedural requirements",
                        doc["cfr_court_considerations"]
                    ]
                }
                for doc in formatted_docs
            ]
        }
    
    # General documents for non-contract cases
    return {
        "document_recommendations": [
            {
                "document_type": "Motion to Determine Jurisdiction",
                "importance": "Critical",
                "rationale": "Establish whether tribal court has jurisdiction before proceeding",
                "key_elements": [
                    "Reference to Montana v. United States test",
                    "Analysis of tribal authority over subject matter",
                    "Connection to tribal interests and self-governance",
                    "Status of parties (tribal member vs. non-member)"
                ]
            },
            {
                "document_type": "Motion to Apply Tribal Law",
                "importance": "High",
                "rationale": "Ensure tribal customs and traditions are properly considered",
                "key_elements": [
                    "Citations to tribal code or customary law",
                    "Explanation of tribal legal principles",
                    "Argument for deference to tribal legal traditions",
                    "Integration with federal Indian law principles"
                ]
            },
            {
                "document_type": "ICRA-Based Challenge",
                "importance": "Medium",
                "rationale": "Raise procedural protections under Indian Civil Rights Act",
                "key_elements": [
                    "Due process violations within tribal procedures",
                    "Equal protection considerations",
                    "Limitations on tribal penalties and sanctions",
                    "Federal court review limitations under ICRA"
                ]
            }
        ]
    }