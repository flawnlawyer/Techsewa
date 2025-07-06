# Brain.py  –  SmartBrain Ultra v2  (UI‑ready)
# -------------------------------------------
# • Local fuzzy + exact alias matching
# • Optional semantic search (sentence‑transformers)  ➜ auto‑disabled if package missing
# • Google/DuckDuckGo scrape fallback
# • .teach() for interactive learning
# • stats(), history, enable_internet attribute

from __future__ import annotations
import os, json, re, time, hashlib, requests
from typing import Optional, Dict, List
from functools import lru_cache
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

# ───────── optional semantic search ─────────
try:
    from sentence_transformers import SentenceTransformer, util
    _SEMANTIC_OK = True
except Exception:
    _SEMANTIC_OK = False
# -------------------------------------------


# =============== LocalBrain =================
class LocalBrain:
    """Local knowledge‑base with fuzzy matching."""
    def __init__(self, db_path: str, min_confidence: int = 75):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Problem DB not found: {db_path}")
        with open(db_path, "r", encoding="utf-8") as fp:
            self.problems: List[Dict] = json.load(fp)

        self.db_path = db_path
        self.min_conf = min_confidence
        self.en_map, self.np_map = {}, {}
        self._build_maps()

    def _build_maps(self):
        self.en_map.clear(); self.np_map.clear()
        for idx, p in enumerate(self.problems):
            for a in p.get("aliases", []):
                self.en_map[a.lower()] = idx
            for a in p.get("np_aliases", []):
                self.np_map[a.lower()] = idx

    # ------ look‑up ----------
    @lru_cache(maxsize=500)
    def match(self, query: str, lang: str = "en", min_conf: int | None = None) -> Optional[str]:
        if not query: return None
        q = query.lower().strip()
        amap = self.np_map if lang == "np" else self.en_map
        threshold = min_conf or self.min_conf

        # exact token match
        for tok in re.findall(r'\w+', q):
            if tok in amap:
                return self.problems[amap[tok]].get(lang, self.problems[amap[tok]].get("en"))

        # fuzzy
        best, score = None, 0
        for alias, idx in amap.items():
            s = fuzz.token_set_ratio(q, alias)
            if s > score and s >= threshold:
                best, score = self.problems[idx].get(lang, self.problems[idx].get("en")), s
        return best

    # ------ teach ----------
    def learn(self, query:str, en_sol:str, np_sol:str|None=None):
        pid = hashlib.md5(query.encode()).hexdigest()[:8]
        self.problems.append({
            "id": pid,
            "aliases": [query],
            "np_aliases": [],
            "en": en_sol,
            "np": np_sol or en_sol,
            "auto_fix": False,
            "learned": True
        })
        with open(self.db_path,"w",encoding="utf-8") as fp:
            json.dump(self.problems, fp, indent=2, ensure_ascii=False)
        self._build_maps()

# =========== SemanticBrain (optional) ===========
class SemanticBrain:
    def __init__(self, problems: List[Dict]):
        self.enabled = _SEMANTIC_OK
        if not self.enabled: return
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.sentences = [p.get("en","") for p in problems]
        self.embeds = self.model.encode(self.sentences, convert_to_tensor=True)

    def search(self, query:str, problems:List[Dict], lang:str="en", th=0.60) -> Optional[str]:
        if not self.enabled: return None
        qv = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(qv, self.embeds)[0]
        idx = int(scores.argmax())
        if float(scores[idx]) >= th:
            return problems[idx].get(lang, problems[idx].get("en"))
        return None

# =========== InternetBrain =====================
class InternetBrain:
    def __init__(self, timeout:int=8):
        self.timeout = timeout
        self.ddg_url = "https://html.duckduckgo.com/html/"

    def search(self, query:str, lang:str="en") -> str:
        try:
            hdr = {"User-Agent":"Mozilla/5.0","Accept-Language":"ne" if lang=="np" else "en"}
            res = requests.post(self.ddg_url, data={"q":query}, headers=hdr, timeout=self.timeout)
            soup = BeautifulSoup(res.text,"html.parser")
            blocks = soup.select(".result__body")[:3]
            if not blocks:
                return "🔍 No relevant results online."
            out=[]
            for b in blocks:
                title = b.select_one(".result__a").get_text(" ",strip=True)
                snip  = b.select_one(".result__snippet").get_text(" ",strip=True)
                link  = b.select_one(".result__a")["href"]
                out.append(f"🔎 {title}\n📝 {snip}\n🔗 {link}")
            return "\n\n".join(out)
        except Exception as e:
            return f"⚠️ Web lookup failed: {e}"

# =========== SmartBrain ========================
class SmartBrain:
    def __init__(self, db_path:str, enable_internet:bool=True, min_confidence:int=75):
        self.local   = LocalBrain(db_path, min_confidence)
        self.semantic= SemanticBrain(self.local.problems)
        self.internet= InternetBrain() if enable_internet else None
        self.enable_internet = enable_internet
        self.history: List[Dict] = []

    # ------- public API ---------
    def solve(self, query:str, lang="en", min_conf=75) -> Dict[str,str]:
        self._remember(query,lang)

        # 1) local
        ans = self.local.match(query, lang, min_conf)
        if ans:
            return {"source":"local","answer":ans}

        # 2) semantic
        sem = self.semantic.search(query, self.local.problems, lang) if self.semantic.enabled else None
        if sem:
            return {"source":"semantic","answer":sem}

        # 3) web
        if self.enable_internet:
            return {"source":"internet","answer":self.internet.search(query, lang)}

        return {"source":"none","answer":"❌ No solution found."}

    # UI CALLS -------------------
    def teach(self, query:str, en_sol:str, np_sol:str|None=None):
        """Alias called by GUI Teach dialog."""
        self.local.learn(query, en_sol, np_sol)

    # stats used by UI
    def stats(self):
        return {
            "total_problems": len(self.local.problems),
            "cached_matches": self.local.match.cache_info().currsize,
            "semantic": self.semantic.enabled,
            "internet": self.enable_internet
        }

    # -------- internals ----------
    def _remember(self,q,lang):
        self.history.append({"ts":time.strftime("%H-%m-%d %H:%M:%S"),"q":q,"lang":lang})
        self.history = self.history[-20:]
