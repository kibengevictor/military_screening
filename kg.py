"""
Minimal importable Knowledge Graph implementation used as a target for safe unpickling
and as a reasonable default if the original pickled KG cannot be loaded.

This class implements a small ruleset and a `recommend_roles` method which the app
expects. It is intentionally small and safe to import during unpickling.
"""
from typing import Dict, Any


class MilitaryScreeningKG:
    """Simple, importable knowledge-graph replacement.

    The original pickled KG may reference this class from __main__. When unpickling
    under gunicorn the __main__ module differs which causes errors. Providing this
    importable class and mapping __main__.MilitaryScreeningKG -> kg.MilitaryScreeningKG
    allows the pickle to be loaded safely (if compatible).
    """

    def __init__(self, rules: Dict[str, Any] = None):
        # Default rules if none provided
        self.rules = rules or {
            'high_confidence': ['Infantry', 'Special Forces', 'Combat Engineer'],
            'medium_confidence': ['Military Police', 'Logistics', 'Signals'],
            'low_confidence': ['Medical Evaluation Required']
        }

    def recommend_roles(self, biomarkers: Dict[str, float]) -> Dict[str, Any]:
        """Return recommended roles and detected risks based on simple thresholds.

        biomarkers: dict with keys like 'movement_quality', 'fatigue_index', etc.
        """
        mq = biomarkers.get('movement_quality', 0.0)
        recommended = []
        detected_risks = []

        if mq > 0.8:
            recommended = self.rules['high_confidence']
        elif mq > 0.6:
            recommended = self.rules['medium_confidence']
        else:
            recommended = self.rules['low_confidence']
            detected_risks.append('Low movement quality')

        return {
            'recommended_roles': recommended,
            'detected_risks': detected_risks
        }
