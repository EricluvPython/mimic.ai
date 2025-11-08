"""Conversation pattern analyzer for analyzing interaction dynamics."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import logging

from app.parser import ParsedMessage

logger = logging.getLogger(__name__)


class ConversationPatternAnalyzer:
    """Analyzer for conversation patterns and interaction dynamics."""
    
    def analyze_response_times(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze response time patterns.
        
        Args:
            messages: List of parsed messages sorted by timestamp
            
        Returns:
            Response time statistics
        """
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda m: m.timestamp)
        
        response_times = []
        user_response_times = defaultdict(list)
        
        for i in range(1, len(sorted_messages)):
            prev_msg = sorted_messages[i - 1]
            curr_msg = sorted_messages[i]
            
            # Skip if same user (not a response)
            if prev_msg.username == curr_msg.username:
                continue
            
            # Calculate time difference
            time_diff = (curr_msg.timestamp - prev_msg.timestamp).total_seconds()
            
            # Only consider responses within 24 hours
            if time_diff <= 86400:  # 24 hours
                response_times.append(time_diff)
                user_response_times[curr_msg.username].append(time_diff)
        
        if not response_times:
            return {
                'average_response_time': 0,
                'median_response_time': 0,
                'by_user': {}
            }
        
        import numpy as np
        
        # Overall statistics
        avg_response = np.mean(response_times)
        median_response = np.median(response_times)
        
        # Per-user statistics
        user_stats = {}
        for user, times in user_response_times.items():
            if times:
                user_stats[user] = {
                    'average_seconds': float(np.mean(times)),
                    'median_seconds': float(np.median(times)),
                    'average_readable': self._format_time(np.mean(times)),
                    'count': len(times)
                }
        
        return {
            'average_response_time': float(avg_response),
            'median_response_time': float(median_response),
            'average_readable': self._format_time(avg_response),
            'median_readable': self._format_time(median_response),
            'total_responses': len(response_times),
            'by_user': user_stats
        }
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into readable time string."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours"
        else:
            return f"{int(seconds / 86400)} days"
    
    def analyze_conversation_flow(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze conversation flow and turn-taking patterns.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Conversation flow analysis
        """
        sorted_messages = sorted(messages, key=lambda m: m.timestamp)
        
        # Track consecutive messages
        turn_lengths = []
        current_user = None
        current_turn_length = 0
        user_turns = defaultdict(list)
        
        for msg in sorted_messages:
            if msg.username == current_user:
                current_turn_length += 1
            else:
                if current_user is not None:
                    turn_lengths.append(current_turn_length)
                    user_turns[current_user].append(current_turn_length)
                current_user = msg.username
                current_turn_length = 1
        
        # Add last turn
        if current_user is not None:
            turn_lengths.append(current_turn_length)
            user_turns[current_user].append(current_turn_length)
        
        if not turn_lengths:
            return {'average_turn_length': 0, 'by_user': {}}
        
        import numpy as np
        
        # Overall statistics
        avg_turn = np.mean(turn_lengths)
        
        # Per-user statistics
        user_stats = {}
        for user, turns in user_turns.items():
            user_stats[user] = {
                'average_turn_length': float(np.mean(turns)),
                'max_turn_length': int(np.max(turns)),
                'total_turns': len(turns)
            }
        
        return {
            'average_turn_length': float(avg_turn),
            'total_turns': len(turn_lengths),
            'by_user': user_stats
        }
    
    def analyze_question_patterns(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze question asking patterns.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Question pattern analysis
        """
        total_messages = len([m for m in messages if not m.is_media])
        user_questions = defaultdict(int)
        user_message_count = defaultdict(int)
        
        question_words = {'what', 'where', 'when', 'why', 'who', 'how', 'which', 'whose'}
        
        for msg in messages:
            if msg.is_media:
                continue
            
            user_message_count[msg.username] += 1
            
            # Check for question marks
            has_question_mark = '?' in msg.message
            
            # Check for question words at start
            words = msg.message.lower().split()
            starts_with_question = words and words[0] in question_words
            
            if has_question_mark or starts_with_question:
                user_questions[msg.username] += 1
        
        # Calculate percentages
        user_stats = {}
        for user in user_message_count:
            total = user_message_count[user]
            questions = user_questions[user]
            user_stats[user] = {
                'question_count': questions,
                'total_messages': total,
                'question_percentage': (questions / total * 100) if total > 0 else 0
            }
        
        total_questions = sum(user_questions.values())
        
        return {
            'total_questions': total_questions,
            'total_messages': total_messages,
            'question_percentage': (total_questions / total_messages * 100) if total_messages > 0 else 0,
            'by_user': user_stats
        }
    
    def analyze_activity_patterns(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze activity patterns by time of day and day of week.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Activity pattern analysis
        """
        hour_distribution = defaultdict(int)
        day_distribution = defaultdict(int)
        user_hour_distribution = defaultdict(lambda: defaultdict(int))
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for msg in messages:
            hour = msg.timestamp.hour
            day = days[msg.timestamp.weekday()]
            
            hour_distribution[hour] += 1
            day_distribution[day] += 1
            user_hour_distribution[msg.username][hour] += 1
        
        # Find peak hours
        if hour_distribution:
            peak_hour = max(hour_distribution.items(), key=lambda x: x[1])[0]
            peak_day = max(day_distribution.items(), key=lambda x: x[1])[0]
        else:
            peak_hour = 0
            peak_day = 'Unknown'
        
        # Convert to sorted lists for visualization
        hour_data = [{'hour': h, 'count': hour_distribution[h]} for h in range(24)]
        day_data = [{'day': day, 'count': day_distribution[day]} for day in days]
        
        # Per-user peak hours
        user_peak_hours = {}
        for user, hours in user_hour_distribution.items():
            if hours:
                user_peak_hours[user] = max(hours.items(), key=lambda x: x[1])[0]
        
        return {
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'hourly_distribution': hour_data,
            'daily_distribution': day_data,
            'user_peak_hours': user_peak_hours
        }
    
    def analyze_message_length_patterns(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze message length patterns.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Message length analysis
        """
        text_messages = [msg for msg in messages if not msg.is_media]
        
        if not text_messages:
            return {'average_length': 0, 'by_user': {}}
        
        import numpy as np
        
        lengths = [len(msg.message) for msg in text_messages]
        user_lengths = defaultdict(list)
        
        for msg in text_messages:
            user_lengths[msg.username].append(len(msg.message))
        
        # Overall statistics
        avg_length = np.mean(lengths)
        median_length = np.median(lengths)
        
        # Categorize messages
        short = sum(1 for l in lengths if l < 50)
        medium = sum(1 for l in lengths if 50 <= l < 150)
        long = sum(1 for l in lengths if l >= 150)
        
        # Per-user statistics
        user_stats = {}
        for user, user_lens in user_lengths.items():
            user_stats[user] = {
                'average_length': float(np.mean(user_lens)),
                'median_length': float(np.median(user_lens)),
                'min_length': int(np.min(user_lens)),
                'max_length': int(np.max(user_lens)),
                'total_messages': len(user_lens)
            }
        
        return {
            'average_length': float(avg_length),
            'median_length': float(median_length),
            'distribution': {
                'short': short,
                'medium': medium,
                'long': long
            },
            'by_user': user_stats
        }
    
    def analyze_comprehensive(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive conversation pattern analysis.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Complete conversation analysis
        """
        logger.info(f"Analyzing conversation patterns for {len(messages)} messages")
        
        return {
            'response_times': self.analyze_response_times(messages),
            'conversation_flow': self.analyze_conversation_flow(messages),
            'question_patterns': self.analyze_question_patterns(messages),
            'activity_patterns': self.analyze_activity_patterns(messages),
            'message_lengths': self.analyze_message_length_patterns(messages)
        }
