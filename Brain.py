import json
import os
import re
import requests
from bs4 import BeautifulSoup
from functools import lru_cache
from fuzzywuzzy import fuzz
import hashlib

class LocalBrain:
    """Enhanced local knowledge base with validation and Nepali support"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._load_db()
        
    def _load_db(self):
        """Robust database loading with validation"""
        try:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Problem DB not found at: {self.db_path}")
                
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Invalid DB format - expected list of problems")
                
            self.problems = data
            self._build_maps()
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in problem DB: {e}")
            
    def _build_maps(self):
        """Build alias maps for both English and Nepali"""
        self.alias_map = {}
        self.np_alias_map = {}
        
        for idx, problem in enumerate(self.problems):
            # English aliases
            for alias in problem.get("aliases", []):
                self.alias_map[alias.lower()] = idx
                
            # Nepali aliases
            for alias in problem.get("np_aliases", []):
                self.np_alias_map[alias.lower()] = idx

    @lru_cache(maxsize=1000)
    def match(self, query, lang="en", min_confidence=75):
        """Enhanced matching with language-specific optimization"""
        query = query.lower().strip()
        alias_map = self.np_alias_map if lang == "np" else self.alias_map
        
        # Phase 1: Exact match
        for word in re.findall(r'\w+', query):  # Better tokenization
            if word in alias_map:
                problem = self.problems[alias_map[word]]
                return problem.get(lang, problem.get("en"))
                
        # Phase 2: Fuzzy match
        best_match, best_score = None, 0
        search_space = self.np_alias_map if lang == "np" else self.alias_map
        
        for alias, idx in search_space.items():
            score = fuzz.token_set_ratio(query, alias)
            if score >= min_confidence and score > best_score:
                best_match = self.problems[idx].get(lang)
                best_score = score
                
        return best_match

    def add_solution(self, aliases, en_solution, np_solution=None):
        """Dynamically add new solutions"""
        new_problem = {
            "id": hashlib.md5(en_solution.encode()).hexdigest()[:8],
            "aliases": aliases,
            "en": en_solution,
            "np": np_solution or en_solution,
            "auto_fix": False,
            "learned": True  # Mark as dynamically learned
        }
        self.problems.append(new_problem)
        self._build_maps()
        self._save_db()
        
    def _save_db(self):
        """Save changes back to the database"""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.problems, f, ensure_ascii=False, indent=2)

class InternetBrain:
    """Enhanced internet search with multiple fallback engines"""
    
    def __init__(self, timeout=8):
        self.timeout = timeout
        self.search_engines = [
            {
                "name": "DuckDuckGo",
                "url": "https://html.duckduckgo.com/html/",
                "method": "POST"
            },
            {
                "name": "Google",
                "url": "https://www.google.com/search",
                "method": "GET"
            }
        ]
        
    def search(self, query, lang="en"):
        """Smart search with fallback and language support"""
        for engine in self.search_engines:
            try:
                results = self._try_engine(engine, query, lang)
                if results:
                    return results
            except Exception as e:
                continue
                
        return "❌ All search attempts failed. Please try again later."

    def _try_engine(self, engine, query, lang):
        """Try a specific search engine"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TechsewaAssistant/1.0',
            'Accept-Language': 'en-US,en;q=0.9' if lang == 'en' else 'ne-NP,ne;q=0.9'
        }
        
        params = {'q': query}
        if lang == 'np':
            params['q'] += " site:.np OR site:.com.np"
            
        if engine["method"] == "POST":
            response = requests.post(
                engine["url"],
                data=params,
                headers=headers,
                timeout=self.timeout
            )
        else:
            response = requests.get(
                engine["url"],
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
        return self._parse_results(response.text, engine["name"])

    def _parse_results(self, html, engine_name):
        """Parse results based on search engine"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        if engine_name == "DuckDuckGo":
            for result in soup.select('.result__body')[:3]:
                title = result.select_one('.result__a').get_text(strip=True)
                snippet = result.select_one('.result__snippet').get_text(strip=True)
                link = result.select_one('.result__a')['href']
                results.append(f"🔍 {title}\n📝 {snippet}\n🔗 {link}")
                
        elif engine_name == "Google":
            for result in soup.select('.g')[:3]:
                title = result.select_one('h3').get_text(strip=True)
                snippet = result.select_one('.IsZvec').get_text(strip=True) if result.select_one('.IsZvec') else ""
                link = result.select_one('a')['href']
                results.append(f"🔍 {title}\n📝 {snippet}\n🔗 {link}")
                
        return "\n\n".join(results) if results else None

class SmartBrain:
    """Intelligent controller with learning and diagnostics"""
    
    def __init__(self, problem_path, enable_internet=True):
        self.local = LocalBrain(problem_path)
        self.web = InternetBrain() if enable_internet else None
        self.enable_internet = enable_internet
        self.query_history = []
        self.learned_solutions = 0
        
    def solve(self, query, lang='en', min_conf=75):
        """Enhanced problem solving with context"""
        self._log_query(query, lang)
        
        # Try local knowledge base
        response = self._try_local_solve(query, lang, min_conf)
        if response:
            return response
            
        # Fallback to internet if enabled
        if self.enable_internet:
            internet_response = self.web.search(query, lang)
            return {
                "source": "internet",
                "answer": internet_response,
                "confidence": 0  # Unknown confidence for web results
            }
            
        return {
            "source": "none",
            "answer": "❌ No solution found in local knowledge base.",
            "confidence": 0
        }
        
    def _try_local_solve(self, query, lang, min_conf):
        """Attempt local solution with multiple strategies"""
        # First try exact match
        exact_match = self.local.match(query, lang, 100)
        if exact_match:
            return {
                "source": "local",
                "answer": exact_match,
                "confidence": 100
            }
            
        # Then try fuzzy match
        fuzzy_match = self.local.match(query, lang, min_conf)
        if fuzzy_match:
            return {
                "source": "local",
                "answer": fuzzy_match,
                "confidence": min_conf
            }
            
        return None
        
    def learn_solution(self, query, solution, lang='en'):
        """Learn new solutions from interactions"""
        np_solution = None
        if lang == 'en':
            # Simple translation placeholder - could integrate with translation API
            np_solution = solution.replace("restart", "पुन: सुरु गर्नुहोस्")
            
        self.local.add_solution(
            aliases=[query],
            en_solution=solution,
            np_solution=np_solution
        )
        self.learned_solutions += 1
        return True
        
    def _log_query(self, query, lang):
        """Maintain query history"""
        self.query_history.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "lang": lang
        })
        
    def get_stats(self):
        """Get usage statistics"""
        return {
            "total_problems": len(self.local.problems),
            "learned_solutions": self.learned_solutions,
            "query_history_size": len(self.query_history),
            "cache_size": self.local.match.cache_info().currsize
        }

# Example Usage
if __name__ == "__main__":
    brain = SmartBrain("D:/Techsewa/problems.json")
    
    # Solve a problem
    result = brain.solve("my internet is not working", lang="en")
    print(f"Result from {result['source']}:")
    print(result["answer"])
    
    # Learn a new solution
    brain.learn_solution(
        "zoom not working", 
        "Try updating Zoom or reinstalling the application."
    )
    
    # Get statistics
    print(brain.get_stats())