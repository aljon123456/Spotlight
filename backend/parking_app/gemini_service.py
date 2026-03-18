"""
Google Gemini AI Service for Parking Assistant
Provides intelligent responses about parking assignments, subscriptions, and more.
"""
import google.generativeai as genai
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', None)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL = "gemini-pro"
else:
    MODEL = None
    logger.warning("GEMINI_API_KEY not configured. Gemini features will be disabled.")


class GeminiParkingAssistant:
    """
    AI-powered assistant using Google Gemini for answering parking questions.
    Provides context-aware responses about the parking system.
    """
    
    SYSTEM_PROMPT = """You are a helpful parking assistant for SpotLight, an intelligent parking management system at Holy Angel University.

SpotLight provides:
1. **Automated Parking Assignment** - The system intelligently assigns parking spots based on:
   - User's schedule and building location
   - Parking availability
   - Subscription tier
   - Distance optimization

2. **Subscription Tiers:**
   - **Basic**: Free tier, standard parking access, can hold 1 active reservation
   - **Premium**: Enhanced tier with priority parking access, can hold 3 active reservations
   - **VIP**: Top tier with exclusive reserved spots, can hold 5 active reservations, premium benefits

3. **Key Features:**
   - User confirmation system (30-minute grace period)
   - Auto-adjustment when availability changes
   - Alternative parking suggestions
   - Real-time notifications
   - No-show tracking

When answering questions:
- Be helpful, friendly, and concise
- Focus on the user's parking needs
- Explain subscription benefits clearly
- Provide practical advice
- If asked about technical details, explain simply
- Always encourage users to contact the parking office for special requests

Answer only about parking-related topics. For unrelated questions, politely redirect to parking assistance."""

    def __init__(self):
        self.is_available = MODEL is not None
    
    def generate_response(self, user_query, context=None):
        """
        Generate a response using Gemini AI.
        
        Args:
            user_query: The user's question
            context: Optional context about the user's assignment
        
        Returns:
            str: The AI-generated response
        """
        if not self.is_available:
            return None
        
        try:
            # Build context string if provided
            context_str = ""
            if context:
                if context.get('current_assignment'):
                    assignment = context['current_assignment']
                    context_str = f"\nUser's current assignment: Slot {assignment.get('slot_number')} ({assignment.get('slot_type')} type)\n"
                if context.get('subscription'):
                    context_str += f"Subscription tier: {context['subscription']}\n"
                if context.get('distance'):
                    context_str += f"Distance to building: {context['distance']}m\n"
            
            # Prepare the full prompt
            full_prompt = f"{self.SYSTEM_PROMPT}\n\nUser Question: {user_query}{context_str}"
            
            # Call Gemini
            model = genai.GenerativeModel(MODEL)
            response = model.generate_content(full_prompt)
            
            if response and response.text:
                return response.text
            else:
                return None
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None
    
    def answer_specific_question(self, user, question_text):
        """
        Answer a specific parking question with Gemini.
        Examples: "What's the difference between Premium and VIP?"
                  "Why was I assigned this slot?"
                  "Can I change my assignment?"
        """
        if not self.is_available:
            return {
                'success': False,
                'response': 'AI assistant is not configured. Please contact support.',
                'powered_by': None
            }
        
        try:
            response = self.generate_response(question_text)
            
            if response:
                return {
                    'success': True,
                    'response': response,
                    'powered_by': 'Gemini',
                    'query': question_text
                }
            else:
                return {
                    'success': False,
                    'response': 'Could not generate a response. Please try again.',
                    'powered_by': 'Gemini'
                }
                
        except Exception as e:
            logger.error(f"Error in answer_specific_question: {str(e)}")
            return {
                'success': False,
                'response': 'An error occurred. Please try again later.',
                'powered_by': 'Gemini',
                'error': str(e)
            }
