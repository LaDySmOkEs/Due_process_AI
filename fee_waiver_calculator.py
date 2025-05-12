"""
Fee Waiver Calculator - Implements sliding scale fee waivers based on poverty guidelines
"""

# 2025 Federal Poverty Guidelines (placeholders - would be updated annually)
# https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines
POVERTY_GUIDELINES = {
    1: 14580,  # Annual income thresholds for a household of 1
    2: 19720,  # Annual income thresholds for a household of 2
    3: 24860,  # etc.
    4: 30000,
    5: 35140,
    6: 40280,
    7: 45420,
    8: 50560,
}
# Add $5,140 for each person over 8
ADDITIONAL_PERSON_AMOUNT = 5140


def get_poverty_threshold(household_size):
    """
    Get the poverty threshold for a given household size
    """
    if household_size <= 8:
        return POVERTY_GUIDELINES.get(household_size, POVERTY_GUIDELINES[1])
    else:
        # For households with more than 8 people, add the additional amount
        # for each person beyond 8
        return POVERTY_GUIDELINES[8] + (ADDITIONAL_PERSON_AMOUNT * (household_size - 8))


def calculate_fee_waiver_percentage(annual_income, household_size):
    """
    Calculate fee waiver percentage based on income relative to poverty guidelines
    
    - 100% fee waiver if income is <= 100% of poverty level
    - No fee waiver if income is > 100% of poverty level
    """
    poverty_threshold = get_poverty_threshold(household_size)
    
    # Calculate income as a percentage of poverty level
    poverty_percentage = (annual_income / poverty_threshold) * 100
    
    # Determine fee waiver percentage based on income relative to poverty level
    if poverty_percentage <= 100:
        return 100  # 100% waiver
    else:
        return 0    # No waiver
        

def calculate_adjusted_fee(base_fee, annual_income, household_size):
    """
    Calculate the adjusted fee after applying any applicable waiver
    """
    waiver_percentage = calculate_fee_waiver_percentage(annual_income, household_size)
    discount = (waiver_percentage / 100) * base_fee
    return max(0, base_fee - discount)


def meets_full_waiver_requirements(annual_income, household_size):
    """
    Check if applicant meets requirements for 100% fee waiver (100% below poverty line)
    """
    poverty_threshold = get_poverty_threshold(household_size)
    poverty_percentage = (annual_income / poverty_threshold) * 100
    return poverty_percentage <= 100