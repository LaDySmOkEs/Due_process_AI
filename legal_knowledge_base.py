"""
Legal Knowledge Base - A module for comprehensive legal knowledge integration.
This module provides structured legal knowledge across multiple domains to enhance AI-powered legal assistance.
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple

# Legal domains organized hierarchically
LEGAL_DOMAINS = {
    "constitutional_law": {
        "name": "Constitutional Law",
        "description": "Fundamental rights, government powers, and constitutional interpretation",
        "key_concepts": [
            "Due process", "Equal protection", "First Amendment rights", "Fourth Amendment protections",
            "Fifth Amendment rights", "Sixth Amendment rights", "Eighth Amendment protections"
        ],
        "landmark_cases": [
            {"name": "Miranda v. Arizona", "year": 1966, "significance": "Established Miranda rights/warnings"},
            {"name": "Gideon v. Wainwright", "year": 1963, "significance": "Right to counsel"},
            {"name": "Mapp v. Ohio", "year": 1961, "significance": "Exclusionary rule"},
            {"name": "Terry v. Ohio", "year": 1968, "significance": "Stop and frisk standards"}
        ]
    },
    "criminal_law": {
        "name": "Criminal Law",
        "description": "Laws related to crimes, prosecution, and defense",
        "key_concepts": [
            "Elements of crimes", "Mens rea", "Actus reus", "Defenses", "Burden of proof",
            "Chain of custody", "Probable cause", "Reasonable suspicion"
        ],
        "procedural_stages": [
            "Investigation", "Arrest", "Booking", "Initial appearance", "Preliminary hearing", 
            "Grand jury", "Arraignment", "Discovery", "Plea bargaining", "Pre-trial motions", 
            "Trial", "Sentencing", "Appeals"
        ],
        "common_motions": [
            {"name": "Motion to Suppress", "purpose": "Exclude illegally obtained evidence"},
            {"name": "Brady Motion", "purpose": "Compel disclosure of exculpatory evidence"},
            {"name": "Motion to Dismiss", "purpose": "Dismiss charges based on legal defects"},
            {"name": "Motion for Change of Venue", "purpose": "Move trial to different location"}
        ]
    },
    "civil_law": {
        "name": "Civil Law",
        "description": "Non-criminal legal disputes between parties",
        "key_areas": [
            "Personal injury", "Contract disputes", "Property disputes", "Torts",
            "Family law", "Employment law", "Intellectual property"
        ],
        "procedural_stages": [
            "Pleadings", "Discovery", "Pre-trial conference", "Trial", "Judgment", "Appeals"
        ],
        "common_motions": [
            {"name": "Motion for Summary Judgment", "purpose": "Decision without full trial"},
            {"name": "Motion to Compel", "purpose": "Force compliance with discovery"},
            {"name": "Motion in Limine", "purpose": "Exclude certain evidence before trial"}
        ]
    },
    "tribal_law": {
        "name": "Tribal Law",
        "description": "Legal matters involving federally recognized Native American tribes",
        "key_areas": [
            "Tribal sovereignty", "CFR courts", "Contract disputes with tribes", 
            "Sovereign immunity", "Tribal jurisdiction", "Federal Indian law"
        ],
        "procedural_stages": [
            "Jurisdictional determination", "Exhaustion of tribal remedies", 
            "Alternative dispute resolution", "Tribal court proceedings", 
            "Federal court proceedings (if applicable)"
        ],
        "common_motions": [
            {"name": "Motion to Determine Jurisdiction", "purpose": "Establish proper court authority"},
            {"name": "Motion to Waive Sovereign Immunity", "purpose": "Address tribal immunity defenses"},
            {"name": "Motion to Enforce Contract", "purpose": "Seek specific performance of tribal contracts"}
        ],
        "special_considerations": [
            "Check for contractual waiver of sovereign immunity",
            "Determine if case falls under CFR court jurisdiction (25 CFR Part 11)",
            "Identify if federal law preempts tribal authority",
            "Consider alternative dispute resolution mechanisms specified in contract"
        ]
    },
    "evidence_law": {
        "name": "Evidence Law",
        "description": "Rules governing admissibility of evidence",
        "key_concepts": [
            "Relevance", "Hearsay and exceptions", "Authentication", "Best evidence rule",
            "Character evidence", "Expert testimony", "Privileged communications"
        ],
        "evidence_types": [
            "Direct evidence", "Circumstantial evidence", "Documentary evidence",
            "Testimonial evidence", "Digital evidence", "Physical evidence"
        ],
        "admissibility_challenges": [
            {"ground": "Fourth Amendment violation", "strategy": "Motion to suppress based on illegal search/seizure"},
            {"ground": "Chain of custody", "strategy": "Challenge documentation and handling of evidence"},
            {"ground": "Fruit of poisonous tree", "strategy": "Evidence derived from illegal actions"},
            {"ground": "Miranda violation", "strategy": "Statements obtained without proper warnings"}
        ]
    },
    "document_preparation": {
        "name": "Legal Document Preparation",
        "description": "Standards and formats for legal documents",
        "document_types": {
            "motions": {
                "components": ["Caption", "Title", "Introduction", "Statement of facts", "Legal argument", "Conclusion", "Supporting documents"],
                "standards": ["Clear statement of relief sought", "Specific legal authority", "Factual basis", "Proper formatting"]
            },
            "pleadings": {
                "components": ["Caption", "Allegations", "Claims/defenses", "Prayer for relief", "Signature"],
                "standards": ["Numbered paragraphs", "Plain statement of claims", "Jurisdictional basis"]
            },
            "discovery": {
                "components": ["Interrogatories", "Requests for production", "Requests for admission", "Depositions"],
                "standards": ["Specificity", "Relevance", "Proportionality", "Proper scope"]
            }
        }
    }
}

# Legal rights categories with detailed descriptions
LEGAL_RIGHTS = {
    "fourth_amendment": {
        "name": "Fourth Amendment Rights",
        "description": "Protection against unreasonable searches and seizures",
        "key_questions": [
            "Was there a legitimate expectation of privacy?",
            "Was there a warrant based on probable cause?",
            "If no warrant, was there a recognized exception?",
            "Was the scope of the search/seizure reasonable?",
            "Was evidence handled properly after seizure?"
        ],
        "common_violations": [
            "Warrantless search without exception",
            "Overbroad search exceeding scope",
            "Search based on insufficient probable cause",
            "Illegal stop without reasonable suspicion",
            "Excessive force during arrest/seizure"
        ]
    },
    "fifth_amendment": {
        "name": "Fifth Amendment Rights",
        "description": "Protection against self-incrimination and double jeopardy",
        "key_questions": [
            "Was the person in custody during questioning?",
            "Were Miranda warnings properly given?",
            "Was the right to remain silent honored?",
            "Is there a double jeopardy issue?",
            "Was due process followed?"
        ],
        "common_violations": [
            "Failure to provide Miranda warnings in custody",
            "Continued questioning after right to counsel invoked",
            "Coerced confession",
            "Property taken without due process",
            "Prosecution after jeopardy attached"
        ]
    },
    "sixth_amendment": {
        "name": "Sixth Amendment Rights",
        "description": "Right to counsel, speedy trial, and confrontation",
        "key_questions": [
            "Was counsel provided at critical stages?",
            "Was there an unreasonable delay in prosecution?",
            "Has the right to confront witnesses been preserved?",
            "Was the trial public?",
            "Was the jury impartial?"
        ],
        "common_violations": [
            "Denial of counsel during critical proceedings",
            "Excessive pre-trial delay without justification",
            "Use of testimonial hearsay without confrontation",
            "Closed proceedings without proper justification",
            "Biased jury selection process"
        ]
    },
    "eighth_amendment": {
        "name": "Eighth Amendment Rights",
        "description": "Protection against excessive bail, fines, and cruel punishment",
        "key_questions": [
            "Is the bail amount proportional to the offense?",
            "Are detention conditions humane and constitutional?",
            "Is the punishment proportional to the crime?",
            "Are there medical needs being ignored?"
        ],
        "common_violations": [
            "Excessive bail without individualized assessment",
            "Inhumane detention conditions",
            "Disproportionate sentencing",
            "Deliberate indifference to medical needs"
        ]
    }
}

# Detailed document strategies by case type
DOCUMENT_STRATEGIES = {
    "criminal_defense": {
        "initial_stage": [
            {"document": "Discovery Request", "purpose": "Obtain all evidence in possession of prosecutor", "timing": "Immediately after arraignment"},
            {"document": "Brady Motion", "purpose": "Specifically request exculpatory evidence", "timing": "With initial discovery request"},
            {"document": "Motion to Preserve Evidence", "purpose": "Ensure all evidence is preserved intact", "timing": "As soon as possible after charges filed"}
        ],
        "pre_trial": [
            {"document": "Motion to Suppress", "purpose": "Exclude illegally obtained evidence", "timing": "After discovery reveals basis"},
            {"document": "Motion to Dismiss", "purpose": "Challenge legal sufficiency of charges", "timing": "After discovery reveals weaknesses"},
            {"document": "Motion for Bill of Particulars", "purpose": "Force prosecution to specify charges in detail", "timing": "If charging document is vague"}
        ],
        "trial": [
            {"document": "Motion in Limine", "purpose": "Exclude prejudicial evidence before trial", "timing": "Before trial begins"},
            {"document": "Jury Instructions", "purpose": "Shape how law is presented to jury", "timing": "Before jury deliberation"},
            {"document": "Directed Verdict Motion", "purpose": "Judgment as matter of law", "timing": "After prosecution's case"}
        ]
    },
    "tribal_contract": {
        "initial_stage": [
            {"document": "Complaint for Breach of Contract", "purpose": "Formally initiate legal action for contract breach", "timing": "Within contractual or statutory limitations"},
            {"document": "Motion to Determine Jurisdiction", "purpose": "Establish whether tribal, CFR, or federal court has jurisdiction", "timing": "At filing or immediately after"},
            {"document": "Notice of Contractual Dispute Resolution", "purpose": "Invoke any dispute resolution procedures in contract", "timing": "Before or concurrent with filing"}
        ],
        "sovereign_immunity": [
            {"document": "Motion to Address Sovereign Immunity", "purpose": "Establish whether sovereign immunity has been waived", "timing": "Early procedural stage"},
            {"document": "Request for Waiver Determination", "purpose": "Ask court to determine if immunity was contractually waived", "timing": "Before substantive proceedings"},
            {"document": "Federal Jurisdiction Analysis", "purpose": "Determine if case can proceed in federal court", "timing": "If tribal immunity is asserted"}
        ],
        "evidence_preservation": [
            {"document": "Request for Production", "purpose": "Obtain contract documents, communications, and payment records", "timing": "Early in discovery phase"},
            {"document": "Motion to Preserve Electronic Records", "purpose": "Ensure all digital communications are preserved", "timing": "Upon filing case"},
            {"document": "Third-Party Subpoenas", "purpose": "Obtain relevant documents from contractors, witnesses", "timing": "During discovery"}
        ],
        "resolution": [
            {"document": "Motion for Summary Judgment", "purpose": "Resolve clear contract issues without trial", "timing": "After discovery completion"},
            {"document": "Settlement Proposal", "purpose": "Formal written settlement terms", "timing": "Any point after filing"},
            {"document": "Motion to Enforce Judgment", "purpose": "Execute judgment against tribal assets if permitted", "timing": "After favorable judgment"}
        ]
    },
    "civil_rights": {
        "initial_stage": [
            {"document": "Section 1983 Complaint", "purpose": "Claim for civil rights violations", "timing": "Within statute of limitations"},
            {"document": "Temporary Restraining Order", "purpose": "Immediate injunctive relief", "timing": "When immediate harm threatens"},
            {"document": "Preliminary Injunction Motion", "purpose": "Relief during pendency of case", "timing": "Early in proceedings"}
        ],
        "discovery": [
            {"document": "Document Requests", "purpose": "Obtain policy manuals, training materials, personnel files", "timing": "After initial disclosures"},
            {"document": "Interrogatories", "purpose": "Written questions about practices and procedures", "timing": "With document requests"},
            {"document": "Depositions", "purpose": "Question officials under oath", "timing": "After document review"}
        ],
        "dispositive": [
            {"document": "Opposition to Qualified Immunity", "purpose": "Overcome immunity defense", "timing": "In response to defense motion"},
            {"document": "Summary Judgment Motion", "purpose": "Judgment without trial", "timing": "After discovery complete"}
        ]
    },
    "habeas_corpus": {
        "initial_stage": [
            {"document": "Habeas Petition", "purpose": "Challenge legality of detention", "timing": "After exhausting state remedies"},
            {"document": "Motion to Appoint Counsel", "purpose": "Obtain legal representation", "timing": "With initial petition"},
            {"document": "Discovery Motion", "purpose": "Obtain evidence supporting claims", "timing": "After petition accepted"}
        ],
        "development": [
            {"document": "Motion for Evidentiary Hearing", "purpose": "Present new evidence", "timing": "After response to petition"},
            {"document": "Motion to Expand Record", "purpose": "Include additional evidence", "timing": "When new evidence discovered"}
        ]
    }
}

def get_legal_domain_info(domain: str) -> Dict:
    """Get information about a specific legal domain"""
    return LEGAL_DOMAINS.get(domain, {"error": "Domain not found"})

def get_rights_analysis_questions(right_category: str) -> List[str]:
    """Get key questions for analyzing a specific rights category"""
    if right_category in LEGAL_RIGHTS:
        return LEGAL_RIGHTS[right_category]["key_questions"]
    return ["Right category not found"]

def get_document_strategy(case_type: str, stage: str) -> List[Dict]:
    """Get recommended document strategy for case type at specific stage"""
    if case_type in DOCUMENT_STRATEGIES and stage in DOCUMENT_STRATEGIES[case_type]:
        return DOCUMENT_STRATEGIES[case_type][stage]
    return [{"error": "Strategy not found for this case type/stage"}]

def get_evidence_challenges() -> List[Dict]:
    """Get list of evidence admissibility challenges"""
    return LEGAL_DOMAINS["evidence_law"]["admissibility_challenges"]

def format_comprehensive_strategy(case_type: str, rights_issues: List[str]) -> Dict:
    """Generate a comprehensive legal strategy based on case type and identified rights issues"""
    strategy = {
        "document_roadmap": [],
        "rights_defense_plan": [],
        "evidence_challenges": [],
        "procedural_timeline": []
    }
    
    # Add documents for all stages
    if case_type in DOCUMENT_STRATEGIES:
        for stage in DOCUMENT_STRATEGIES[case_type]:
            strategy["document_roadmap"].extend(DOCUMENT_STRATEGIES[case_type][stage])
    
    # Add rights-specific strategies
    for right in rights_issues:
        if right in LEGAL_RIGHTS:
            strategy["rights_defense_plan"].append({
                "right": LEGAL_RIGHTS[right]["name"],
                "violations_to_check": LEGAL_RIGHTS[right]["common_violations"],
                "key_questions": LEGAL_RIGHTS[right]["key_questions"]
            })
    
    # Add evidence challenges
    strategy["evidence_challenges"] = get_evidence_challenges()
    
    # Add procedural stages timeline
    if case_type == "criminal_defense":
        strategy["procedural_timeline"] = LEGAL_DOMAINS["criminal_law"]["procedural_stages"]
    elif case_type == "tribal_contract":
        strategy["procedural_timeline"] = LEGAL_DOMAINS["tribal_law"]["procedural_stages"]
    elif case_type in ["civil_rights", "personal_injury", "contract"]:
        strategy["procedural_timeline"] = LEGAL_DOMAINS["civil_law"]["procedural_stages"]
    
    return strategy

def enhance_ai_prompt_with_legal_knowledge(prompt: str, case_type: str, issue_area: str) -> str:
    """Enhance an AI prompt with relevant legal knowledge for more accurate responses"""
    legal_context = ""
    
    # Add domain-specific knowledge
    for domain, info in LEGAL_DOMAINS.items():
        if domain == issue_area or case_type in domain:
            legal_context += f"\n\nConsider these {info['name']} concepts and principles:\n"
            if "key_concepts" in info:
                legal_context += "\nKey concepts: " + ", ".join(info["key_concepts"])
            if "key_areas" in info:
                legal_context += "\nKey areas: " + ", ".join(info["key_areas"])
    
    # Add constitutional rights information if applicable
    rights_related = any(right in prompt.lower() for right in 
                         ["fourth amendment", "fifth amendment", "sixth amendment", 
                          "eighth amendment", "constitutional", "rights"])
    
    if rights_related:
        legal_context += "\n\nBe sure to consider these constitutional rights issues:\n"
        for right, info in LEGAL_RIGHTS.items():
            legal_context += f"\n{info['name']}: {info['description']}\n"
            legal_context += "Common violations: " + ", ".join(info["common_violations"][:3]) + "\n"
    
    # Add document strategy information if applicable
    if "document" in prompt.lower() or "filing" in prompt.lower() or "motion" in prompt.lower():
        if case_type in DOCUMENT_STRATEGIES:
            legal_context += f"\n\nConsider these strategic document filings for {case_type} cases:\n"
            for stage, docs in DOCUMENT_STRATEGIES[case_type].items():
                legal_context += f"\n{stage.replace('_', ' ').title()} stage:"
                for doc in docs[:2]:  # Add just a couple examples to keep prompt reasonable
                    legal_context += f"\n- {doc['document']}: {doc['purpose']}"
    
    # Combine with original prompt while keeping within reasonable length
    max_context_len = 1500  # Reasonable size that won't make prompts too long
    if len(legal_context) > max_context_len:
        legal_context = legal_context[:max_context_len] + "..."
    
    enhanced_prompt = prompt + "\n\n" + legal_context
    return enhanced_prompt

# Sample case law database for common rights violations
CASE_LAW_DATABASE = {
    "fourth_amendment": [
        {
            "case": "United States v. Jones",
            "citation": "565 U.S. 400 (2012)",
            "holding": "Installation of GPS tracking device on vehicle constitutes a search under Fourth Amendment",
            "application": "Use when challenging GPS tracking or electronic surveillance without a warrant"
        },
        {
            "case": "Rodriguez v. United States",
            "citation": "575 U.S. 348 (2015)",
            "holding": "Police cannot extend traffic stop beyond time needed to address the traffic violation without reasonable suspicion",
            "application": "Use when challenging evidence from prolonged traffic stops"
        }
    ],
    "fifth_amendment": [
        {
            "case": "Berghuis v. Thompkins",
            "citation": "560 U.S. 370 (2010)",
            "holding": "Suspect must unambiguously invoke right to remain silent; silence alone is insufficient",
            "application": "Consider when evaluating whether right to silence was properly invoked"
        },
        {
            "case": "Missouri v. Seibert",
            "citation": "542 U.S. 600 (2004)",
            "holding": "Two-step interrogation technique (questioning without Miranda, then with Miranda) is unconstitutional",
            "application": "Use when challenging confessions obtained after deliberate withholding of Miranda warnings"
        }
    ],
    "sixth_amendment": [
        {
            "case": "Missouri v. Frye",
            "citation": "566 U.S. 134 (2012)",
            "holding": "Defense counsel has duty to communicate formal plea offers to accused",
            "application": "Use in ineffective assistance claims where plea offers weren't communicated"
        },
        {
            "case": "Barker v. Wingo",
            "citation": "407 U.S. 514 (1972)",
            "holding": "Established four-part test for speedy trial violations: length of delay, reason for delay, defendant's assertion of right, and prejudice",
            "application": "Framework for analyzing speedy trial claims"
        }
    ]
}

def get_relevant_case_law(rights_category: str, specific_issue: Optional[str] = None) -> List[Dict]:
    """Retrieve relevant case law for a rights category and specific issue"""
    if rights_category in CASE_LAW_DATABASE:
        cases = CASE_LAW_DATABASE[rights_category]
        if specific_issue:
            # Filter cases more specifically if an issue is provided
            return [case for case in cases if specific_issue.lower() in case["application"].lower()]
        return cases
    return []