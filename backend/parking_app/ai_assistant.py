"""
AI Query Assistant for explaining parking assignments.
Users can ask why they were assigned a specific parking slot.
Enhanced with Google Gemini AI for intelligent responses.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from parking_app.models import Assignment
from parking_app.assignment_engine import ParkingAssignmentEngine
from parking_app.gemini_service import GeminiParkingAssistant
import logging

logger = logging.getLogger(__name__)


class ParkingQueryAssistant:
    """
    AI Assistant for explaining parking assignments.
    Provides reasons why a user was assigned a specific slot.
    """
    
    def __init__(self):
        self.engine = ParkingAssignmentEngine()
    
    def explain_assignment(self, assignment):
        """
        Explain why a user was assigned a specific parking slot.
        Returns a structured explanation with assignment factors.
        """
        if not assignment:
            return None
        
        user = assignment.user
        slot = assignment.parking_slot
        schedule = assignment.schedule
        building = schedule.building
        
        # Calculate distance
        distance = self.engine._calculate_distance(slot, building)
        
        # Get subscription info
        subscription_type = 'basic'
        if hasattr(user, 'subscription') and user.subscription.is_active():
            subscription_type = user.subscription.subscription_type
        
        # Build explanation
        explanation = {
            'assignment_id': assignment.id,
            'parking_slot': {
                'slot_number': slot.slot_number,
                'slot_type': slot.slot_type,
                'building': slot.parking_lot.name,
                'status': slot.status,
            },
            'user': {
                'email': user.email,
                'subscription_type': subscription_type,
            },
            'schedule': {
                'building': building.name,
                'start_date': schedule.start_date,
                'end_date': schedule.end_date,
                'start_time': str(schedule.start_time),
                'end_time': str(schedule.end_time),
            },
            'assignment_factors': {
                'distance_to_building': f"{distance}m" if distance else "N/A",
                'slot_type_priority': self._get_slot_type_explanation(slot.slot_type, subscription_type),
                'availability_status': 'Available during your schedule',
                'confidence_score': round(assignment.ai_confidence_score * 100, 1) if assignment.ai_confidence_score else 0,
            },
            'summary': self._generate_summary(user, slot, distance, subscription_type, building),
            'alternatives': self._get_alternatives(user, assignment),
        }
        
        return explanation
    
    def _get_slot_type_explanation(self, slot_type, subscription_type):
        """Explain why this slot type was assigned based on subscription."""
        explanations = {
            'premium': 'Premium slot - assigned for priority access',
            'reserved': 'Reserved premium slot - VIP tier benefit',
            'regular': 'Regular slot - standard parking option',
            'handicap': 'Accessible slot - for users needing accommodation',
        }
        
        type_exp = explanations.get(slot_type, 'Standard slot')
        
        # Add subscription context
        if subscription_type == 'vip' and slot_type in ['premium', 'reserved']:
            type_exp += f" (VIP subscriber benefit)"
        elif subscription_type == 'premium' and slot_type == 'premium':
            type_exp += f" (Premium subscriber benefit)"
        
        return type_exp
    
    def _generate_summary(self, user, slot, distance, subscription_type, building):
        """Generate human-readable summary of the assignment."""
        summaries = {
            'vip': f"As a VIP subscriber, you were assigned {slot.slot_number} ({slot.slot_type} slot) "
                   f"because it provides premium parking {distance}m from {building.name} with secure access.",
            'premium': f"As a Premium subscriber, you were assigned {slot.slot_number} ({slot.slot_type} slot) "
                      f"offering priority parking {distance}m from {building.name}.",
            'basic': f"You were assigned {slot.slot_number} ({slot.slot_type} slot), "
                    f"the best available option {distance}m from {building.name} matching your schedule."
        }
        
        return summaries.get(subscription_type, summaries['basic'])
    
    def _get_alternatives(self, user, assignment):
        """Suggest alternative parking slots that could have been assigned."""
        # Get other available slots for this schedule
        available = self.engine._get_available_slots(user, assignment.schedule)
        alternatives = available.exclude(id=assignment.parking_slot.id)[:2]
        
        return [
            {
                'slot_number': alt.slot_number,
                'slot_type': alt.slot_type,
                'distance': self.engine._calculate_distance(alt, assignment.schedule.building),
                'reason': f"Alternative {alt.slot_type} slot also available during your schedule"
            }
            for alt in alternatives
        ]
    
    def answer_query(self, user, query_text):
        """
        Answer a natural language query about parking using Gemini AI.
        Falls back to keyword matching if Gemini is unavailable.
        """
        query_lower = query_text.lower().strip()
        current_assignment = Assignment.objects.filter(
            user=user, 
            status='active'
        ).first()
        
        # Try Gemini AI FIRST for all substantive questions
        gemini = GeminiParkingAssistant()
        if gemini.is_available and len(query_text) > 10:  # Only use Gemini for longer/detailed questions
            try:
                # Build context for Gemini
                context = {}
                if current_assignment:
                    context['current_assignment'] = {
                        'slot_number': current_assignment.parking_slot.slot_number,
                        'slot_type': current_assignment.parking_slot.slot_type,
                    }
                    context['distance'] = current_assignment.distance_to_building
                
                # If user has subscription, add it
                if hasattr(user, 'subscription') and user.subscription:
                    context['subscription'] = user.subscription.subscription_type
                
                response = gemini.generate_response(query_text, context)
                if response:
                    return {
                        'query_type': 'ai_response',
                        'response': response,
                        'powered_by': 'Gemini AI'
                    }
            except Exception as e:
                logger.error(f"Gemini error: {str(e)}")
                # Fall through to keyword matching
        
        # Handle simple greetings
        if any(word in query_lower for word in ['hello', 'hi ', 'hi,', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return {
                'query_type': 'greeting',
                'response': "Hello! I'm your parking assistant. I can help you with questions about your assignment, alternative parking options, subscription benefits, or how the system works. What would you like to know?",
                'powered_by': 'Keyword Match'
            }
        
        # Handle thankful messages
        if any(word in query_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
            return {
                'query_type': 'thanks',
                'response': "You're welcome! I'm here to help anytime. Feel free to ask me anything about your parking assignment or the system. Is there anything else you'd like to know?",
                'powered_by': 'Keyword Match'
            }
        
        # Handle help requests
        if any(word in query_lower for word in ['help', 'assist', 'support', 'guide', 'what can you do']):
            return {
                'query_type': 'help',
                'response': "I can help with the following:\n"
                           "• Ask why you were assigned your current slot\n"
                           "• Find alternative parking options\n"
                           "• Learn about subscription benefits\n"
                           "• Understand how the parking system works\n"
                           "Just ask me any of these questions!",
                'powered_by': 'Keyword Match'
            }
        
        # Keyword-based fallbacks for parking-specific questions
        if any(word in query_lower for word in ['why', 'reason', 'assigned', 'explanation']):
            if current_assignment:
                explanation = self.explain_assignment(current_assignment)
                return {
                    'query_type': 'explanation',
                    'response': f"You were assigned {current_assignment.parking_slot.slot_number} because: "
                               f"{explanation['summary']}",
                    'details': explanation,
                    'powered_by': 'System'
                }
        
        if any(word in query_lower for word in ['change', 'swap', 'different', 'closer', 'better', 'options', 'alternative']):
            if current_assignment:
                alternatives = self._get_alternatives(user, current_assignment)
                return {
                    'query_type': 'alternatives',
                    'response': f"Based on your schedule, here are alternative parking options that might work for you. "
                               f"Contact the parking office if you'd like to switch.",
                    'alternatives': alternatives,
                    'powered_by': 'System'
                }
        
        # If we have Gemini but question was too short, try it anyway for context
        if gemini.is_available:
            try:
                context = {}
                if current_assignment:
                    context['current_assignment'] = {
                        'slot_number': current_assignment.parking_slot.slot_number,
                        'slot_type': current_assignment.parking_slot.slot_type,
                    }
                    context['distance'] = current_assignment.distance_to_building
                
                if hasattr(user, 'subscription') and user.subscription:
                    context['subscription'] = user.subscription.subscription_type
                
                response = gemini.generate_response(query_text, context)
                if response:
                    return {
                        'query_type': 'ai_response',
                        'response': response,
                        'powered_by': 'Gemini AI'
                    }
            except Exception as e:
                logger.error(f"Gemini fallback error: {str(e)}")
        
        # Default response
        return {
            'query_type': 'general',
            'response': "I can help with questions about your parking assignment, alternative options, "
                       "subscription benefits, or how the system works. What would you like to know?",
            'powered_by': 'Keyword Match'
        }


class ParkingAssistantViewSet(viewsets.ViewSet):
    """
    API endpoints for the AI parking assistant.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_assignment(self, request):
        """Get explanation for current parking assignment."""
        assignment = Assignment.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        if not assignment:
            return Response(
                {'error': 'No active parking assignment found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        assistant = ParkingQueryAssistant()
        explanation = assistant.explain_assignment(assignment)
        
        return Response(explanation, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        Ask the AI assistant a question about your parking.
        
        Request body:
        {
            "query": "Why was I assigned this slot?"
        }
        """
        query_text = request.data.get('query', '').strip()
        
        if not query_text:
            return Response(
                {'error': 'Please provide a query'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assistant = ParkingQueryAssistant()
        response = assistant.answer_query(request.user, query_text)
        
        logger.info(f"User {request.user.email} query: {query_text}")
        
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def help(self, request):
        """Get help on what you can ask the assistant."""
        help_text = {
            'examples': [
                "Why was I assigned this parking slot?",
                "Can I get a closer parking spot?",
                "What are my other parking options?",
                "How does the parking assignment system work?",
                "What are the subscription benefits?",
                "How can I upgrade my subscription?"
            ],
            'query_types': [
                'explanation - Ask why you were assigned a slot',
                'alternatives - Find other parking options',
                'subscription - Learn about tiers and benefits',
                'system_info - Understand how the algorithm works',
                'general - General questions about parking'
            ],
            'tips': [
                'Be specific in your questions',
                'Ask about your current assignment or alternatives',
                'Inquire about subscription benefits for better parking',
                'Contact the parking office for manual changes'
            ]
        }
        
        return Response(help_text, status=status.HTTP_200_OK)
