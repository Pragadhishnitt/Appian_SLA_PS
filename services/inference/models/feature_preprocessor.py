"""
Feature Preprocessor for Inference Service
Replicates the feature engineering from Model_Train for consistent predictions
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime


class FeaturePreprocessor:
    """Replicates training feature engineering for inference"""
    
    # ========== COMMON MAPPINGS ==========
    ACTIVITY_MAP = {
        "Submit Application": 0, "Check Credit": 1, "Manual Review": 2,
        "Quality Assurance": 3, "Approve": 4, "Reject": 5
    }
    
    TIER_MAP = {'Bronze': 0, 'Silver': 1, 'Gold': 2, 'Platinum': 3}
    REGION_MAP = {'North': 0, 'South': 1, 'East': 2, 'West': 3}
    
    # Activity base durations (from process config)
    ACTIVITY_BASE_DURATION = {
        "Submit Application": 0.1, "Check Credit": 2.0, "Manual Review": 4.0,
        "Quality Assurance": 1.5, "Approve": 0.5, "Reject": 0.3
    }
    
    TIER_SPEED_MODIFIER = {'Bronze': 1.2, 'Silver': 1.1, 'Gold': 1.0, 'Platinum': 0.8}
    
    # ========== DURATION MODEL FEATURES (26 features) ==========
    # Must match train_duration_model.py create_duration_features()
    DURATION_FEATURES = [
        'activity_encoded', 'tier_encoded', 'region_encoded', 'complexity_score', 'priority',
        'assigned_hour', 'assigned_day_of_week', 'assigned_month',
        'is_weekend', 'is_business_hours', 'is_peak_hour', 'is_night_shift',
        'is_monday', 'is_friday',
        'activity_base_duration', 'expected_duration', 'complexity_duration_modifier',
        'workload_proxy', 'tier_speed_modifier',
        'resource_task_count', 'resource_activity_variety', 'activity_frequency',
        'complexity_x_activity', 'loan_amount_log', 'priority_x_complexity', 'expected_x_workload'
    ]
    
    # ========== ROUTING MODEL FEATURES (17 features) ==========
    # Must match train_routing_model.py create_routing_features()
    ROUTING_FEATURES = [
        'current_activity_encoded', 'tier_encoded', 'region_encoded', 'complexity_score',
        'position_in_process', 'progress_ratio', 'priority',
        'hour_of_day', 'day_of_week', 'month', 'is_weekend', 'is_business_hours',
        'is_start_of_process', 'resource_sample_count',
        'complexity_x_position', 'loan_amount_log', 'prev_activity_count'
    ]
    
    # ========== SLA MODEL FEATURES ==========
    # SLA uses feature_engineering.py + additional SLA-specific features
    # This is a simplified version for inference
    SLA_FEATURES = [
        'activity_encoded', 'tier_encoded', 'region_encoded', 'complexity_score', 'priority',
        'hour_of_day', 'day_of_week', 'is_weekend', 'is_business_hours',
        'hours_to_sla', 'sla_urgent', 'sla_critical', 'sla_pressure_ratio',
        'loan_amount_log', 'elapsed_time_hours'
    ]
    
    @classmethod
    def preprocess_duration(cls, raw_input: Dict[str, Any]) -> np.ndarray:
        """Preprocess features for duration prediction - 26 features"""
        
        # Extract raw inputs with defaults
        activity = raw_input.get('activity', 'Manual Review')
        customer_tier = raw_input.get('customer_tier', 'Silver')
        complexity_score = float(raw_input.get('complexity_score', 5.0))
        region = raw_input.get('region', 'North')
        loan_amount = float(raw_input.get('loan_amount', 50000))
        priority = int(raw_input.get('priority', 3))
        
        # Get current time for temporal features
        now = datetime.now()
        assigned_hour = int(raw_input.get('assigned_hour', now.hour))
        assigned_day_of_week = int(raw_input.get('assigned_day_of_week', now.weekday()))
        assigned_month = int(raw_input.get('assigned_month', now.month))
        
        # Basic encodings
        activity_encoded = cls.ACTIVITY_MAP.get(activity, 2)
        tier_encoded = cls.TIER_MAP.get(customer_tier, 1)
        region_encoded = cls.REGION_MAP.get(region, 0)
        
        # Temporal flags
        is_weekend = 1 if assigned_day_of_week >= 5 else 0
        is_business_hours = 1 if 9 <= assigned_hour <= 17 else 0
        is_peak_hour = 1 if 10 <= assigned_hour <= 15 else 0
        is_night_shift = 1 if assigned_hour < 6 or assigned_hour > 22 else 0
        is_monday = 1 if assigned_day_of_week == 0 else 0
        is_friday = 1 if assigned_day_of_week == 4 else 0
        
        # Process knowledge features
        activity_base_duration = cls.ACTIVITY_BASE_DURATION.get(activity, 2.0)
        complexity_duration_modifier = 1.0 + (complexity_score - 5) * 0.1
        expected_duration = activity_base_duration * complexity_duration_modifier
        
        # Workload proxy based on hour
        if 9 <= assigned_hour <= 11:
            workload_proxy = 1.3
        elif 14 <= assigned_hour <= 16:
            workload_proxy = 1.2
        elif assigned_hour < 7 or assigned_hour > 19:
            workload_proxy = 0.8
        else:
            workload_proxy = 1.0
        
        tier_speed_modifier = cls.TIER_SPEED_MODIFIER.get(customer_tier, 1.0)
        
        # Resource features (defaults for inference)
        resource_task_count = float(raw_input.get('resource_task_count', 100))
        resource_activity_variety = float(raw_input.get('resource_activity_variety', 5))
        activity_frequency = float(raw_input.get('activity_frequency', 500))
        
        # Interaction features
        complexity_x_activity = complexity_score * activity_encoded
        loan_amount_log = np.log1p(loan_amount)
        priority_x_complexity = priority * complexity_score
        expected_x_workload = expected_duration * workload_proxy
        
        # Build feature array in EXACT order matching training
        features = [
            activity_encoded, tier_encoded, region_encoded, complexity_score, priority,
            assigned_hour, assigned_day_of_week, assigned_month,
            is_weekend, is_business_hours, is_peak_hour, is_night_shift,
            is_monday, is_friday,
            activity_base_duration, expected_duration, complexity_duration_modifier,
            workload_proxy, tier_speed_modifier,
            resource_task_count, resource_activity_variety, activity_frequency,
            complexity_x_activity, loan_amount_log, priority_x_complexity, expected_x_workload
        ]
        
        return np.array([features], dtype=np.float32)
    
    @classmethod
    def preprocess_routing(cls, raw_input: Dict[str, Any]) -> np.ndarray:
        """Preprocess features for routing prediction - 17 features"""
        
        activity = raw_input.get('current_activity', raw_input.get('activity', 'Manual Review'))
        customer_tier = raw_input.get('customer_tier', 'Silver')
        complexity_score = float(raw_input.get('complexity_score', 5.0))
        region = raw_input.get('region', 'North')
        loan_amount = float(raw_input.get('loan_amount', 50000))
        priority = int(raw_input.get('priority', 3))
        position_in_process = int(raw_input.get('position_in_process', 1))
        progress_ratio = float(raw_input.get('progress_ratio', 0.5))
        prev_activity_count = int(raw_input.get('prev_activity_count', 1))
        
        now = datetime.now()
        hour_of_day = int(raw_input.get('hour_of_day', now.hour))
        day_of_week = int(raw_input.get('day_of_week', now.weekday()))
        month = int(raw_input.get('month', now.month))
        
        current_activity_encoded = cls.ACTIVITY_MAP.get(activity, 2)
        tier_encoded = cls.TIER_MAP.get(customer_tier, 1)
        region_encoded = cls.REGION_MAP.get(region, 0)
        
        is_weekend = 1 if day_of_week >= 5 else 0
        is_business_hours = 1 if 9 <= hour_of_day <= 17 else 0
        is_start_of_process = 1 if position_in_process == 1 else 0
        resource_sample_count = float(raw_input.get('resource_sample_count', 100))
        complexity_x_position = complexity_score * position_in_process
        loan_amount_log = np.log1p(loan_amount)
        
        features = [
            current_activity_encoded, tier_encoded, region_encoded, complexity_score,
            position_in_process, progress_ratio, priority,
            hour_of_day, day_of_week, month, is_weekend, is_business_hours,
            is_start_of_process, resource_sample_count,
            complexity_x_position, loan_amount_log, prev_activity_count
        ]
        
        return np.array([features], dtype=np.float32)
    
    @classmethod
    def preprocess_sla_breach(cls, raw_input: Dict[str, Any]) -> np.ndarray:
        """Preprocess features for SLA breach prediction"""
        
        activity = raw_input.get('activity', 'Manual Review')
        customer_tier = raw_input.get('customer_tier', 'Silver')
        complexity_score = float(raw_input.get('complexity_score', 5.0))
        region = raw_input.get('region', 'North')
        loan_amount = float(raw_input.get('loan_amount', 50000))
        priority = int(raw_input.get('priority', 3))
        elapsed_time = float(raw_input.get('elapsed_time', 0))
        hours_to_sla = float(raw_input.get('hours_to_sla', 24))
        
        now = datetime.now()
        hour_of_day = int(raw_input.get('hour_of_day', now.hour))
        day_of_week = int(raw_input.get('day_of_week', now.weekday()))
        
        activity_encoded = cls.ACTIVITY_MAP.get(activity, 2)
        tier_encoded = cls.TIER_MAP.get(customer_tier, 1)
        region_encoded = cls.REGION_MAP.get(region, 0)
        
        is_weekend = 1 if day_of_week >= 5 else 0
        is_business_hours = 1 if 9 <= hour_of_day <= 17 else 0
        
        sla_urgent = 1 if hours_to_sla <= 4 else 0
        sla_critical = 1 if hours_to_sla <= 1 else 0
        sla_pressure_ratio = hours_to_sla / 24
        loan_amount_log = np.log1p(loan_amount)
        
        features = [
            activity_encoded, tier_encoded, region_encoded, complexity_score, priority,
            hour_of_day, day_of_week, is_weekend, is_business_hours,
            hours_to_sla, sla_urgent, sla_critical, sla_pressure_ratio,
            loan_amount_log, elapsed_time
        ]
        
        return np.array([features], dtype=np.float32)
    
    @classmethod
    def get_feature_names(cls, model_type: str) -> List[str]:
        """Get feature names for a given model type"""
        if 'duration' in model_type.lower():
            return cls.DURATION_FEATURES
        elif 'routing' in model_type.lower():
            return cls.ROUTING_FEATURES
        elif 'sla' in model_type.lower() or 'breach' in model_type.lower():
            return cls.SLA_FEATURES
        else:
            return cls.DURATION_FEATURES
