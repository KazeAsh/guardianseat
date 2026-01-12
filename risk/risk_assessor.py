import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from scipy import stats

class RadarRiskAssessor:
    """
    Advanced risk assessment using mmWave radar and sensor fusion
    Evaluates child safety risk based on multiple factors
    """
    
    def __init__(self):
        # Risk thresholds (configurable)
        self.TEMP_DANGER = 40.0  # °C - Immediate danger
        self.TEMP_WARNING = 26.0  # °C - Warning level
        self.TIME_CRITICAL = 30  # minutes - Critical time
        self.TIME_WARNING = 10   # minutes - Warning time
        
        # Vital sign thresholds
        self.CHILD_HR_MIN = 80   # BPM - Minimum child heart rate
        self.CHILD_HR_MAX = 120  # BPM - Maximum child heart rate
        self.ADULT_HR_MIN = 60   # BPM - Minimum adult heart rate
        self.ADULT_HR_MAX = 100  # BPM - Maximum adult heart rate
        
        # Risk weights (sum to 1.0)
        self.weights = {
            'temperature': 0.25,
            'time_elapsed': 0.20,
            'vital_signs': 0.25,
            'environmental': 0.15,
            'vehicle_state': 0.15
        }
        
        # Load historical patterns for anomaly detection
        self._load_normal_patterns()
    
    def _load_normal_patterns(self):
        """Load/define normal patterns for anomaly detection"""
        # These would normally be trained on historical data
        self.normal_patterns = {
            'child_hr_mean': 100,  # Average child heart rate
            'child_hr_std': 10,    # Standard deviation
            'child_br_mean': 25,   # Average child breathing rate
            'child_br_std': 5,
            'car_temp_rise_rate': 0.5,  # °C per minute in hot car
        }
    
    def assess_risk(self, radar_data: Dict, car_sensors: Dict, 
                   environmental: Dict, time_elapsed_min: float) -> Dict:
        """
        Comprehensive risk assessment combining all data sources
        
        Returns:
            Dictionary with risk scores, assessment, and recommendations
        """
        
        # Calculate individual risk components
        temp_risk = self._temperature_risk(car_sensors.get('temperature_c', 25))
        time_risk = self._time_risk(time_elapsed_min)
        vital_risk = self._vital_signs_risk(radar_data.get('vital_signs', {}))
        env_risk = self._environmental_risk(environmental)
        vehicle_risk = self._vehicle_state_risk(car_sensors)
        
        # Weighted total risk
        total_risk = (
            temp_risk * self.weights['temperature'] +
            time_risk * self.weights['time_elapsed'] +
            vital_risk * self.weights['vital_signs'] +
            env_risk * self.weights['environmental'] +
            vehicle_risk * self.weights['vehicle_state']
        )
        
        # Clamp to [0, 1]
        total_risk = max(0, min(1, total_risk))
        
        # Determine risk level and actions
        risk_level, actions = self._determine_risk_level(total_risk, {
            'temperature': car_sensors.get('temperature_c', 25),
            'time_elapsed': time_elapsed_min,
            'vital_signs': radar_data.get('vital_signs', {}),
            'vital_signs_detected': radar_data.get('vital_signs', {}).get('vital_signs_detected', False)
        })
        
        # Anomaly detection
        anomalies = self._detect_anomalies(radar_data, car_sensors, time_elapsed_min)
        
        # Confidence score (how reliable is our assessment)
        confidence = self._calculate_confidence(radar_data, car_sensors)
        
        return {
            'risk_components': {
                'temperature_risk': round(temp_risk, 3),
                'time_risk': round(time_risk, 3),
                'vital_signs_risk': round(vital_risk, 3),
                'environmental_risk': round(env_risk, 3),
                'vehicle_state_risk': round(vehicle_risk, 3)
            },
            'total_risk': round(total_risk, 3),
            'risk_level': risk_level,
            'confidence': round(confidence, 3),
            'anomalies_detected': anomalies,
            'recommended_actions': actions,
            'timestamp': datetime.now().isoformat(),
            'assessment_summary': self._generate_summary(
                total_risk, risk_level, radar_data, car_sensors, time_elapsed_min
            )
        }
    
    def _temperature_risk(self, temperature_c: float) -> float:
        """Calculate risk based on temperature"""
        if temperature_c >= self.TEMP_DANGER:
            return 1.0
        elif temperature_c >= self.TEMP_WARNING:
            # Linear increase from warning to danger
            return (temperature_c - self.TEMP_WARNING) / (self.TEMP_DANGER - self.TEMP_WARNING)
        else:
            return 0.0
    
    def _time_risk(self, minutes_elapsed: float) -> float:
        """Calculate risk based on time elapsed"""
        if minutes_elapsed >= self.TIME_CRITICAL:
            return 1.0
        elif minutes_elapsed >= self.TIME_WARNING:
            return (minutes_elapsed - self.TIME_WARNING) / (self.TIME_CRITICAL - self.TIME_WARNING)
        else:
            return 0.0
    
    def _vital_signs_risk(self, vital_signs: Dict) -> float:
        """
        Calculate risk based on vital signs quality and patterns
        Higher risk if vital signs are detected (child present) but quality is poor
        """
        if not vital_signs.get('vital_signs_detected', False):
            return 0.0  # No vital signs = likely no child
        
        heart_rate = vital_signs.get('heart_rate_bpm', 0)
        breathing_rate = vital_signs.get('breathing_rate_bpm', 0)
        heartbeat_conf = vital_signs.get('heartbeat_confidence', 0)
        breathing_conf = vital_signs.get('breathing_confidence', 0)
        
        # Risk increases if vital signs are abnormal
        risk = 0.0
        
        # Check if heart rate is in child range but confidence is low
        if self.CHILD_HR_MIN <= heart_rate <= self.CHILD_HR_MAX:
            # Child detected - this increases risk if conditions are dangerous
            # But low confidence adds uncertainty risk
            if heartbeat_conf < 0.5:
                risk += 0.3  # Uncertainty penalty
        elif heart_rate > 0:  # Vital signs detected but not child-like
            risk += 0.2  # Unexpected pattern
        
        # Check breathing rate
        if 20 <= breathing_rate <= 30:  # Normal child breathing
            if breathing_conf < 0.5:
                risk += 0.2
        elif breathing_rate > 0:
            risk += 0.1
        
        # Overall confidence penalty
        avg_confidence = (heartbeat_conf + breathing_conf) / 2
        risk += (1 - avg_confidence) * 0.5
        
        return min(risk, 1.0)
    
    def _environmental_risk(self, environmental: Dict) -> float:
        """Calculate risk based on environmental conditions"""
        risk = 0.0
        
        # Temperature (already considered separately, but outdoor temp matters)
        outdoor_temp = environmental.get('temperature_c', 25)
        if outdoor_temp > 30:
            risk += 0.3
        elif outdoor_temp > 25:
            risk += 0.1
        
        # Humidity (high humidity reduces cooling)
        humidity = environmental.get('humidity', 50)
        if humidity > 70:
            risk += 0.2
        
        # Sun exposure (estimated)
        weather = environmental.get('weather', '').lower()
        if 'clear' in weather or 'sunny' in weather:
            risk += 0.2
        
        # Time of day (midday is hottest)
        hour = datetime.now().hour
        if 12 <= hour <= 16:  # 12 PM to 4 PM
            risk += 0.2
        
        return min(risk, 1.0)
    
    def _vehicle_state_risk(self, car_sensors: Dict) -> float:
        """Calculate risk based on vehicle state"""
        risk = 0.0
        
        # Engine off increases risk
        if car_sensors.get('engine_state') == 'off':
            risk += 0.4
        
        # Doors closed increases risk
        if car_sensors.get('door_state') == 'closed':
            risk += 0.4
        
        # Windows up (estimated - would need window sensors)
        # For now, assume risk if doors closed and engine off
        if (car_sensors.get('door_state') == 'closed' and 
            car_sensors.get('engine_state') == 'off'):
            risk += 0.2
        
        return min(risk, 1.0)
    
    def _determine_risk_level(self, total_risk: float, context: Dict) -> Tuple[str, List[str]]:
        """Determine risk level and recommended actions"""
        
        if total_risk >= 0.8:
            level = "CRITICAL"
            actions = [
                "IMMEDIATE: Contact emergency services (911)",
                "Alert vehicle owner with emergency notification",
                "Activate vehicle horn and lights",
                "If possible, remotely activate climate control",
                "Dispatch security/law enforcement to location"
            ]
        
        elif total_risk >= 0.6:
            level = "HIGH"
            actions = [
                "URGENT: Send emergency alert to vehicle owner",
                "Activate vehicle alarm system",
                "Send notification to backup contacts",
                "Monitor vital signs continuously",
                "Prepare emergency services dispatch"
            ]
        
        elif total_risk >= 0.4:
            level = "MODERATE"
            actions = [
                "WARNING: Send alert to vehicle owner",
                "Check if this is a false positive",
                "Monitor situation for 5 minutes",
                "Alert backup contact",
                "Record all sensor data for analysis"
            ]
        
        elif total_risk >= 0.2:
            level = "LOW"
            actions = [
                "NOTIFICATION: Send informational alert",
                "Monitor for changes",
                "Check environmental conditions",
                "Update risk assessment in 2 minutes"
            ]
        
        else:
            level = "SAFE"
            actions = [
                "Continue routine monitoring",
                "Log normal conditions",
                "Update dashboard status"
            ]
        
        # Add context-specific actions
        if context.get('temperature', 25) > 35:
            actions.append("⚠️ High temperature detected - expedite response")
        
        if context.get('time_elapsed', 0) > 20:
            actions.append("⏰ Vehicle occupied for extended period")
        
        if context.get('vital_signs_detected', False):
            actions.append("👶 Child detected via mmWave radar")
        
        return level, actions
    
    def _detect_anomalies(self, radar_data: Dict, car_sensors: Dict, 
                         time_elapsed: float) -> List[Dict]:
        """Detect anomalous patterns that might indicate problems"""
        anomalies = []
        
        vital_signs = radar_data.get('vital_signs', {})
        heart_rate = vital_signs.get('heart_rate_bpm', 0)
        breathing_rate = vital_signs.get('breathing_rate_bpm', 0)
        
        # 1. Vital sign anomalies
        if vital_signs.get('vital_signs_detected', False):
            # Check if heart rate is abnormally high/low for child
            if self.CHILD_HR_MIN <= heart_rate <= self.CHILD_HR_MAX:
                # Calculate z-score for anomaly detection
                z_score = abs(heart_rate - self.normal_patterns['child_hr_mean']) / self.normal_patterns['child_hr_std']
                if z_score > 2.0:
                    anomalies.append({
                        'type': 'abnormal_heart_rate',
                        'severity': 'high' if z_score > 3 else 'medium',
                        'value': heart_rate,
                        'expected_range': f"{self.CHILD_HR_MIN}-{self.CHILD_HR_MAX} BPM",
                        'description': f"Heart rate {heart_rate} BPM is statistically unusual"
                    })
            
            # Check breathing rate
            if 10 <= breathing_rate <= 40:  # Plausible range
                z_score = abs(breathing_rate - self.normal_patterns['child_br_mean']) / self.normal_patterns['child_br_std']
                if z_score > 2.0:
                    anomalies.append({
                        'type': 'abnormal_breathing',
                        'severity': 'medium',
                        'value': breathing_rate,
                        'expected_range': "20-30 breaths/min",
                        'description': f"Breathing rate {breathing_rate} BPM is unusual"
                    })
        
        # 2. Temperature rise anomaly
        temp = car_sensors.get('temperature_c', 25)
        expected_rise = time_elapsed * self.normal_patterns['car_temp_rise_rate']
        if temp > 30 and time_elapsed > 10:
            actual_rise = temp - 25  # Assuming starting at 25°C
            if actual_rise > expected_rise * 1.5:
                anomalies.append({
                    'type': 'rapid_temperature_rise',
                    'severity': 'high',
                    'temperature': temp,
                    'time_elapsed': time_elapsed,
                    'description': f"Temperature rising faster than expected: {actual_rise:.1f}°C in {time_elapsed:.0f}min"
                })
        
        # 3. Signal quality anomalies
        quality = radar_data.get('quality_metrics', {})
        if quality.get('overall_quality', 0) < 0.3:
            anomalies.append({
                'type': 'poor_signal_quality',
                'severity': 'medium',
                'value': quality.get('overall_quality', 0),
                'description': "Low mmWave signal quality - may affect vital sign detection"
            })
        
        # 4. Motion artifact when expecting stillness
        motion = radar_data.get('motion_artifact', {})
        if motion.get('has_motion_artifact', False) and time_elapsed > 15:
            anomalies.append({
                'type': 'unexpected_movement',
                'severity': 'low',
                'movement_index': motion.get('movement_index', 0),
                'description': "Movement detected in stationary vehicle"
            })
        
        return anomalies
    
    def _calculate_confidence(self, radar_data: Dict, car_sensors: Dict) -> float:
        """Calculate confidence in risk assessment"""
        confidence = 1.0
        
        # Reduce confidence based on data quality
        quality = radar_data.get('quality_metrics', {})
        overall_quality = quality.get('overall_quality', 0.5)
        confidence *= overall_quality
        
        # Reduce confidence if sensor data is sparse
        sensor_count = sum(1 for key in ['temperature_c', 'door_state', 'engine_state'] 
                          if key in car_sensors)
        sensor_confidence = sensor_count / 3
        confidence *= sensor_confidence
        
        # Reduce confidence if vital signs have low confidence
        vital_signs = radar_data.get('vital_signs', {})
        vital_confidence = (vital_signs.get('heartbeat_confidence', 0) + 
                          vital_signs.get('breathing_confidence', 0)) / 2
        confidence *= max(0.3, vital_confidence)  # Don't reduce below 0.3
        
        return confidence
    
    def _generate_summary(self, total_risk: float, risk_level: str,
                         radar_data: Dict, car_sensors: Dict, 
                         time_elapsed: float) -> str:
        """Generate human-readable risk summary"""
        
        vital_signs = radar_data.get('vital_signs', {})
        temp = car_sensors.get('temperature_c', 25)
        
        if risk_level == "CRITICAL":
            return f"🚨 CRITICAL RISK: Child detected in vehicle for {time_elapsed:.0f}min at {temp}°C. " \
                   f"Heart rate: {vital_signs.get('heart_rate_bpm', 'N/A')} BPM. " \
                   f"IMMEDIATE ACTION REQUIRED."
        
        elif risk_level == "HIGH":
            return f"⚠️ HIGH RISK: Possible child in vehicle for {time_elapsed:.0f}min. " \
                   f"Temperature: {temp}°C. Urgent attention needed."
        
        elif risk_level == "MODERATE":
            return f"🔶 MODERATE RISK: Vehicle occupied for {time_elapsed:.0f}min. " \
                   f"Temperature: {temp}°C. Monitor closely."
        
        elif risk_level == "LOW":
            return f"🔸 LOW RISK: Vehicle conditions normal. " \
                   f"Time elapsed: {time_elapsed:.0f}min, Temperature: {temp}°C."
        
        else:
            return f"✅ SAFE: No significant risk detected. " \
                   f"Monitoring normal conditions."
    
    def generate_report(self, risk_assessment: Dict, scenario_id: str = None) -> Dict:
        """Generate comprehensive risk report"""
        
        report = {
            'report_id': f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'scenario_id': scenario_id,
            'generated_at': datetime.now().isoformat(),
            'risk_assessment': risk_assessment,
            'statistics': {
                'risk_distribution': self._calculate_statistics(risk_assessment),
                'trend_analysis': self._analyze_trends(risk_assessment)
            },
            'compliance_check': self._check_compliance(risk_assessment),
            'export_formats': ['json', 'csv', 'pdf']  # Available export formats
        }
        
        return report
    
    def _calculate_statistics(self, risk_assessment: Dict) -> Dict:
        """Calculate statistics for reporting"""
        components = risk_assessment.get('risk_components', {})
        
        return {
            'highest_risk_component': max(components.items(), key=lambda x: x[1])[0],
            'average_component_risk': np.mean(list(components.values())),
            'risk_variance': np.var(list(components.values())),
            'dominant_factors': [k for k, v in components.items() if v > 0.3]
        }
    
    def _analyze_trends(self, risk_assessment: Dict) -> Dict:
        """Analyze risk trends (in real system would compare with historical)"""
        # Simplified trend analysis
        total_risk = risk_assessment.get('total_risk', 0)
        
        if total_risk > 0.7:
            trend = "rapidly_increasing"
        elif total_risk > 0.4:
            trend = "increasing"
        elif total_risk > 0.1:
            trend = "stable"
        else:
            trend = "decreasing"
        
        return {
            'trend': trend,
            'stability': 'unstable' if total_risk > 0.6 else 'stable',
            'projected_risk_in_10min': min(1.0, total_risk * 1.5)  # Simplified projection
        }
    
    def _check_compliance(self, risk_assessment: Dict) -> Dict:
        """Check compliance with safety standards"""
        # Simplified compliance check
        temp = risk_assessment.get('assessment_summary', '')
        risk_level = risk_assessment.get('risk_level', 'SAFE')
        
        standards = {
            'iso_26262': risk_level in ['SAFE', 'LOW'],  # Automotive safety
            'gdpr': True,  # Privacy compliance (mmWave is privacy-friendly)
            'nhtsa_guidelines': risk_level != 'CRITICAL',  # US automotive safety
            'ece_r100': True  # UN vehicle safety regulation
        }
        
        return {
            'compliance_status': all(standards.values()),
            'standards': standards,
            'notes': 'mmWave radar ensures privacy compliance by not capturing personal identifiers'
        }

# Test the risk assessor
if __name__ == "__main__":
    print("🔍 GuardianSensor: Risk Assessment Engine")
    print("=" * 60)
    
    # Initialize risk assessor
    assessor = RadarRiskAssessor()
    
    # Create test data
    radar_data = {
        'vital_signs': {
            'breathing_rate_bpm': 22.5,
            'heart_rate_bpm': 105.3,
            'breathing_confidence': 0.7,
            'heartbeat_confidence': 0.8,
            'vital_signs_detected': True,
            'occupant_type': 'child',
            'type_confidence': 0.75
        },
        'quality_metrics': {
            'breathing_snr_db': 15.2,
            'heartbeat_snr_db': 12.8,
            'overall_quality': 0.65
        },
        'motion_artifact': {
            'movement_index': 0.05,
            'has_motion_artifact': False
        }
    }
    
    car_sensors = {
        'temperature_c': 38.5,
        'seat_pressure_kg': 18.2,
        'door_state': 'closed',
        'engine_state': 'off',
        'co2_ppm': 850,
        'humidity_percent': 65
    }
    
    environmental = {
        'temperature_c': 32.5,
        'humidity': 60,
        'weather': 'Clear',
        'city': 'Tokyo'
    }
    
    time_elapsed_min = 25.5
    
    # Assess risk
    print("\n1. Assessing risk scenario...")
    risk_assessment = assessor.assess_risk(
        radar_data, car_sensors, environmental, time_elapsed_min
    )
    
    print(f"\n2. Risk Assessment Results:")
    print(f"   Overall Risk: {risk_assessment['total_risk']:.3f}")
    print(f"   Risk Level: {risk_assessment['risk_level']}")
    print(f"   Confidence: {risk_assessment['confidence']:.3f}")
    
    print(f"\n3. Risk Components:")
    for component, value in risk_assessment['risk_components'].items():
        print(f"   {component}: {value:.3f}")
    
    print(f"\n4. Anomalies Detected:")
    if risk_assessment['anomalies_detected']:
        for anomaly in risk_assessment['anomalies_detected']:
            print(f"   - {anomaly['type']}: {anomaly['description']}")
    else:
        print("   No anomalies detected")
    
    print(f"\n5. Recommended Actions:")
    for i, action in enumerate(risk_assessment['recommended_actions'], 1):
        print(f"   {i}. {action}")
    
    print(f"\n6. Assessment Summary:")
    print(f"   {risk_assessment['assessment_summary']}")
    
    # Generate comprehensive report
    print("\n7. Generating risk report...")
    report = assessor.generate_report(risk_assessment, scenario_id="test_001")
    
    print(f"\n Risk assessment complete!")
    print(f"Report ID: {report['report_id']}")
    print(f"Compliance: {'Compliant' if report['compliance_check']['compliance_status'] else 'Non-compliant!!'}")