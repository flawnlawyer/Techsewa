# brain.py - Ultimate AI Assistant for TechSewa (Fixed Version)
import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from functools import lru_cache
from typing import Dict, List, Optional

# ==================== INITIAL SETUP ====================
DEFAULT_PROBLEMS = [
    {
        "id": "restart-windows",
        "aliases": ["how to restart windows", "reboot pc", "restart computer", restart],
        "np_aliases": ["windows restart गर्ने तरिका", "कम्प्युटर रिस्टार्ट गर्ने तरिका"],
        "en": "Press Win + X, then select 'Shut down or sign out' > 'Restart'",
        "np": "Win + X थिच्नुहोस्, त्यसपछि 'Shut down or sign out' > 'Restart' चयन गर्नुहोस्",
        "auto_fix": False
    },
    {
        "id": "wifi-password",
        "aliases": ["find wifi password", "view wifi password windows"],
        "np_aliases": ["wifi पासवर्ड हेर्ने तरिका"],
        "en": "1. Open Command Prompt as admin\n2. Type: netsh wlan show profile name=NETWORK key=clear\n3. Find the 'Key Content' field",
        "np": "1. Command Prompt प्रशासकको रूपमा खोल्नुहोस्\n2. टाइप गर्नुहोस्: netsh wlan show profile name=NETWORK key=clear\n3. 'Key Content' फिल्ड हेर्नुहोस्",
        "auto_fix": False
    }
]

# ==================== CORE BRAIN CLASSES ====================
class LocalBrain:
    def __init__(self, db_path: str = "problems.json"):
        self.db_path = db_path
        self._ensure_knowledge_base()
        with open(db_path, "r", encoding="utf-8") as f:
            self.problems = json.load(f)  # Now directly loading the list
        self._build_maps()
    
    def _ensure_knowledge_base(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_PROBLEMS, f, indent=2, ensure_ascii=False)
    
    def _build_maps(self):
        self.en_map = {}
        self.np_map = {}
        for idx, problem in enumerate(self.problems):
            for alias in problem.get("aliases", []):
                self.en_map[alias.lower()] = idx
            for alias in problem.get("np_aliases", []):
                self.np_map[alias.lower()] = idx

    @lru_cache(maxsize=500)
    def match(self, query: str, lang: str = "en", min_conf: int = 65) -> Optional[str]:
        query = query.lower().strip()
        amap = self.np_map if lang == "np" else self.en_map
        
        # Exact match
        for token in re.findall(r'\w+', query):
            if token in amap:
                return self.problems[amap[token]].get(lang)
        
        # Fuzzy match
        best_match, best_score = None, 0
        for alias, idx in amap.items():
            score = fuzz.token_set_ratio(query, alias)
            if score > best_score and score >= min_conf:
                best_match = self.problems[idx].get(lang)
                best_score = score
        return best_match

class InternetBrain:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.ddg_url = "https://html.duckduckgo.com/html/"
    
    def search(self, query: str, lang: str = "en") -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "ne" if lang == "np" else "en"
            }
            res = requests.post(
                self.ddg_url,
                data={"q": query},
                headers=headers,
                timeout=self.timeout
            )
            soup = BeautifulSoup(res.text, "html.parser")
            results = []
            
            for result in soup.select(".result__body")[:3]:
                title = result.select_one(".result__a").get_text(strip=True)
                snippet = result.select_one(".result__snippet").get_text(" ", strip=True)
                link = result.select_one(".result__a")["href"]
                results.append(f"🔍 {title}\n📝 {snippet}\n🔗 {link}")
            
            return "\n\n".join(results) if results else "No results found."
        except Exception as e:
            return f"⚠️ Search failed: {str(e)}"

class FreeAI:
    @staticmethod
    def ask(query: str) -> Optional[str]:
        try:
            res = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": 0.7,
                    "max_tokens": 150
                },
                headers={"Accept": "application/json"},
                timeout=10
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None

# ==================== MAIN BRAIN ====================
class SmartBrain:
    def __init__(self, db_path: str = "problems.json", enable_internet: bool = True):
        self.local = LocalBrain(db_path)
        self.internet = InternetBrain() if enable_internet else None
        self.enable_internet = enable_internet
        self.history = []
        
        self.SUPPORT_MSG = """
📌 Need more help? Contact:
📍 Learner Mission & Training Center
🗺️ Thuphandanda, Dadeldhura
📞 9867315931 | 📧 learnermission@gmail.com
"""

    def solve(self, query: str, lang: str = "en") -> Dict[str, str]:
        self._remember(query, lang)
        
        # 1. Local knowledge
        if answer := self.local.match(query, lang):
            return self._format("local", answer)
        
        # 2. Free AI
        if answer := FreeAI.ask(query):
            return self._format("ai", answer)
        
        # 3. Web search
        if self.enable_internet and (answer := self.internet.search(query, lang)):
            return self._format("internet", answer)
        
        return self._format("none", "Sorry, I couldn't find a solution.")

    def _format(self, source: str, answer: str) -> Dict[str, str]:
        return {
            "source": source,
            "answer": f"{answer}\n\n{self.SUPPORT_MSG.strip()}"
        }

    def _remember(self, query: str, lang: str):
        self.history.append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "lang": lang
        })
        self.history = self.history[-100:]  # Keep last 100 entries

# ==================== USAGE EXAMPLE ====================
if __name__ == "__main__":
    print("Initializing TechSewa Brain...")
    brain = SmartBrain()  # Will auto-create problems.json if needed
    
    while True:
        print("\n" + "="*50)
        query = input("Ask a tech question (or 'quit'): ").strip()
        if query.lower() in ('quit', 'exit'):
            break
            
        lang = "np" if any(ord(c) > 127 for c in query) else "en"
        result = brain.solve(query, lang)
        
        print(f"\n🔧 Source: {result['source'].upper()}")
        print(result["answer"])