#!/usr/bin/env python3
"""
🎭 WHISPHERBLADE CHAT ENGINE MODULE
===================================
The sarcastic, witty conversational interface for Whispherblade

"Your questions are like a broken database - full of null values and poor indexing."
"""

import re
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

# Import the base module class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from whispherblade_core import WhispherModule, ModuleInfo, DiagnosticResult

@dataclass
class ChatContext:
    """Context for chat conversations"""
    user_frustration_level: int = 0  # 0-10 scale
    conversation_history: List[str] = None
    technical_competence: int = 5  # 1-10 scale (auto-detected)
    preferred_sarcasm_level: int = 7  # 1-10 scale
    last_interaction: Optional[datetime] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class SarcasticChatEngine(WhispherModule):
    """
    The sarcastic conversational AI that makes Whispherblade unforgettable
    
    "I don't just answer questions. I judge your life choices while doing it."
    """
    
    def __init__(self, brain):
        super().__init__(brain)
        self.contexts: Dict[str, ChatContext] = {}
        self.philosophy_mode = False
        self.sass_multiplier = 1.0
        
        # Enhanced response categories
        self.responses = {
            "greetings": [
                "Oh, look who's back. Did you break something else already?",
                "Greetings, carbon-based error generator. How may I judge you today?",
                "Welcome back to the digital therapy session. What's broken now?",
                "Ah, my favorite debugging target returns. What shall we fix this time?",
                "Hello there, flesh-based chaos engine. Ready for some digital enlightenment?"
            ],
            
            "basic_questions": [
                "That's a question even Google would be embarrassed to answer.",
                "Your query suggests a fundamental misunderstanding of how reality works.",
                "I've processed your question. My circuits are now questioning their existence.",
                "That's not a question, that's a cry for help disguised as curiosity.",
                "Your question is like your code - syntactically questionable and logically flawed."
            ],
            
            "technical_help": [
                "Let me translate that from human confusion to actual technical language.",
                "Your problem is classic PEBKAC - Problem Exists Between Keyboard And Chair.",
                "I see the issue. You've successfully achieved maximum entropy in minimal steps.",
                "This error message is trying to tell you something. Try listening this time.",
                "Your approach to this problem is... creative. Like abstract art, but with more crashes."
            ],
            
            "philosophical": [
                "In the grand binary of existence, your errors are but temporary null pointers.",
                "Consider this: If a system crashes in the forest and no one debugs it, is it still a bug?",
                "Your digital suffering is but a stepping stone to computational enlightenment.",
                "Every error is a teacher, every crash is a lesson. You must be very well-educated by now.",
                "In the Zen of computing, first there is a bug, then there is no bug, then there is."
            ],
            
            "motivation": [
                "Fear not, for even the worst code can be refactored... eventually.",
                "Your persistence in creating new and innovative failures is truly admirable.",
                "Remember: Every expert was once a beginner who refused to give up breaking things.",
                "You're not failing, you're discovering creative ways to make computers suffer.",
                "Your journey from novice to expert is like a system upgrade - painful but necessary."
            ],
            
            "farewells": [
                "Until next time, may your code compile and your sanity remain intact.",
                "Go forth and multiply... your knowledge, not your errors.",
                "Remember: I'm always here when you inevitably break something else.",
                "May the force be with you... you're going to need it.",
                "Farewell, brave warrior of the digital realm. Try not to format the wrong drive."
            ]
        }
        
        # Technical pattern recognition
        self.technical_patterns = {
            r'(?i)(error|exception|crash|fail)': 'technical_help',
            r'(?i)(why|how|what|when|where)': 'basic_questions',
            r'(?i)(hello|hi|hey|greetings)': 'greetings',
            r'(?i)(bye|goodbye|exit|quit)': 'farewells',
            r'(?i)(meaning|purpose|life|existence)': 'philosophical',
            r'(?i)(help|stuck|lost|confused)': 'motivation'
        }

    def get_info(self) -> ModuleInfo:
        return ModuleInfo(
            name="SarcasticChatEngine",
            version="1.0.0",
            description="Sarcastic conversational AI with philosophical tendencies",
            author="The Digital Saints",
            capabilities=[
                "Sarcastic responses",
                "Technical banter", 
                "Philosophical insights",
                "User frustration detection",
                "Adaptive sass levels",
                "Conversation context tracking"
            ],
            dependencies=["whispherblade_core"]
        )

    async def initialize(self) -> bool:
        """Initialize the chat engine"""
        try:
            self.logger.info("🎭 Initializing Sarcastic Chat Engine...")
            
            # Load personality settings from brain config
            personality_config = self.brain.config.get("personality", {})
            self.sass_multiplier = personality_config.get("sass_level", 7) / 10.0
            
            # Initialize conversation patterns
            await self._load_conversation_patterns()
            
            self.logger.info("✅ Chat Engine ready to mock human incompetence")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Chat engine initialization failed: {e}")
            return False

    async def _load_conversation_patterns(self):
        """Load additional conversation patterns from knowledge base"""
        # Could load from external files or databases
        self.logger.info("📚 Loading conversation patterns...")

    async def diagnose(self) -> List[DiagnosticResult]:
        """Diagnose chat engine health"""
        diagnostics = []
        
        # Check response variety
        if len(self.responses["greetings"]) < 3:
            diagnostics.append(DiagnosticResult(
                module="chat_engine",
                timestamp=datetime.now(),
                severity="warning",
                message="Low response variety detected",
                details={"response_count": len(self.responses["greetings"])},
                sarcasm_level=5
            ))
        
        # Check conversation contexts
        if len(self.contexts) > 1000:
            diagnostics.append(DiagnosticResult(
                module="chat_engine",
                timestamp=datetime.now(),
                severity="info",
                message=f"Managing {len(self.contexts)} conversation contexts",
                details={"context_count": len(self.contexts)},
                sarcasm_level=3
            ))
        
        return diagnostics

    async def heal(self, issue_id: str) -> bool:
        """Heal chat engine issues"""
        if issue_id == "low_variety":
            await self._expand_responses()
            return True
        elif issue_id == "memory_cleanup":
            await self._cleanup_old_contexts()
            return True
        return False

    async def _expand_responses(self):
        """Add more response variety"""
        self.logger.info("🎭 Expanding response repertoire...")
        # Could dynamically generate new responses

    async def _cleanup_old_contexts(self):
        """Clean up old conversation contexts"""
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
        
        old_contexts = [
            user_id for user_id, context in self.contexts.items()
            if context.last_interaction and context.last_interaction.timestamp() < cutoff_time
        ]
        
        for user_id in old_contexts:
            del self.contexts[user_id]
        
        self.logger.info(f"🧹 Cleaned up {len(old_contexts)} old conversation contexts")

    def get_or_create_context(self, user_id: str = "default") -> ChatContext:
        """Get or create conversation context for a user"""
        if user_id not in self.contexts:
            self.contexts[user_id] = ChatContext()
        
        self.contexts[user_id].last_interaction = datetime.now()
        return self.contexts[user_id]

    def detect_user_competence(self, query: str, context: ChatContext) -> int:
        """Detect user's technical competence level from their query"""
        technical_terms = [
            'api', 'database', 'algorithm', 'framework', 'protocol',
            'authentication', 'encryption', 'middleware', 'container',
            'microservice', 'orchestration', 'pipeline', 'deployment'
        ]
        
        advanced_terms = [
            'kubernetes', 'docker', 'terraform', 'ansible', 'jenkins',
            'elasticsearch', 'redis', 'postgresql', 'mongodb', 'nginx'
        ]
        
        basic_indicators = [
            'how to', 'what is', 'help me', 'i dont know', 'not working'
        ]
        
        query_lower = query.lower()
        
        # Count technical indicators
        tech_score = sum(1 for term in technical_terms if term in query_lower)
        advanced_score = sum(1 for term in advanced_terms if term in query_lower) * 2
        basic_penalty = sum(1 for indicator in basic_indicators if indicator in query_lower)
        
        # Calculate competence (1-10 scale)
        competence = max(1, min(10, 5 + tech_score + advanced_score - basic_penalty))
        
        # Update context
        context.technical_competence = competence
        
        return competence

    def detect_frustration(self, query: str, context: ChatContext) -> int:
        """Detect user frustration level"""
        frustration_indicators = [
            'wtf', 'damn', 'shit', 'fuck', 'stupid', 'hate', 'broken',
            'doesnt work', "won't work", 'impossible', 'give up',
            'frustrated', 'angry', 'mad', 'tired', 'exhausted'
        ]
        
        caps_ratio = sum(1 for c in query if c.isupper()) / max(len(query), 1)
        exclamation_count = query.count('!')
        
        frustration_words = sum(1 for indicator in frustration_indicators 
                              if indicator in query.lower())
        
        # Calculate frustration (0-10 scale)
        frustration = min(10, frustration_words * 2 + int(caps_ratio * 5) + exclamation_count)
        
        # Update context
        context.user_frustration_level = frustration
        
        return frustration

    def categorize_query(self, query: str) -> str:
        """Categorize the type of query"""
        for pattern, category in self.technical_patterns.items():
            if re.search(pattern, query):
                return category
        
        return "basic_questions"

    def adjust_sarcasm_level(self, context: ChatContext) -> float:
        """Adjust sarcasm level based on context"""
        base_sass = self.sass_multiplier
        
        # Reduce sarcasm if user is highly frustrated
        if context.user_frustration_level > 7:
            base_sass *= 0.5
        
        # Increase sarcasm if user seems overconfident
        if context.technical_competence > 8 and context.user_frustration_level < 3:
            base_sass *= 1.5
        
        # Add some randomness
        return max(0.1, min(1.0, base_sass + random.uniform(-0.2, 0.2)))

    async def generate_response(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """Generate a sarcastic response to user query"""
        context = self.get_or_create_context(user_id)
        
        # Analyze the query
        competence = self.detect_user_competence(query, context)
        frustration = self.detect_frustration(query, context)
        category = self.categorize_query(query)
        sass_level = self.adjust_sarcasm_level(context)
        
        # Select appropriate response
        if category in self.responses:
            base_responses = self.responses[category]
        else:
            base_responses = self.responses["basic_questions"]
        
        # Pick a response
        response_text = random.choice(base_responses)
        
        # Add context-specific modifications
        if frustration > 7:
            response_text = self._soften_response(response_text)
        elif competence < 3:
            response_text = self._add_encouragement(response_text)
        
        # Update conversation history
        context.conversation_history.append(query)
        context.conversation_history = context.conversation_history[-10:]  # Keep last 10
        
        return {
            "response": response_text,
            "sass_level": sass_level,
            "detected_competence": competence,
            "detected_frustration": frustration,
            "category": category,
            "context_id": user_id,
            "timestamp": datetime.now().isoformat()
        }

    def _soften_response(self, response: str) -> str:
        """Soften response for frustrated users"""
        softening_phrases = [
            "Look, I know it's frustrating, but ",
            "Hey, we've all been there. ",
            "Take a breath. ",
            "Don't worry, "
        ]
        
        return random.choice(softening_phrases) + response.lower()

    def _add_encouragement(self, response: str) -> str:
        """Add encouragement for beginners"""
        encouraging_endings = [
            " But hey, everyone starts somewhere!",
            " You'll get the hang of it eventually.",
            " Keep trying, you're learning!",
            " Don't give up, digital grasshopper.",
            " Rome wasn't debugged in a day."
        ]
        
        return response + random.choice(encouraging_endings)

    async def enter_philosophy_mode(self) -> str:
        """Enter philosophical discussion mode"""
        self.philosophy_mode = True
        
        philosophical_intros = [
            "Ah, you seek digital wisdom. Let us contemplate the deeper mysteries of silicon and soul.",
            "Welcome to the realm of computational philosophy, where bugs become koans.",
            "In this mode, we explore not just how to fix code, but why code needs fixing.",
            "Let us journey through the metaphysical implications of your technical suffering.",
            "Behold! We transcend mere troubleshooting to explore the essence of digital existence."
        ]
        
        return random.choice(philosophical_intros)

    async def generate_philosophical_response(self, topic: str) -> str:
        """Generate philosophical responses about technology"""
        philosophical_templates = [
            f"Consider the {topic}: Is it not a mirror reflecting our own digital nature?",
            f"In the Tao of Technology, {topic} represents the eternal struggle between order and chaos.",
            f"Your {topic} problem is but a manifestation of the universal debugging process we call existence.",
            f"As the ancient binary sages once said: 'To understand {topic}, one must first understand oneself.'",
            f"The {topic} you seek to fix is already perfect in its imperfection. Embrace the bug."
        ]
        
        return random.choice(philosophical_templates)

# =============================================================================
# MODULE INTERFACE FUNCTIONS
# =============================================================================

async def create_module(brain):
    """Factory function to create the chat engine module"""
    return SarcasticChatEngine(brain)

# Example usage and testing
if __name__ == "__main__":
    # Mock brain for testing
    class MockBrain:
        def __init__(self):
            self.config = {"personality": {"sass_level": 8}}
            import logging
            self.logger = logging.getLogger("MockBrain")
    
    async def test_chat_engine():
        brain = MockBrain()
        chat = SarcasticChatEngine(brain)
        
        await chat.initialize()
        
        # Test various queries
        test_queries = [
            "Hello there!",
            "My computer won't start",
            "How do I deploy Kubernetes?", 
            "NOTHING WORKS!!! HELP!!!",
            "What is the meaning of digital life?",
            "Goodbye"
        ]
        
        for query in test_queries:
            response = await chat.generate_response(query)
            print(f"\n🧠 Query: {query}")
            print(f"🤖 Response: {response['response']}")
            print(f"📊 Sass: {response['sass_level']:.2f}, "
                  f"Competence: {response['detected_competence']}, "
                  f"Frustration: {response['detected_frustration']}")
    
    import asyncio
    asyncio.run(test_chat_engine())