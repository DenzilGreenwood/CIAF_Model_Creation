"""
CIAF Industries Module
======================

Industry-specific AI governance implementations providing specialized compliance,
monitoring, and enforcement capabilities across all major economic sectors.

This module contains production-ready implementations for:
- Banking & Financial Services
- Healthcare & Medical AI
- Manufacturing & Industrial Systems
- Transportation & Autonomous Vehicles
- Energy & Utilities
- Insurance & Risk Assessment
- Legal & Professional Services
- Telecommunications
- Retail & E-commerce
- Media & Content Generation
- Government & Public Sector
- Education
- Defense & Aerospace
- Biotechnology & Genomics
- Climate & ESG Sustainability
- Cross-Border Multi-Jurisdictional
- Cybersecurity & Digital Identity
- AI Supply Chain & Lifecycle
- Foundation Models & Multi-Agent Systems
- Human Resources & Workforce

Each industry implementation extends the core CIAF framework with:
- Sector-specific regulatory compliance (EU AI Act, GDPR, industry regulations)
- Specialized risk assessment and mitigation strategies
- Industry-standard audit trails and transparency requirements
- Customized bias detection and fairness monitoring
- Cryptographic verification and provenance tracking
"""

from typing import Dict, List, Optional, Type
from ciaf.core.interfaces import AIGovernanceFramework

# Import all industry implementations
from .banking import BankingAIGovernanceFramework
from .healthcare import HealthcareAIGovernanceFramework
from .manufacturing import ManufacturingAIGovernanceFramework
from .transportation import TransportationAIGovernanceFramework
from .energy import EnergyAIGovernanceFramework
from .insurance import InsuranceAIGovernanceFramework
from .legal import LegalAIGovernanceFramework
from .telecommunications import TelecommunicationsAIGovernanceFramework
from .retail import RetailAIGovernanceFramework
from .media import MediaAIGovernanceFramework
from .government import GovernmentAIGovernanceFramework
from .education import EducationAIGovernanceFramework
from .defense import DefenseAIGovernanceFramework
from .biotechnology import BiotechnologyAIGovernanceFramework
from .climate_esg import ClimateESGAIGovernanceFramework
from .cross_border import CrossBorderAIGovernanceFramework
from .cybersecurity import CybersecurityAIGovernanceFramework
from .ai_supply_chain import AISupplyChainGovernanceFramework
from .foundation_models import FoundationModelGovernanceFramework
from .human_resources import HumanResourcesAIGovernanceFramework

__all__ = [
    'BankingAIGovernanceFramework',
    'HealthcareAIGovernanceFramework', 
    'ManufacturingAIGovernanceFramework',
    'TransportationAIGovernanceFramework',
    'EnergyAIGovernanceFramework',
    'InsuranceAIGovernanceFramework',
    'LegalAIGovernanceFramework',
    'TelecommunicationsAIGovernanceFramework',
    'RetailAIGovernanceFramework',
    'MediaAIGovernanceFramework',
    'GovernmentAIGovernanceFramework',
    'EducationAIGovernanceFramework',
    'DefenseAIGovernanceFramework',
    'BiotechnologyAIGovernanceFramework',
    'ClimateESGAIGovernanceFramework',
    'CrossBorderAIGovernanceFramework',
    'CybersecurityAIGovernanceFramework',
    'AISupplyChainGovernanceFramework',
    'FoundationModelGovernanceFramework',
    'HumanResourcesAIGovernanceFramework',
    'IndustryFrameworkRegistry',
    'get_industry_framework',
    'list_available_industries'
]

# Industry Framework Registry
INDUSTRY_FRAMEWORKS: Dict[str, Type[AIGovernanceFramework]] = {
    'banking': BankingAIGovernanceFramework,
    'healthcare': HealthcareAIGovernanceFramework,
    'manufacturing': ManufacturingAIGovernanceFramework,
    'transportation': TransportationAIGovernanceFramework,
    'energy': EnergyAIGovernanceFramework,
    'insurance': InsuranceAIGovernanceFramework,
    'legal': LegalAIGovernanceFramework,
    'telecommunications': TelecommunicationsAIGovernanceFramework,
    'retail': RetailAIGovernanceFramework,
    'media': MediaAIGovernanceFramework,
    'government': GovernmentAIGovernanceFramework,
    'education': EducationAIGovernanceFramework,
    'defense': DefenseAIGovernanceFramework,
    'biotechnology': BiotechnologyAIGovernanceFramework,
    'climate_esg': ClimateESGAIGovernanceFramework,
    'cross_border': CrossBorderAIGovernanceFramework,
    'cybersecurity': CybersecurityAIGovernanceFramework,
    'ai_supply_chain': AISupplyChainGovernanceFramework,
    'foundation_models': FoundationModelGovernanceFramework,
    'human_resources': HumanResourcesAIGovernanceFramework,
}

class IndustryFrameworkRegistry:
    """Registry for managing industry-specific AI governance frameworks"""
    
    @staticmethod
    def get_framework(industry: str) -> Type[AIGovernanceFramework]:
        """Get the governance framework class for a specific industry"""
        if industry not in INDUSTRY_FRAMEWORKS:
            raise ValueError(f"Industry '{industry}' not supported. Available: {list(INDUSTRY_FRAMEWORKS.keys())}")
        return INDUSTRY_FRAMEWORKS[industry]
    
    @staticmethod
    def list_industries() -> List[str]:
        """List all available industry frameworks"""
        return list(INDUSTRY_FRAMEWORKS.keys())
    
    @staticmethod
    def create_framework(industry: str, **kwargs) -> AIGovernanceFramework:
        """Create an instance of the specified industry framework"""
        framework_class = IndustryFrameworkRegistry.get_framework(industry)
        return framework_class(**kwargs)

def get_industry_framework(industry: str) -> Type[AIGovernanceFramework]:
    """Convenience function to get industry framework"""
    return IndustryFrameworkRegistry.get_framework(industry)

def list_available_industries() -> List[str]:
    """Convenience function to list available industries"""
    return IndustryFrameworkRegistry.list_industries()