"""Relationship Insights Service.

Analyzes communication patterns between users to provide relationship insights.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

from app.parser import ParsedMessage

logger = logging.getLogger(__name__)


class RelationshipInsightsService:
    """Service for analyzing relationships between users."""
    
    def analyze_compatibility(
        self,
        user1_messages: List[ParsedMessage],
        user2_messages: List[ParsedMessage],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """
        Analyze communication style compatibility between two users.
        
        Args:
            user1_messages: First user's messages
            user2_messages: Second user's messages
            user1_name: First user's name
            user2_name: Second user's name
            
        Returns:
            Compatibility analysis
        """
        # Message length similarity
        u1_avg_length = sum(len(m.message.split()) for m in user1_messages if not m.is_media) / max(len(user1_messages), 1)
        u2_avg_length = sum(len(m.message.split()) for m in user2_messages if not m.is_media) / max(len(user2_messages), 1)
        length_similarity = 1 - min(abs(u1_avg_length - u2_avg_length) / max(u1_avg_length, u2_avg_length, 1), 1)
        
        # Activity time similarity
        u1_hours = Counter(m.timestamp.hour for m in user1_messages)
        u2_hours = Counter(m.timestamp.hour for m in user2_messages)
        time_overlap = len(set(u1_hours.keys()).intersection(set(u2_hours.keys()))) / 24
        
        # Response patterns
        u1_questions = sum(1 for m in user1_messages if '?' in m.message and not m.is_media)
        u2_questions = sum(1 for m in user2_messages if '?' in m.message and not m.is_media)
        question_balance = 1 - abs(u1_questions - u2_questions) / max(u1_questions + u2_questions, 1)
        
        # Overall compatibility score
        compatibility_score = (length_similarity * 0.3 + time_overlap * 0.3 + question_balance * 0.4)
        
        return {
            'users': [user1_name, user2_name],
            'compatibility_score': round(compatibility_score * 100, 2),
            'metrics': {
                'message_length_similarity': round(length_similarity * 100, 2),
                'activity_time_overlap': round(time_overlap * 100, 2),
                'question_balance': round(question_balance * 100, 2)
            },
            'insights': self._generate_compatibility_insights(
                length_similarity, time_overlap, question_balance
            )
        }
    
    def analyze_interaction_frequency(
        self,
        all_messages: List[ParsedMessage],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """
        Analyze interaction frequency and patterns between two users.
        
        Args:
            all_messages: All messages from conversation
            user1_name: First user's name
            user2_name: Second user's name
            
        Returns:
            Interaction frequency analysis
        """
        # Filter messages between these two users
        interaction_messages = [
            m for m in all_messages 
            if m.username in [user1_name, user2_name]
        ]
        
        if not interaction_messages:
            return {'error': 'No interactions found between users'}
        
        # Group by date
        daily_interactions = defaultdict(lambda: {user1_name: 0, user2_name: 0})
        for msg in interaction_messages:
            date = msg.timestamp.date()
            daily_interactions[date][msg.username] += 1
        
        # Calculate metrics
        total_days = (max(daily_interactions.keys()) - min(daily_interactions.keys())).days + 1
        active_days = len(daily_interactions)
        avg_messages_per_day = len(interaction_messages) / max(active_days, 1)
        
        # Find longest conversation streak
        sorted_dates = sorted(daily_interactions.keys())
        max_streak = 1
        current_streak = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        # Balance of interaction
        u1_count = sum(1 for m in interaction_messages if m.username == user1_name)
        u2_count = sum(1 for m in interaction_messages if m.username == user2_name)
        interaction_balance = min(u1_count, u2_count) / max(u1_count, u2_count, 1)
        
        return {
            'users': [user1_name, user2_name],
            'total_interactions': len(interaction_messages),
            'time_period': {
                'start': min(daily_interactions.keys()).isoformat(),
                'end': max(daily_interactions.keys()).isoformat(),
                'total_days': total_days,
                'active_days': active_days
            },
            'frequency': {
                'avg_messages_per_day': round(avg_messages_per_day, 2),
                'longest_streak_days': max_streak,
                'interaction_balance': round(interaction_balance * 100, 2)
            },
            'message_distribution': {
                user1_name: u1_count,
                user2_name: u2_count
            }
        }
    
    def analyze_emotional_support(
        self,
        all_messages: List[ParsedMessage],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """
        Analyze emotional support patterns in conversation.
        
        Args:
            all_messages: All messages from conversation
            user1_name: First user's name
            user2_name: Second user's name
            
        Returns:
            Emotional support analysis
        """
        # Support keywords/phrases
        support_keywords = {
            'empathy': ['understand', 'feel', 'sorry', 'sad', 'happy', 'proud'],
            'encouragement': ['can do', 'believe', 'great', 'awesome', 'amazing', 'good job'],
            'help': ['help', 'support', 'here for you', 'let me know', 'anything you need'],
            'agreement': ['yeah', 'yes', 'agree', 'exactly', 'right', 'true']
        }
        
        user_support_scores = {user1_name: defaultdict(int), user2_name: defaultdict(int)}
        
        for msg in all_messages:
            if msg.is_media or msg.username not in [user1_name, user2_name]:
                continue
            
            msg_lower = msg.message.lower()
            for category, keywords in support_keywords.items():
                for keyword in keywords:
                    if keyword in msg_lower:
                        user_support_scores[msg.username][category] += 1
        
        return {
            'users': [user1_name, user2_name],
            'support_patterns': {
                user1_name: dict(user_support_scores[user1_name]),
                user2_name: dict(user_support_scores[user2_name])
            },
            'insights': self._generate_support_insights(user_support_scores, user1_name, user2_name)
        }
    
    def detect_conflicts(
        self,
        all_messages: List[ParsedMessage],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """
        Detect potential conflict patterns in conversations with detailed reasoning.
        
        Args:
            all_messages: All messages from conversation
            user1_name: First user's name
            user2_name: Second user's name
            
        Returns:
            Conflict detection analysis with sources of divergence and evidence
        """
        # Conflict indicators with categories
        disagreement_keywords = ['no', 'disagree', 'wrong', 'not true', 'incorrect', "don't think so"]
        frustration_keywords = ['seriously', 'whatever', 'fine', 'never mind', 'forget it', 'why would']
        defensive_keywords = ['but', 'however', 'actually', 'technically', 'well actually', 'not really']
        negative_keywords = ['never', 'always', 'can\'t', 'won\'t', 'refuse', 'impossible']
        
        exclamation_threshold = 2  # Multiple exclamation marks
        caps_threshold = 0.5  # More than 50% caps
        question_threshold = 2  # Multiple question marks (could indicate confusion/frustration)
        
        potential_conflicts = []
        divergence_sources = []
        topic_disagreements = {}
        
        for i, msg in enumerate(all_messages):
            if msg.is_media or msg.username not in [user1_name, user2_name]:
                continue
            
            conflict_score = 0
            indicators = []
            conflict_type = []
            
            msg_lower = msg.message.lower()
            
            # Check for disagreement patterns
            disagreement_count = sum(1 for kw in disagreement_keywords if kw in msg_lower)
            if disagreement_count > 0:
                conflict_score += disagreement_count * 2
                indicators.append(f"direct disagreement ('{', '.join([kw for kw in disagreement_keywords if kw in msg_lower])}')")
                conflict_type.append("disagreement")
            
            # Check for frustration
            frustration_count = sum(1 for kw in frustration_keywords if kw in msg_lower)
            if frustration_count > 0:
                conflict_score += frustration_count * 1.5
                indicators.append(f"frustration signals ('{', '.join([kw for kw in frustration_keywords if kw in msg_lower])}')")
                conflict_type.append("frustration")
            
            # Check for defensive language
            defensive_count = sum(1 for kw in defensive_keywords if kw in msg_lower)
            if defensive_count > 0:
                conflict_score += defensive_count
                indicators.append(f"defensive tone ('{', '.join([kw for kw in defensive_keywords if kw in msg_lower])}')")
                conflict_type.append("defensive")
            
            # Check for absolute negative language
            negative_count = sum(1 for kw in negative_keywords if kw in msg_lower)
            if negative_count > 0:
                conflict_score += negative_count
                indicators.append(f"absolute/negative language ('{', '.join([kw for kw in negative_keywords if kw in msg_lower])}')")
                conflict_type.append("negative")
            
            # Check for excessive punctuation
            exclamation_count = msg.message.count('!')
            if exclamation_count >= exclamation_threshold:
                conflict_score += 2
                indicators.append(f"multiple exclamation marks ({exclamation_count}x)")
                conflict_type.append("emotional_intensity")
            
            question_count = msg.message.count('?')
            if question_count >= question_threshold:
                conflict_score += 1
                indicators.append(f"multiple question marks ({question_count}x - possible confusion/frustration)")
                conflict_type.append("confusion")
            
            # Check for excessive caps
            if len(msg.message) > 5:
                caps_ratio = sum(1 for c in msg.message if c.isupper()) / len(msg.message)
                if caps_ratio > caps_threshold:
                    conflict_score += 2
                    indicators.append(f"excessive capitalization ({int(caps_ratio*100)}% of message)")
                    conflict_type.append("shouting")
            
            # Check for short, abrupt responses (potential dismissiveness)
            if len(msg.message.split()) <= 2 and i > 0:
                prev_msg = all_messages[i-1]
                if prev_msg.username != msg.username and len(prev_msg.message.split()) > 10:
                    conflict_score += 1
                    indicators.append(f"dismissive short response ('{msg.message}' to {len(prev_msg.message.split())} word message)")
                    conflict_type.append("dismissive")
            
            # Check for conversational imbalance (one-sided conversation)
            if i > 2:
                recent_senders = [all_messages[j].username for j in range(max(0, i-5), i+1) if all_messages[j].username in [user1_name, user2_name]]
                if len(recent_senders) >= 4 and len(set(recent_senders)) == 1:
                    conflict_score += 0.5
                    indicators.append("one-sided conversation (lack of engagement from other party)")
                    conflict_type.append("disengagement")
            
            if conflict_score >= 2:
                # Get context
                context_messages = []
                for j in range(max(0, i-2), min(len(all_messages), i+3)):
                    if all_messages[j].username in [user1_name, user2_name]:
                        context_messages.append({
                            'user': all_messages[j].username,
                            'message': all_messages[j].message[:150],
                            'is_conflict': j == i
                        })
                
                conflict_entry = {
                    'timestamp': msg.timestamp.isoformat(),
                    'date': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'user': msg.username,
                    'message': msg.message[:200],
                    'conflict_score': round(conflict_score, 1),
                    'conflict_types': list(set(conflict_type)),
                    'indicators': indicators,
                    'context': context_messages,
                    'reasoning': self._generate_conflict_reasoning(msg, indicators, conflict_type, context_messages)
                }
                
                potential_conflicts.append(conflict_entry)
                
                # Track topic disagreements
                for topic_type in conflict_type:
                    if topic_type not in topic_disagreements:
                        topic_disagreements[topic_type] = 0
                    topic_disagreements[topic_type] += 1
        
        # Analyze divergence sources
        if potential_conflicts:
            divergence_sources = self._analyze_divergence_sources(
                potential_conflicts, 
                topic_disagreements,
                user1_name,
                user2_name
            )
        
        return {
            'users': [user1_name, user2_name],
            'potential_conflicts_detected': len(potential_conflicts),
            'conflict_rate': round(len(potential_conflicts) / max(len(all_messages), 1) * 100, 2),
            'conflicts': sorted(potential_conflicts, key=lambda x: x['conflict_score'], reverse=True)[:15],  # Top 15
            'divergence_sources': divergence_sources,
            'conflict_type_breakdown': topic_disagreements,
            'health_score': max(0, 100 - len(potential_conflicts) * 2),
            'risk_level': self._calculate_risk_level(len(potential_conflicts), len(all_messages))
        }
    
    def _generate_conflict_reasoning(
        self,
        msg: ParsedMessage,
        indicators: List[str],
        conflict_types: List[str],
        context: List[Dict]
    ) -> str:
        """Generate human-readable reasoning for conflict detection."""
        reasoning_parts = []
        
        if 'disagreement' in conflict_types:
            reasoning_parts.append("Message contains direct disagreement language")
        if 'frustration' in conflict_types:
            reasoning_parts.append("Shows signs of frustration or exasperation")
        if 'defensive' in conflict_types:
            reasoning_parts.append("Defensive tone suggests pushback against previous statements")
        if 'emotional_intensity' in conflict_types:
            reasoning_parts.append("High emotional intensity indicated by punctuation")
        if 'shouting' in conflict_types:
            reasoning_parts.append("Excessive capitalization suggests raised voice/emphasis")
        if 'dismissive' in conflict_types:
            reasoning_parts.append("Short response to lengthy message indicates possible dismissiveness")
        if 'disengagement' in conflict_types:
            reasoning_parts.append("Lack of reciprocal engagement from conversation partner")
        
        base_reasoning = '. '.join(reasoning_parts)
        
        # Add evidence
        evidence = f". Evidence: {'; '.join(indicators[:3])}"
        
        return base_reasoning + evidence
    
    def _analyze_divergence_sources(
        self,
        conflicts: List[Dict],
        topic_breakdown: Dict[str, int],
        user1: str,
        user2: str
    ) -> List[Dict[str, Any]]:
        """Analyze and categorize sources of divergence between users."""
        sources = []
        
        # Most common conflict type
        if topic_breakdown:
            top_type = max(topic_breakdown.items(), key=lambda x: x[1])
            type_names = {
                'disagreement': 'Direct Disagreements',
                'frustration': 'Frustration & Impatience',
                'defensive': 'Defensive Communication',
                'negative': 'Negative Language Patterns',
                'emotional_intensity': 'Emotional Intensity',
                'confusion': 'Confusion or Misunderstanding',
                'shouting': 'Raised Voice/Emphasis',
                'dismissive': 'Dismissive Behavior',
                'disengagement': 'Lack of Engagement'
            }
            
            sources.append({
                'source': type_names.get(top_type[0], top_type[0].title()),
                'frequency': top_type[1],
                'severity': 'high' if top_type[1] >= 5 else 'medium' if top_type[1] >= 2 else 'low',
                'description': self._get_divergence_description(top_type[0]),
                'evidence_count': top_type[1],
                'recommendation': self._get_recommendation(top_type[0])
            })
        
        # Check for user-specific patterns
        user1_conflicts = [c for c in conflicts if c['user'] == user1]
        user2_conflicts = [c for c in conflicts if c['user'] == user2]
        
        if len(user1_conflicts) > len(user2_conflicts) * 2:
            sources.append({
                'source': f'{user1} Communication Style',
                'frequency': len(user1_conflicts),
                'severity': 'medium',
                'description': f'{user1} initiates most conflict-indicating messages, suggesting possible communication style mismatch',
                'evidence_count': len(user1_conflicts),
                'recommendation': f'{user1} may benefit from moderating tone and language patterns'
            })
        elif len(user2_conflicts) > len(user1_conflicts) * 2:
            sources.append({
                'source': f'{user2} Communication Style',
                'frequency': len(user2_conflicts),
                'severity': 'medium',
                'description': f'{user2} initiates most conflict-indicating messages, suggesting possible communication style mismatch',
                'evidence_count': len(user2_conflicts),
                'recommendation': f'{user2} may benefit from moderating tone and language patterns'
            })
        
        # Check for temporal patterns
        if len(conflicts) >= 3:
            timestamps = [datetime.fromisoformat(c['timestamp']) for c in conflicts]
            time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() / 3600 for i in range(1, len(timestamps))]
            avg_time_between = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            
            if avg_time_between < 24:  # Less than a day between conflicts
                sources.append({
                    'source': 'Frequent Tension',
                    'frequency': len(conflicts),
                    'severity': 'high',
                    'description': f'Conflicts occur frequently (avg {avg_time_between:.1f} hours apart), suggesting ongoing unresolved issues',
                    'evidence_count': len(conflicts),
                    'recommendation': 'Consider addressing underlying issues directly rather than letting tensions accumulate'
                })
        
        return sources
    
    def _get_divergence_description(self, conflict_type: str) -> str:
        """Get detailed description for conflict type."""
        descriptions = {
            'disagreement': 'Users frequently contradict each other directly, indicating differing viewpoints or opinions',
            'frustration': 'Messages show impatience or exasperation, suggesting unmet expectations or repeated issues',
            'defensive': 'Defensive language patterns indicate users feel the need to justify or protect their positions',
            'negative': 'Use of absolute negative terms (never/always) suggests polarized thinking or frustration',
            'emotional_intensity': 'High emotional intensity in messages indicates strong feelings about topics',
            'confusion': 'Multiple questions suggest misunderstanding or need for clarification',
            'shouting': 'Capitalization patterns indicate emphasis or raised voice tone',
            'dismissive': 'Short responses to detailed messages suggest lack of engagement or respect',
            'disengagement': 'One-sided conversation patterns indicate withdrawal from interaction'
        }
        return descriptions.get(conflict_type, 'Communication pattern that may indicate tension')
    
    def _get_recommendation(self, conflict_type: str) -> str:
        """Get recommendation for conflict type."""
        recommendations = {
            'disagreement': 'Practice active listening and acknowledge different perspectives before responding',
            'frustration': 'Take breaks when frustrated; address recurring issues directly rather than through hints',
            'defensive': 'Focus on understanding rather than defending; use "I feel" statements',
            'negative': 'Avoid absolute language; be specific about behaviors rather than character',
            'emotional_intensity': 'Allow time to cool down before responding to emotional topics',
            'confusion': 'Clarify expectations and meanings proactively; ask for confirmation of understanding',
            'shouting': 'Use emphasis sparingly; consider why you feel the need to raise your voice',
            'dismissive': 'Give thoughtful responses that match the effort of incoming messages',
            'disengagement': 'Ensure both parties have equal opportunity to participate; check in if someone seems withdrawn'
        }
        return recommendations.get(conflict_type, 'Improve communication patterns and mutual understanding')
    
    def _calculate_risk_level(self, conflict_count: int, total_messages: int) -> str:
        """Calculate overall risk level for the relationship."""
        if total_messages == 0:
            return 'unknown'
        
        conflict_rate = conflict_count / total_messages
        
        if conflict_rate >= 0.15:
            return 'high'
        elif conflict_rate >= 0.08:
            return 'medium'
        elif conflict_rate >= 0.03:
            return 'low'
        else:
            return 'minimal'
    
    def analyze_conversation_dynamics(
        self,
        all_messages: List[ParsedMessage],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of conversation dynamics.
        
        Args:
            all_messages: All messages from conversation
            user1_name: First user's name
            user2_name: Second user's name
            
        Returns:
            Comprehensive dynamics analysis
        """
        interaction_messages = [
            m for m in all_messages 
            if m.username in [user1_name, user2_name]
        ]
        
        # Who initiates conversations more
        initiations = {user1_name: 0, user2_name: 0}
        for i, msg in enumerate(interaction_messages):
            if i == 0 or (interaction_messages[i].timestamp - interaction_messages[i-1].timestamp).total_seconds() > 3600:
                # New conversation (1 hour gap)
                initiations[msg.username] += 1
        
        # Response times
        response_times = []
        for i in range(1, len(interaction_messages)):
            if interaction_messages[i].username != interaction_messages[i-1].username:
                time_diff = (interaction_messages[i].timestamp - interaction_messages[i-1].timestamp).total_seconds()
                if time_diff < 3600:  # Within 1 hour
                    response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Topic shifts (simple heuristic: very different message lengths)
        topic_shifts = 0
        for i in range(1, len(interaction_messages)):
            curr_len = len(interaction_messages[i].message.split())
            prev_len = len(interaction_messages[i-1].message.split())
            if abs(curr_len - prev_len) > 20:
                topic_shifts += 1
        
        return {
            'users': [user1_name, user2_name],
            'conversation_dynamics': {
                'initiations': initiations,
                'initiation_balance': round(min(initiations.values()) / max(initiations.values(), 1) * 100, 2),
                'avg_response_time_seconds': round(avg_response_time, 2),
                'avg_response_time_minutes': round(avg_response_time / 60, 2),
                'estimated_topic_shifts': topic_shifts,
                'engagement_score': round(min(100, len(response_times) / max(len(interaction_messages), 1) * 200), 2)
            }
        }
    
    def _generate_compatibility_insights(
        self,
        length_similarity: float,
        time_overlap: float,
        question_balance: float
    ) -> List[str]:
        """Generate human-readable compatibility insights."""
        insights = []
        
        if length_similarity > 0.8:
            insights.append("Both users have very similar message lengths - good communication sync!")
        elif length_similarity < 0.5:
            insights.append("Message length difference detected - one user tends to write longer messages")
        
        if time_overlap > 0.6:
            insights.append("High activity time overlap - both users are often online at the same times")
        elif time_overlap < 0.3:
            insights.append("Low activity overlap - users are active at different times")
        
        if question_balance > 0.7:
            insights.append("Balanced conversation - both users ask similar amounts of questions")
        elif question_balance < 0.4:
            insights.append("One user asks significantly more questions than the other")
        
        return insights
    
    def _generate_support_insights(
        self,
        support_scores: Dict[str, Dict],
        user1_name: str,
        user2_name: str
    ) -> List[str]:
        """Generate insights about emotional support patterns."""
        insights = []
        
        u1_total = sum(support_scores[user1_name].values())
        u2_total = sum(support_scores[user2_name].values())
        
        if u1_total > u2_total * 1.5:
            insights.append(f"{user1_name} provides more emotional support in the conversation")
        elif u2_total > u1_total * 1.5:
            insights.append(f"{user2_name} provides more emotional support in the conversation")
        else:
            insights.append("Both users provide balanced emotional support")
        
        # Check for specific support types
        for category in ['empathy', 'encouragement', 'help']:
            u1_score = support_scores[user1_name].get(category, 0)
            u2_score = support_scores[user2_name].get(category, 0)
            
            if u1_score + u2_score > 10:
                insights.append(f"Strong {category} present in conversations")
        
        return insights
