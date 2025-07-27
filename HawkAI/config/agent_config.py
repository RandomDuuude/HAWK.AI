from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    description: str
    capabilities: List[str]
    model: str
    response_time_target: float  # seconds
    priority_level: int  # 1 (highest) to 5 (lowest)

# Agent configurations
AGENT_CONFIGS = {
    "safety_monitoring": AgentConfig(
        name="Safety Monitoring Agent",
        description="Specialized in real-time safety assessment and risk monitoring",
        capabilities=[
            "crowd_density_analysis",
            "weather_risk_assessment", 
            "infrastructure_safety_check",
            "emergency_exit_evaluation"
        ],
        model=MODEL_NAME_FLASH_2,
        response_time_target=2.0,
        priority_level=1
    ),
    
    "data_analytics": AgentConfig(
        name="Data Analytics Agent", 
        description="Specialized in pattern analysis and predictive modeling",
        capabilities=[
            "historical_pattern_analysis",
            "anomaly_detection",
            "trend_prediction",
            "statistical_analysis"
        ],
        model=MODEL_NAME_FLASH_2,
        response_time_target=5.0,
        priority_level=2
    ),
    
    "alert_management": AgentConfig(
        name="Alert Management Agent",
        description="Specialized in emergency response and alert coordination", 
        capabilities=[
            "alert_prioritization",
            "response_plan_generation",
            "escalation_management",
            "resource_coordination"
        ],
        model=MODEL_NAME_FLASH_2,
        response_time_target=1.0,
        priority_level=1
    )
}

# Routing rules for the coordinator agent
ROUTING_RULES = {
    # Safety-related keywords
    "safety_keywords": [
        "crowd", "density", "exit", "emergency", "evacuation", "weather", 
        "risk", "hazard", "incident", "safety", "danger"
    ],
    
    # Analytics-related keywords  
    "analytics_keywords": [
        "pattern", "trend", "historical", "predict", "anomaly", "analysis",
        "statistics", "data", "metrics", "performance"
    ],
    
    # Alert-related keywords
    "alert_keywords": [
        "alert", "priority", "response", "escalate", "urgent", "critical",
        "emergency", "notification", "protocol"
    ]
}

def get_agent_for_query(query: str) -> str:
    """Determine which agent should handle a query based on keywords"""
    query_lower = query.lower()
    
    # Count keyword matches for each category
    safety_score = sum(1 for keyword in ROUTING_RULES["safety_keywords"] 
                      if keyword in query_lower)
    analytics_score = sum(1 for keyword in ROUTING_RULES["analytics_keywords"] 
                         if keyword in query_lower)  
    alert_score = sum(1 for keyword in ROUTING_RULES["alert_keywords"]
                     if keyword in query_lower)
    
    # Return agent with highest score
    scores = {
        "safety_monitoring": safety_score,
        "data_analytics": analytics_score, 
        "alert_management": alert_score
    }
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "safety_monitoring"