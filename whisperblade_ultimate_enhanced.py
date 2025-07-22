#!/usr/bin/env python3
"""
WhisperBlade Ultimate Enhanced - The Greatest AI Brain
Version 3.0 - Revolutionary AI architecture with advanced reasoning, multi-modal processing, and unlimited knowledge access
Designed to surpass GPT, Google, and DeepSeek with innovative approaches
"""

import os
import json
import re
import time
import hashlib
import asyncio
import aiohttp
import sqlite3
import threading
import queue
import math
import random
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
from functools import lru_cache, wraps
from contextlib import asynccontextmanager
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus, urljoin, urlparse
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
import heapq
import networkx as nx

# Enhanced imports with advanced fallback handling
try:
    import psutil
    HW_MONITOR_OK = True
except ImportError:
    HW_MONITOR_OK = False
    print("⚠️  psutil not available - hardware monitoring disabled")

try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    ADVANCED_AI_OK = True
except ImportError:
    ADVANCED_AI_OK = False
    print("⚠️  Advanced AI libraries not available - using fallback AI")

try:
    import speech_recognition as sr
    import pyttsx3
    SPEECH_OK = True
except ImportError:
    SPEECH_OK = False
    print("⚠️  Speech libraries not available - voice interface disabled")

try:
    import PyPDF2
    import docx
    import openpyxl
    from PIL import Image
    import pytesseract
    DOCUMENT_OK = True
except ImportError:
    DOCUMENT_OK = False
    print("⚠️  Document libraries not available - document processing disabled")

try:
    import requests
    from bs4 import BeautifulSoup
    import feedparser
    WEB_OK = True
except ImportError:
    WEB_OK = False
    print("⚠️  Web libraries not available - web search disabled")

try:
    from fuzzywuzzy import fuzz, process
    import difflib
    FUZZY_OK = True
except ImportError:
    FUZZY_OK = False
    print("⚠️  Fuzzy matching not available - using basic matching")

try:
    import spacy
    import nltk
    from textblob import TextBlob
    NLP_OK = True
except ImportError:
    NLP_OK = False
    print("⚠️  NLP libraries not available - using basic text processing")

# ==================== ADVANCED CONFIGURATION ====================
@dataclass
class AdvancedConfig:
    """Advanced configuration with AI-specific settings"""
    # Database settings
    DB_PATH: str = "whisperblade_ultimate.db"
    VECTOR_DB_PATH: str = "vectors.db"
    CACHE_SIZE: int = 10000
    
    # AI Performance settings
    MAX_RESPONSE_TIME: float = 2.0
    SEMANTIC_THRESHOLD: float = 0.6
    FUZZY_THRESHOLD: int = 65
    REASONING_DEPTH: int = 5
    PARALLEL_PROCESSING: bool = True
    MAX_WORKERS: int = 8
    
    # Advanced AI features
    ENABLE_REASONING: bool = True
    ENABLE_LEARNING: bool = True
    ENABLE_CREATIVITY: bool = True
    ENABLE_MULTI_MODAL: bool = True
    ENABLE_CHAIN_OF_THOUGHT: bool = True
    ENABLE_SELF_REFLECTION: bool = True
    
    # Search and knowledge
    MAX_SEARCH_RESULTS: int = 20
    KNOWLEDGE_GRAPH_DEPTH: int = 3
    CONTEXT_WINDOW_SIZE: int = 4096
    
    # Logging and monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_PERFORMANCE_MONITORING: bool = True
    ENABLE_LEARNING_ANALYTICS: bool = True
    
    # API Configuration
    FREE_APIS: Dict[str, str] = field(default_factory=lambda: {
        'duckduckgo': 'https://api.duckduckgo.com/',
        'wikipedia': 'https://en.wikipedia.org/api/rest_v1/',
        'openai_free': 'https://api.openai.com/v1/',  # When available
        'huggingface': 'https://api-inference.huggingface.co/',
        'github_copilot': 'https://api.github.com/',
        'arxiv': 'http://export.arxiv.org/api/',
        'reddit': 'https://www.reddit.com/r/',
        'stackoverflow': 'https://api.stackexchange.com/2.3/',
        'news_api': 'https://newsapi.org/v2/',
        'wolfram_alpha': 'http://api.wolframalpha.com/v2/',
        'google_scholar': 'https://scholar.google.com/',
        'semantic_scholar': 'https://api.semanticscholar.org/',
        'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
        'crossref': 'https://api.crossref.org/',
        'openweather': 'https://api.openweathermap.org/data/2.5/',
        'free_gpt': 'https://api.freegpt.one/v1/',
        'you_search': 'https://api.you.com/search',
        'bing_free': 'https://www.bing.com/search',
        'yandex': 'https://yandex.com/search/',
        'baidu': 'https://www.baidu.com/s',
    })
    
    # Contact information
    SUPPORT_CONTACT: str = """
📌 TechSewa Ultimate AI Support:
🏢 Advanced AI Research Center - Learner Mission & Training
🗺️ Thuphandanda, Dadeldhura, Nepal
📞 +977-9867315931
📧 ai.support@learnermission.com
🌐 https://whisperblade-ai.com
⏰ 24/7 AI-Powered Support Available
🤖 Powered by WhisperBlade Ultimate AI v3.0
"""

# ==================== ADVANCED DATA MODELS ====================
@dataclass
class AIThought:
    """Represents a single thought in the AI reasoning process"""
    id: str
    content: str
    confidence: float
    reasoning_step: int
    dependencies: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeNode:
    """Advanced knowledge node with relationships"""
    id: str
    content_en: str
    content_np: str
    aliases_en: List[str] = field(default_factory=list)
    aliases_np: List[str] = field(default_factory=list)
    category: str = "general"
    priority: int = 1
    error_codes: List[str] = field(default_factory=list)
    relationships: Dict[str, float] = field(default_factory=dict)  # node_id -> strength
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    success_rate: float = 1.0
    learning_weight: float = 1.0
    tags: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    verification_status: str = "unverified"  # verified, unverified, disputed

@dataclass
class AIResponse:
    """Enhanced AI response with reasoning chain"""
    answer: str
    source: str
    confidence: float
    response_time: float
    lang: str
    reasoning_chain: List[AIThought] = field(default_factory=list)
    knowledge_nodes_used: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    alternative_answers: List[str] = field(default_factory=list)
    certainty_level: str = "medium"  # high, medium, low, uncertain
    creativity_score: float = 0.0
    learning_opportunity: bool = False
    follow_up_questions: List[str] = field(default_factory=list)
    context_used: Dict[str, Any] = field(default_factory=dict)
    api_sources: List[str] = field(default_factory=list)

@dataclass
class SystemMetrics:
    """Advanced system performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_usage: float = 0.0
    network_latency: float = 0.0
    ai_processing_load: float = 0.0
    knowledge_base_size: int = 0
    active_reasoning_threads: int = 0
    cache_hit_rate: float = 0.0
    learning_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

# ==================== ADVANCED REASONING ENGINE ====================
class AdvancedReasoningEngine:
    """Revolutionary AI reasoning engine with multi-step thinking"""
    
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.thought_graph = nx.DiGraph()
        self.reasoning_cache = {}
        self.learning_memory = deque(maxlen=1000)
        self.creativity_engine = CreativityEngine()
        self.logic_validator = LogicValidator()
        
    async def reason_about(self, query: str, context: Dict[str, Any]) -> List[AIThought]:
        """Advanced multi-step reasoning process"""
        reasoning_chain = []
        
        # Step 1: Query Analysis and Decomposition
        analysis_thought = await self._analyze_query(query, context)
        reasoning_chain.append(analysis_thought)
        
        # Step 2: Knowledge Retrieval and Synthesis
        knowledge_thoughts = await self._gather_knowledge(query, analysis_thought)
        reasoning_chain.extend(knowledge_thoughts)
        
        # Step 3: Logical Reasoning and Inference
        inference_thoughts = await self._perform_inference(reasoning_chain, context)
        reasoning_chain.extend(inference_thoughts)
        
        # Step 4: Creative Problem Solving (if needed)
        if self.config.ENABLE_CREATIVITY:
            creative_thoughts = await self._apply_creativity(query, reasoning_chain)
            reasoning_chain.extend(creative_thoughts)
        
        # Step 5: Self-Reflection and Validation
        if self.config.ENABLE_SELF_REFLECTION:
            reflection_thought = await self._self_reflect(reasoning_chain)
            reasoning_chain.append(reflection_thought)
        
        return reasoning_chain
    
    async def _analyze_query(self, query: str, context: Dict[str, Any]) -> AIThought:
        """Analyze and decompose the query"""
        analysis = {
            'query_type': self._classify_query_type(query),
            'complexity': self._assess_complexity(query),
            'key_concepts': self._extract_concepts(query),
            'intent': self._detect_intent(query),
            'emotional_tone': self._analyze_emotion(query),
            'urgency_level': self._assess_urgency(query)
        }
        
        return AIThought(
            id=f"analysis_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            content=f"Query analysis: {json.dumps(analysis, indent=2)}",
            confidence=0.9,
            reasoning_step=1,
            metadata=analysis
        )
    
    async def _gather_knowledge(self, query: str, analysis: AIThought) -> List[AIThought]:
        """Gather relevant knowledge from multiple sources"""
        knowledge_thoughts = []
        
        # Parallel knowledge gathering
        tasks = [
            self._search_internal_knowledge(query, analysis),
            self._search_web_knowledge(query, analysis),
            self._search_contextual_knowledge(query, analysis),
            self._search_analogical_knowledge(query, analysis)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                knowledge_thoughts.extend(result)
        
        return knowledge_thoughts
    
    async def _perform_inference(self, reasoning_chain: List[AIThought], context: Dict[str, Any]) -> List[AIThought]:
        """Perform logical inference and deduction"""
        inference_thoughts = []
        
        # Collect all available facts
        facts = []
        for thought in reasoning_chain:
            if 'facts' in thought.metadata:
                facts.extend(thought.metadata['facts'])
        
        # Apply different reasoning strategies
        strategies = [
            self._deductive_reasoning,
            self._inductive_reasoning,
            self._abductive_reasoning,
            self._analogical_reasoning
        ]
        
        for strategy in strategies:
            try:
                inference = await strategy(facts, context)
                if inference:
                    inference_thoughts.append(inference)
            except Exception as e:
                logging.error(f"Reasoning strategy failed: {e}")
        
        return inference_thoughts
    
    async def _apply_creativity(self, query: str, reasoning_chain: List[AIThought]) -> List[AIThought]:
        """Apply creative problem-solving techniques"""
        creative_thoughts = []
        
        # Different creativity techniques
        techniques = [
            self.creativity_engine.lateral_thinking,
            self.creativity_engine.analogical_thinking,
            self.creativity_engine.combinatorial_creativity,
            self.creativity_engine.constraint_relaxation
        ]
        
        for technique in techniques:
            try:
                creative_thought = await technique(query, reasoning_chain)
                if creative_thought:
                    creative_thoughts.append(creative_thought)
            except Exception as e:
                logging.error(f"Creative technique failed: {e}")
        
        return creative_thoughts
    
    async def _self_reflect(self, reasoning_chain: List[AIThought]) -> AIThought:
        """Self-reflection on the reasoning process"""
        reflection_analysis = {
            'reasoning_quality': self._assess_reasoning_quality(reasoning_chain),
            'confidence_consistency': self._check_confidence_consistency(reasoning_chain),
            'logical_coherence': self._validate_logical_coherence(reasoning_chain),
            'completeness': self._assess_completeness(reasoning_chain),
            'potential_biases': self._detect_biases(reasoning_chain),
            'improvement_suggestions': self._suggest_improvements(reasoning_chain)
        }
        
        overall_confidence = statistics.mean([t.confidence for t in reasoning_chain])
        
        return AIThought(
            id=f"reflection_{int(time.time())}",
            content=f"Self-reflection: {json.dumps(reflection_analysis, indent=2)}",
            confidence=overall_confidence,
            reasoning_step=len(reasoning_chain) + 1,
            metadata=reflection_analysis
        )
    
    # Helper methods for reasoning
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        patterns = {
            'factual': r'\b(what|when|where|who|which)\b',
            'procedural': r'\b(how|steps|process|procedure)\b',
            'causal': r'\b(why|because|cause|reason)\b',
            'comparative': r'\b(better|worse|compare|vs|versus)\b',
            'troubleshooting': r'\b(problem|issue|error|fix|solve)\b',
            'creative': r'\b(create|design|imagine|invent)\b'
        }
        
        for query_type, pattern in patterns.items():
            if re.search(pattern, query.lower()):
                return query_type
        
        return 'general'
    
    def _assess_complexity(self, query: str) -> float:
        """Assess query complexity (0-1 scale)"""
        factors = {
            'length': min(len(query.split()) / 20, 1),
            'technical_terms': len(re.findall(r'\b[A-Z]{2,}\b', query)) / 10,
            'question_words': len(re.findall(r'\b(what|when|where|who|why|how)\b', query.lower())) / 5,
            'complexity_indicators': len(re.findall(r'\b(complex|complicated|advanced|sophisticated)\b', query.lower())) / 3
        }
        
        return min(sum(factors.values()) / len(factors), 1.0)
    
    def _extract_concepts(self, query: str) -> List[str]:
        """Extract key concepts from query"""
        # Simple concept extraction - can be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        # Filter out common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why', 'who'}
        concepts = [word for word in words if word not in stop_words]
        return list(set(concepts))
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent"""
        intent_patterns = {
            'information_seeking': r'\b(tell me|explain|what is|information about)\b',
            'problem_solving': r'\b(fix|solve|repair|troubleshoot|help)\b',
            'learning': r'\b(learn|understand|teach|show)\b',
            'comparison': r'\b(compare|difference|better|vs)\b',
            'recommendation': r'\b(recommend|suggest|best|should)\b'
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, query.lower()):
                return intent
        
        return 'general_inquiry'
    
    def _analyze_emotion(self, query: str) -> str:
        """Analyze emotional tone of query"""
        emotion_indicators = {
            'urgent': r'\b(urgent|emergency|immediately|asap|quickly)\b',
            'frustrated': r'\b(frustrated|annoying|hate|terrible)\b',
            'curious': r'\b(curious|wondering|interested)\b',
            'confused': r'\b(confused|don\'t understand|unclear)\b',
            'neutral': r'.*'  # Default
        }
        
        for emotion, pattern in emotion_indicators.items():
            if re.search(pattern, query.lower()):
                return emotion
        
        return 'neutral'
    
    def _assess_urgency(self, query: str) -> int:
        """Assess urgency level (1-5 scale)"""
        urgency_keywords = {
            5: ['emergency', 'critical', 'urgent', 'asap', 'immediately'],
            4: ['important', 'quickly', 'soon', 'priority'],
            3: ['help', 'problem', 'issue'],
            2: ['question', 'wondering'],
            1: ['general', 'information']
        }
        
        query_lower = query.lower()
        for level, keywords in urgency_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return level
        
        return 2  # Default medium urgency

# ==================== CREATIVITY ENGINE ====================
class CreativityEngine:
    """Advanced creativity engine for innovative problem solving"""
    
    def __init__(self):
        self.creative_techniques = [
            'lateral_thinking',
            'analogical_thinking',
            'combinatorial_creativity',
            'constraint_relaxation',
            'random_stimulation',
            'morphological_analysis'
        ]
    
    async def lateral_thinking(self, query: str, reasoning_chain: List[AIThought]) -> Optional[AIThought]:
        """Apply lateral thinking techniques"""
        # Generate alternative perspectives
        perspectives = [
            "What if we approach this from the opposite direction?",
            "What would happen if we removed the main constraint?",
            "How would a child solve this problem?",
            "What if we combined this with something completely unrelated?"
        ]
        
        creative_ideas = []
        for perspective in perspectives:
            # Generate ideas based on perspective
            idea = f"Lateral thinking perspective: {perspective} Applied to: {query}"
            creative_ideas.append(idea)
        
        return AIThought(
            id=f"lateral_{int(time.time())}",
            content=f"Lateral thinking generated {len(creative_ideas)} alternative approaches",
            confidence=0.7,
            reasoning_step=len(reasoning_chain) + 1,
            metadata={'creative_ideas': creative_ideas, 'technique': 'lateral_thinking'}
        )
    
    async def analogical_thinking(self, query: str, reasoning_chain: List[AIThought]) -> Optional[AIThought]:
        """Apply analogical thinking"""
        # Find analogies from different domains
        domains = ['nature', 'technology', 'sports', 'cooking', 'music', 'architecture']
        analogies = []
        
        for domain in domains:
            analogy = f"In {domain}, a similar problem might be solved by..."
            analogies.append(analogy)
        
        return AIThought(
            id=f"analogical_{int(time.time())}",
            content=f"Analogical thinking found {len(analogies)} potential analogies",
            confidence=0.6,
            reasoning_step=len(reasoning_chain) + 1,
            metadata={'analogies': analogies, 'technique': 'analogical_thinking'}
        )
    
    async def combinatorial_creativity(self, query: str, reasoning_chain: List[AIThought]) -> Optional[AIThought]:
        """Combine existing ideas in novel ways"""
        existing_ideas = []
        for thought in reasoning_chain:
            if 'ideas' in thought.metadata:
                existing_ideas.extend(thought.metadata['ideas'])
        
        combinations = []
        for i in range(min(len(existing_ideas), 5)):
            for j in range(i+1, min(len(existing_ideas), 5)):
                combination = f"Combine: {existing_ideas[i]} + {existing_ideas[j]}"
                combinations.append(combination)
        
        return AIThought(
            id=f"combinatorial_{int(time.time())}",
            content=f"Combinatorial creativity generated {len(combinations)} novel combinations",
            confidence=0.65,
            reasoning_step=len(reasoning_chain) + 1,
            metadata={'combinations': combinations, 'technique': 'combinatorial_creativity'}
        )
    
    async def constraint_relaxation(self, query: str, reasoning_chain: List[AIThought]) -> Optional[AIThought]:
        """Relax constraints to find creative solutions"""
        relaxation_ideas = [
            "What if budget was unlimited?",
            "What if time was not a factor?",
            "What if we could use any technology?",
            "What if physical laws didn't apply?",
            "What if we had unlimited resources?"
        ]
        
        return AIThought(
            id=f"constraint_relaxation_{int(time.time())}",
            content=f"Constraint relaxation opened {len(relaxation_ideas)} new possibilities",
            confidence=0.6,
            reasoning_step=len(reasoning_chain) + 1,
            metadata={'relaxation_ideas': relaxation_ideas, 'technique': 'constraint_relaxation'}
        )

# ==================== LOGIC VALIDATOR ====================
class LogicValidator:
    """Advanced logic validation and consistency checking"""
    
    def __init__(self):
        self.logical_rules = self._initialize_logical_rules()
    
    def _initialize_logical_rules(self) -> Dict[str, Callable]:
        """Initialize logical validation rules"""
        return {
            'consistency': self._check_consistency,
            'completeness': self._check_completeness,
            'soundness': self._check_soundness,
            'relevance': self._check_relevance,
            'coherence': self._check_coherence
        }
    
    def validate_reasoning(self, reasoning_chain: List[AIThought]) -> Dict[str, float]:
        """Validate the logical consistency of reasoning chain"""
        validation_results = {}
        
        for rule_name, rule_func in self.logical_rules.items():
            try:
                score = rule_func(reasoning_chain)
                validation_results[rule_name] = score
            except Exception as e:
                logging.error(f"Logic validation rule {rule_name} failed: {e}")
                validation_results[rule_name] = 0.5  # Neutral score
        
        return validation_results
    
    def _check_consistency(self, reasoning_chain: List[AIThought]) -> float:
        """Check for logical consistency"""
        # Simple consistency check - look for contradictions
        statements = [thought.content for thought in reasoning_chain]
        contradiction_indicators = ['not', 'never', 'impossible', 'contradicts']
        
        contradictions = 0
        for i, statement in enumerate(statements):
            for j, other_statement in enumerate(statements[i+1:], i+1):
                for indicator in contradiction_indicators:
                    if indicator in statement.lower() and indicator in other_statement.lower():
                        contradictions += 1
        
        # Return consistency score (1 = fully consistent, 0 = highly contradictory)
        max_possible_contradictions = len(statements) * (len(statements) - 1) / 2
        if max_possible_contradictions == 0:
            return 1.0
        
        consistency_score = 1.0 - (contradictions / max_possible_contradictions)
        return max(0.0, min(1.0, consistency_score))
    
    def _check_completeness(self, reasoning_chain: List[AIThought]) -> float:
        """Check reasoning completeness"""
        expected_steps = ['analysis', 'knowledge', 'inference', 'conclusion']
        found_steps = set()
        
        for thought in reasoning_chain:
            content_lower = thought.content.lower()
            for step in expected_steps:
                if step in content_lower:
                    found_steps.add(step)
        
        completeness_score = len(found_steps) / len(expected_steps)
        return completeness_score
    
    def _check_soundness(self, reasoning_chain: List[AIThought]) -> float:
        """Check logical soundness"""
        # Check if conclusions follow from premises
        total_confidence = sum(thought.confidence for thought in reasoning_chain)
        avg_confidence = total_confidence / len(reasoning_chain) if reasoning_chain else 0
        
        # Simple soundness metric based on confidence consistency
        confidence_variance = statistics.variance([t.confidence for t in reasoning_chain]) if len(reasoning_chain) > 1 else 0
        soundness_score = avg_confidence * (1 - confidence_variance)
        
        return max(0.0, min(1.0, soundness_score))
    
    def _check_relevance(self, reasoning_chain: List[AIThought]) -> float:
        """Check relevance of reasoning steps"""
        # Simple relevance check - ensure each step builds on previous ones
        relevance_scores = []
        
        for i, thought in enumerate(reasoning_chain[1:], 1):
            previous_thought = reasoning_chain[i-1]
            
            # Check for common keywords or concepts
            current_words = set(thought.content.lower().split())
            previous_words = set(previous_thought.content.lower().split())
            
            overlap = len(current_words.intersection(previous_words))
            total_words = len(current_words.union(previous_words))
            
            relevance = overlap / total_words if total_words > 0 else 0
            relevance_scores.append(relevance)
        
        return statistics.mean(relevance_scores) if relevance_scores else 1.0
    
    def _check_coherence(self, reasoning_chain: List[AIThought]) -> float:
        """Check overall coherence of reasoning"""
        if not reasoning_chain:
            return 0.0
        
        # Check if reasoning steps follow a logical progression
        coherence_factors = []
        
        # Factor 1: Confidence progression (should generally increase or stay stable)
        confidences = [t.confidence for t in reasoning_chain]
        confidence_trend = 1.0 if len(confidences) <= 1 else (confidences[-1] - confidences[0]) / len(confidences)
        coherence_factors.append(max(0, confidence_trend + 0.5))  # Normalize to 0-1
        
        # Factor 2: Step numbering consistency
        steps = [t.reasoning_step for t in reasoning_chain if hasattr(t, 'reasoning_step')]
        step_consistency = 1.0 if steps == sorted(steps) else 0.5
        coherence_factors.append(step_consistency)
        
        # Factor 3: Content flow (basic check for connecting words)
        connecting_words = ['therefore', 'thus', 'consequently', 'because', 'since', 'as a result']
        connections = sum(1 for thought in reasoning_chain 
                         for word in connecting_words 
                         if word in thought.content.lower())
        connection_score = min(1.0, connections / max(1, len(reasoning_chain) - 1))
        coherence_factors.append(connection_score)
        
        return statistics.mean(coherence_factors)