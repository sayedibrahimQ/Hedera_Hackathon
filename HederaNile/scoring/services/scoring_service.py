"""
AI Credit Scoring Service for NileFi.
Provides credit score calculation and explainability for SME loan applications.
"""

import numpy as np
from decimal import Decimal
from typing import Dict, Tuple, List
from django.conf import settings


class CreditScoringService:
    """
    AI-powered credit scoring for startups/SMEs.
    Uses a deterministic scoring algorithm with explainability.
    Can be upgraded to ML model (scikit-learn) with training data.
    """
    
    def __init__(self):
        self.enabled = settings.AI_SCORING_ENABLED
        
        # Feature weights for scoring (sum = 1.0)
        self.weights = {
            'revenue': 0.25,
            'business_age': 0.20,
            'monthly_sales': 0.20,
            'sector_risk': 0.15,
            'document_completeness': 0.10,
            'previous_funding': 0.10,
        }
        
        # Sector risk mapping (lower is better)
        self.sector_risks = {
            'technology': 0.3,
            'healthcare': 0.4,
            'fintech': 0.35,
            'manufacturing': 0.5,
            'agriculture': 0.6,
            'retail': 0.55,
            'services': 0.45,
            'energy': 0.5,
            'education': 0.4,
            'default': 0.5,
        }
    
    def calculate_score(self, startup_data: Dict) -> Tuple[float, str, Dict]:
        """
        Calculate credit score for a startup.
        
        Args:
            startup_data: Dict containing startup financial and business data
        
        Returns:
            Tuple of (score, risk_level, explanation)
            - score: 0-100
            - risk_level: 'Low', 'Medium', 'High'
            - explanation: Dict with feature importance
        """
        if not self.enabled:
            return 50.0, 'Medium', {}
        
        # Extract features
        features = self._extract_features(startup_data)
        
        # Calculate weighted score
        score = self._calculate_weighted_score(features)
        
        # Determine risk level
        risk_level = self._determine_risk_level(score)
        
        # Generate explanation
        explanation = self._generate_explanation(features, score)
        
        return score, risk_level, explanation
    
    def _extract_features(self, data: Dict) -> Dict:
        """Extract and normalize features from startup data"""
        
        # Revenue feature (normalize to 0-1)
        revenue = float(data.get('revenue', 0))
        revenue_score = min(revenue / 1_000_000, 1.0)  # Cap at 1M
        
        # Business age feature (normalize to 0-1)
        business_age_months = int(data.get('business_age_months', 0))
        age_score = min(business_age_months / 60, 1.0)  # Cap at 5 years
        
        # Monthly sales feature (normalize to 0-1)
        monthly_sales = float(data.get('monthly_sales', 0))
        sales_score = min(monthly_sales / 100_000, 1.0)  # Cap at 100K
        
        # Sector risk (0-1, lower is better)
        sector = data.get('sector', '').lower()
        sector_score = 1.0 - self.sector_risks.get(sector, self.sector_risks['default'])
        
        # Document completeness (0-1)
        docs_uploaded = len(data.get('ipfs_docs', []))
        doc_score = min(docs_uploaded / 5, 1.0)  # Expect at least 5 docs
        
        # Previous funding (0-1)
        prev_funding = float(data.get('previous_funding', 0))
        funding_score = min(prev_funding / 500_000, 1.0)  # Cap at 500K
        
        return {
            'revenue': revenue_score,
            'business_age': age_score,
            'monthly_sales': sales_score,
            'sector_risk': sector_score,
            'document_completeness': doc_score,
            'previous_funding': funding_score,
        }
    
    def _calculate_weighted_score(self, features: Dict) -> float:
        """Calculate final weighted score"""
        score = 0.0
        
        for feature, value in features.items():
            weight = self.weights.get(feature, 0.0)
            score += value * weight * 100
        
        # Add some randomness for realism (±5 points)
        # noise = np.random.uniform(-5, 5)
        # score += noise
        
        # Clamp to 0-100
        score = max(0.0, min(100.0, score))
        
        return round(score, 2)
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score >= 70:
            return 'Low'
        elif score >= 40:
            return 'Medium'
        else:
            return 'High'
    
    def _generate_explanation(self, features: Dict, final_score: float) -> Dict:
        """
        Generate explainability output showing feature importance.
        Similar to SHAP values but simpler for MVP.
        """
        
        # Calculate contribution of each feature to final score
        contributions = {}
        for feature, value in features.items():
            weight = self.weights.get(feature, 0.0)
            contribution = value * weight * 100
            contributions[feature] = {
                'normalized_value': round(value, 3),
                'weight': weight,
                'contribution_to_score': round(contribution, 2),
            }
        
        # Sort by contribution (descending)
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: x[1]['contribution_to_score'],
            reverse=True
        )
        
        return {
            'final_score': final_score,
            'features': dict(sorted_features),
            'top_strengths': [k for k, v in sorted_features[:2]],
            'top_weaknesses': [k for k, v in sorted_features[-2:]],
            'methodology': 'Weighted scoring based on financial health, business maturity, and sector risk',
        }
    
    def batch_score(self, startups: List[Dict]) -> List[Tuple[float, str, Dict]]:
        """
        Calculate scores for multiple startups in batch.
        Useful for batch processing and analytics.
        """
        results = []
        for startup in startups:
            result = self.calculate_score(startup)
            results.append(result)
        return results


class MLCreditScoringService(CreditScoringService):
    """
    ML-based credit scoring using scikit-learn.
    To be implemented when sufficient training data is available.
    
    Upgrade steps:
    1. Collect historical data (startups + outcomes)
    2. Train Random Forest or Gradient Boosting model
    3. Use SHAP for explainability
    4. Deploy model and switch to this service
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_path = settings.AI_MODEL_PATH
        # self._load_model()
    
    def _load_model(self):
        """Load trained ML model from disk"""
        import joblib
        try:
            data_scaler = joblib.load('data_scaler.pkl')
            credit_model = joblib.load('credit_model.pkl')
            
            # Get the 95 feature names the model was trained on
            MODEL_FEATURES = data_scaler.feature_names_in_
            print("AI models loaded successfully.")
            
        except Exception as e:
            print(f"CRITICAL ERROR: Could not load models: {e}")
            data_scaler = None
            credit_model = None
            MODEL_FEATURES = []

    
        pass
    
    def calculate_score_ml(self, startup_data: Dict) -> Tuple[float, str, Dict]:
    """
        Calculates the credit score from a dictionary of SME data.
        
        Args:
            sme_data: A dictionary where keys are the feature names.
                    The function will automatically align this with the 95 
                    required features, filling in 0 for any missing data.

        Returns:
            A list: [probability_of_bankruptcy, probability_of_not_bankruptcy]
    """
    if not credit_model or not data_scaler:
        print("Models are not loaded. Cannot predict.")
        # Return a default "undetermined" score
        return [0.5, 0.5] 
        
    try:
        # 1. Create a pandas Series aligned to the model's 95 features.
        # - It ensures all 95 features are present.
        # - It puts them in the correct order.
        # - .fillna(0) sets any data not provided by the user to 0.
        input_series = pd.Series(sme_data, index=MODEL_FEATURES).fillna(0)
        
        # 2. Convert the Series to a single-row DataFrame.
        input_df = input_series.to_frame().T
        
        # 3. Ensure all data is numeric (in case of errors).
        input_df = input_df.apply(pd.to_numeric)

        # 4. Scale the data using the loaded scaler.
        scaled_data = data_scaler.transform(input_df)
        
        # 5. Predict the probabilities.
        # The model's classes are [0, 1] (Not Bankrupt, Bankrupt).
        # predict_proba() returns [[prob_not_bankrupt, prob_bankrupt]]
        probabilities = credit_model.predict_proba(scaled_data)
        
        prediction = probabilities[0]
        
        prob_not_bankrupt = prediction[0]
        prob_bankrupt = prediction[1]
        
        # 6. Return in your requested format:
        # [percentage of bankruptcy, percentage of not bankruptcy]
        return [prob_bankrupt, prob_not_bankrupt]

    except Exception as e:
        print(f"Error during prediction: {e}")
        return [0.5, 0.5] # Return "undetermined" on error

        raise NotImplementedError("ML model not yet trained")


# Singleton instance
credit_scoring_service = CreditScoringService()
import joblib
import pandas as pd
import numpy as np

# --- 1. Load Models ---
# Load these once when your application starts.
try:
    data_scaler = joblib.load('data_scaler.pkl')
    credit_model = joblib.load('credit_model.pkl')
    
    # Get the 95 feature names the model was trained on
    MODEL_FEATURES = data_scaler.feature_names_in_
    print("AI models loaded successfully.")
    
except Exception as e:
    print(f"CRITICAL ERROR: Could not load models: {e}")
    data_scaler = None
    credit_model = None
    MODEL_FEATURES = []

# --- 2. The Prediction Function ---

def get_credit_score(sme_data: dict):
    