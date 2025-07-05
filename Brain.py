import json
import os
import re
import requests
from functools import lru_cache
from fuzzywuzzy import fuzz
import hashlib
from typing import Optional, Dict, List

class LocalBrain:
    """Enhanced local knowledge base with confidence threshold support"""
    
    def __init__(self, db_path: str, min_confidence: int = 75):
        self.min_confidence = min_confidence
        self.db_path = db_path
        self.problems = []
        self._load_db()
        self._build_maps()

    def _load_db(self):
        """Load and validate problem database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Problem DB not found at: {self.db_path}")
            
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            raise ValueError("Problem DB should contain a list of problems")
        self.problems = data

    def _build_maps(self):
        """Create efficient alias lookup structures"""
        self.alias_map = {}  # English aliases
        self.np_alias_map = {}  # Nepali aliases
        
        for idx, problem in enumerate(self.problems):
            for alias in problem.get("aliases", []):
                self.alias_map[alias.lower()] = idx
            for alias in problem.get("np_aliases", []):
                self.np_alias_map[alias.lower()] = idx

    @lru_cache(maxsize=500)
    def match(self, query: str, lang: str = "en", min_confidence: Optional[int] = None) -> Optional[str]:
        """
        Find best matching solution
        Args:
            query: User's problem description
            lang: 'en' or 'np'
            min_confidence: Optional override for instance default
        Returns:
            Localized solution or None
        """
        query = query.lower().strip()
        threshold = min_confidence or self.min_confidence
        alias_map = self.np_alias_map if lang == "np" else self.alias_map
        
        # Phase 1: Exact match
        for token in re.findall(r'\w+', query):
            if token in alias_map:
                return self.problems[alias_map[token]].get(lang)
        
        # Phase 2: Fuzzy match
        best_match, best_score = None, 0
        for alias, idx in alias_map.items():
            score = fuzz.token_set_ratio(query, alias)
            if score >= threshold and score > best_score:
                best_match = self.problems[idx].get(lang)
                best_score = score
                
        return best_match

class InternetBrain:
    """Fallback internet search with error handling"""
    
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.search_url = "https://search.techsewa.com/api"  # Example endpoint
        
    def search(self, query: str, lang: str = "en") -> str:
        """Safe search with timeout"""
        try:
            # Mock implementation - replace with actual API call
            return (
                f"🔍 Try these solutions from Techsewa Knowledge Base:\n"
                f"1. Restart your device\n"
                f"2. Check network connections\n"
                f"3. Visit support.techsewa.com/{lang}/{hashlib.md5(query.encode()).hexdigest()[:6]}"
            )
        except Exception:
            return "⚠️ Internet solutions currently unavailable"

class SmartBrain:
    """Intelligent problem solver with local+web fallback"""
    
    def __init__(self, problem_path: str, enable_internet: bool = True, min_confidence: int = 75):
        self.local = LocalBrain(problem_path, min_confidence)
        self.web = InternetBrain() if enable_internet else None
        self.enable_internet = enable_internet
        
    def solve(self, query: str, lang: str = "en", min_conf: Optional[int] = None) -> Dict[str, str]:
        """
        Solve problems with confidence threshold
        Returns:
            {'source': 'local'|'internet'|'none', 'answer': str}
        """
        # Try local knowledge first
        local_solution = self.local.match(query, lang, min_conf or self.local.min_confidence)
        if local_solution:
            return {"source": "local", "answer": local_solution}
            
        # Fallback to internet
        if self.enable_internet:
            return {
                "source": "internet",
                "answer": self.web.search(query, lang)
            }
            
        return {"source": "none", "answer": "No solutions available"}