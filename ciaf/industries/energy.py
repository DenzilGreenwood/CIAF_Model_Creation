"""
Energy AI Governance Framework
==============================

Comprehensive AI governance for energy and utility systems including:
- Power grid optimization and smart grid management
- Renewable energy forecasting and integration
- Critical infrastructure protection and cybersecurity
- Environmental compliance and emissions monitoring
- Nuclear safety and radiation protection (NRC regulations)
- NERC CIP (North American Electric Reliability Corporation Critical Infrastructure Protection)
- FERC compliance for wholesale energy markets
- Smart meter privacy and consumer protection
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from ciaf.core.interfaces import AIGovernanceFramework
from ciaf.compliance.bias_validator import BiasValidator
from ciaf.compliance.audit_trails import AuditTrail
from ciaf.compliance.validators import ComplianceValidator

class GridStabilityLevel(Enum):
    """Grid stability classification levels"""
    CRITICAL = "critical"
    MARGINAL = "marginal"
    STABLE = "stable"
    OPTIMAL = "optimal"

class EnergySource(Enum):
    """Energy generation source types"""
    NUCLEAR = "nuclear"
    COAL = "coal"
    NATURAL_GAS = "natural_gas"
    WIND = "wind"
    SOLAR = "solar"
    HYDROELECTRIC = "hydroelectric"

@dataclass
class GridStabilityAssessment:
    """Grid stability and reliability assessment"""
    assessment_id: str
    grid_region: str
    stability_level: GridStabilityLevel
    frequency_deviation: float
    voltage_stability_margin: float
    load_forecast_accuracy: float
    renewable_penetration: float
    assessment_timestamp: datetime
    analyst_id: str
    
    def calculate_stability_score(self) -> float:
        """Calculate overall grid stability score"""
        freq_score = max(0, 1 - abs(self.frequency_deviation) / 0.5)
        voltage_score = min(1.0, self.voltage_stability_margin / 0.3)
        forecast_score = self.load_forecast_accuracy
        
        return (freq_score * 0.4 + voltage_score * 0.3 + forecast_score * 0.3)

@dataclass
class RenewableIntegrationResult:
    """Renewable energy integration assessment"""
    integration_id: str
    energy_source: EnergySource
    capacity_mw: float
    forecasted_output: float
    actual_output: float
    forecast_error: float
    integration_timestamp: datetime
    
    def calculate_forecast_accuracy(self) -> float:
        """Calculate renewable energy forecast accuracy"""
        if self.forecasted_output == 0:
            return 0.0
        return 1.0 - abs(self.forecast_error) / self.forecasted_output

class EnergyAIGovernanceFramework(AIGovernanceFramework):
    """
    Energy AI Governance Framework for power grid and utility systems
    """
    
    def __init__(self, utility_id: str, grid_region: str, **kwargs):
        super().__init__(**kwargs)
        self.utility_id = utility_id
        self.grid_region = grid_region
        self.bias_validator = BiasValidator()
        self.audit_trail = AuditTrail()
        self.compliance_validator = ComplianceValidator()
        
        self.regulatory_standards = [
            "NERC_CIP", "NERC_BAL", "FERC_Order_841",
            "EPA_CAA", "NRC_10_CFR", "IEEE_1547"
        ]
        
        self.grid_assessments = {}
        self.renewable_integrations = {}
    
    def assess_grid_stability(
        self,
        assessment_id: str,
        frequency_deviation: float,
        voltage_stability_margin: float,
        load_forecast_accuracy: float,
        renewable_penetration: float,
        **kwargs
    ) -> GridStabilityAssessment:
        """Assess grid stability and reliability"""
        
        # Determine stability level
        if abs(frequency_deviation) > 0.3 or voltage_stability_margin < 0.1:
            stability_level = GridStabilityLevel.CRITICAL
        elif abs(frequency_deviation) > 0.1 or voltage_stability_margin < 0.2:
            stability_level = GridStabilityLevel.MARGINAL
        else:
            stability_level = GridStabilityLevel.STABLE
        
        assessment = GridStabilityAssessment(
            assessment_id=assessment_id,
            grid_region=self.grid_region,
            stability_level=stability_level,
            frequency_deviation=frequency_deviation,
            voltage_stability_margin=voltage_stability_margin,
            load_forecast_accuracy=load_forecast_accuracy,
            renewable_penetration=renewable_penetration,
            assessment_timestamp=datetime.now(),
            analyst_id=kwargs.get('analyst_id', 'grid_operator')
        )
        
        self.grid_assessments[assessment_id] = assessment
        
        self.audit_trail.log_event(
            event_type="grid_stability_assessment",
            details={
                "assessment_id": assessment_id,
                "stability_level": stability_level.value,
                "stability_score": assessment.calculate_stability_score()
            }
        )
        
        return assessment
    
    def validate_renewable_integration(
        self,
        integration_id: str,
        energy_source: EnergySource,
        capacity_mw: float,
        forecasted_output: float,
        actual_output: float,
        **kwargs
    ) -> RenewableIntegrationResult:
        """Validate renewable energy integration"""
        
        forecast_error = abs(forecasted_output - actual_output)
        
        result = RenewableIntegrationResult(
            integration_id=integration_id,
            energy_source=energy_source,
            capacity_mw=capacity_mw,
            forecasted_output=forecasted_output,
            actual_output=actual_output,
            forecast_error=forecast_error,
            integration_timestamp=datetime.now()
        )
        
        self.renewable_integrations[integration_id] = result
        
        self.audit_trail.log_event(
            event_type="renewable_integration",
            details={
                "integration_id": integration_id,
                "energy_source": energy_source.value,
                "forecast_accuracy": result.calculate_forecast_accuracy()
            }
        )
        
        return result