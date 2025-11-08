"""Advanced NLP analyzer for enhanced pattern extraction and style analysis.

Implements BERTopic, LDA, NER, sentiment analysis, personality insights,
readability metrics, and formality detection.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import logging

import numpy as np
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora
from gensim.models import LdaModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import textstat

from app.parser import ParsedMessage

logger = logging.getLogger(__name__)


class AdvancedNLPAnalyzer:
    """Advanced NLP analyzer for comprehensive message analysis."""
    
    def __init__(self):
        """Initialize the NLP analyzer."""
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Formality indicators
        self.formal_words = {
            'therefore', 'furthermore', 'however', 'nevertheless', 'consequently',
            'thus', 'hence', 'accordingly', 'moreover', 'indeed', 'regarding',
            'concerning', 'pursuant', 'aforementioned', 'hereby'
        }
        
        self.informal_words = {
            'yeah', 'nah', 'yep', 'nope', 'gonna', 'wanna', 'gotta',
            'kinda', 'sorta', 'dunno', 'ain\'t', 'y\'all', 'btw',
            'lol', 'omg', 'tbh', 'idk', 'imo', 'fyi'
        }
    
    def extract_topics_bertopic(
        self,
        messages: List[ParsedMessage],
        n_topics: int = 10
    ) -> Dict[str, Any]:
        """
        Extract topics using BERTopic.
        
        Args:
            messages: List of parsed messages
            n_topics: Number of topics to extract
            
        Returns:
            Dictionary with topics and their information
        """
        # Filter out media messages
        texts = [msg.message for msg in messages if not msg.is_media and len(msg.message) > 10]
        
        if len(texts) < 10:
            logger.warning("Not enough messages for BERTopic analysis")
            return {
                'topics': [],
                'method': 'bertopic',
                'message': 'Insufficient data for topic modeling'
            }
        
        try:
            # Create BERTopic model
            topic_model = BERTopic(
                nr_topics=min(n_topics, len(texts) // 2),
                calculate_probabilities=False,
                verbose=False
            )
            
            # Fit and transform
            topics, probs = topic_model.fit_transform(texts)
            
            # Get topic information
            topic_info = topic_model.get_topic_info()
            
            # Extract top topics
            topic_list = []
            for topic_id in range(min(n_topics, len(topic_info) - 1)):
                if topic_id == -1:  # Skip outlier topic
                    continue
                    
                words = topic_model.get_topic(topic_id)
                if words:
                    keywords = [word for word, _ in words[:5]]
                    doc_count = int(topic_info[topic_info['Topic'] == topic_id]['Count'].values[0])
                    # Create topic name from top keywords
                    topic_name = '_'.join(keywords[:3])
                    topic_list.append({
                        'topic': topic_name,
                        'keywords': keywords,
                        'score': float(doc_count) / len(texts),  # Normalized score
                        'document_count': doc_count
                    })
            
            logger.info(f"Extracted {len(topic_list)} topics using BERTopic")
            
            return {
                'topics': topic_list,
                'method': 'bertopic',
                'total_documents': len(texts),
                'n_topics': len(topic_list)
            }
            
        except Exception as e:
            logger.error(f"BERTopic analysis failed: {e}")
            return {
                'topics': [],
                'method': 'bertopic',
                'error': str(e)
            }
    
    def extract_topics_lda(
        self,
        messages: List[ParsedMessage],
        n_topics: int = 5
    ) -> Dict[str, Any]:
        """
        Extract topics using LDA (Latent Dirichlet Allocation).
        
        Args:
            messages: List of parsed messages
            n_topics: Number of topics to extract
            
        Returns:
            Dictionary with topics and their information
        """
        texts = [msg.message.lower() for msg in messages if not msg.is_media and len(msg.message) > 10]
        
        if len(texts) < 5:
            return {
                'topics': [],
                'method': 'lda',
                'message': 'Insufficient data for LDA'
            }
        
        try:
            # Tokenize
            tokenized_texts = [re.findall(r'\b\w{3,}\b', text) for text in texts]
            
            # Create dictionary and corpus
            dictionary = corpora.Dictionary(tokenized_texts)
            dictionary.filter_extremes(no_below=2, no_above=0.7)
            corpus = [dictionary.doc2bow(text) for text in tokenized_texts]
            
            # Train LDA model
            lda_model = LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=min(n_topics, len(texts) // 3),
                random_state=42,
                passes=10
            )
            
            # Extract topics
            topic_list = []
            for topic_id in range(lda_model.num_topics):
                words = lda_model.show_topic(topic_id, topn=5)
                keywords = [word for word, _ in words]
                weights = [float(weight) for _, weight in words]
                # Create topic name from top keywords
                topic_name = '_'.join(keywords[:3])
                topic_list.append({
                    'topic': topic_name,
                    'keywords': keywords,
                    'score': sum(weights) / len(weights),  # Average weight as score
                    'weights': weights
                })
            
            logger.info(f"Extracted {len(topic_list)} topics using LDA")
            
            return {
                'topics': topic_list,
                'method': 'lda',
                'total_documents': len(texts),
                'n_topics': len(topic_list)
            }
            
        except Exception as e:
            logger.error(f"LDA analysis failed: {e}")
            return {
                'topics': [],
                'method': 'lda',
                'error': str(e)
            }
    
    def analyze_sentiment_progression(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze sentiment progression over time.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Sentiment analysis with timeline
        """
        sentiment_timeline = []
        
        for msg in messages:
            if msg.is_media:
                continue
            
            scores = self.sentiment_analyzer.polarity_scores(msg.message)
            
            sentiment_timeline.append({
                'timestamp': msg.timestamp.isoformat(),
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'username': msg.username
            })
        
        if not sentiment_timeline:
            return {
                'timeline': [],
                'overall': {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 1}
            }
        
        # Calculate overall sentiment
        avg_compound = np.mean([s['compound'] for s in sentiment_timeline])
        avg_positive = np.mean([s['positive'] for s in sentiment_timeline])
        avg_negative = np.mean([s['negative'] for s in sentiment_timeline])
        avg_neutral = np.mean([s['neutral'] for s in sentiment_timeline])
        
        return {
            'timeline': sentiment_timeline,
            'overall': {
                'compound': float(avg_compound),
                'positive': float(avg_positive),
                'negative': float(avg_negative),
                'neutral': float(avg_neutral)
            },
            'sentiment_label': self._get_sentiment_label(avg_compound)
        }
    
    def _get_sentiment_label(self, compound: float) -> str:
        """Get sentiment label from compound score."""
        if compound >= 0.05:
            return 'positive'
        elif compound <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_personality_traits(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze personality traits based on linguistic patterns.
        
        Uses simple heuristics based on linguistic research (LIWC-inspired).
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Personality trait indicators
        """
        text_messages = [msg for msg in messages if not msg.is_media]
        combined_text = ' '.join([msg.message.lower() for msg in text_messages])
        words = re.findall(r'\b\w+\b', combined_text)
        
        if not words:
            return {'traits': {}, 'message': 'Insufficient data'}
        
        total_words = len(words)
        
        # First-person pronouns (I, me, my) - indicator of self-focus
        first_person = len([w for w in words if w in ['i', 'me', 'my', 'mine', 'myself']])
        
        # Social words (we, us, they) - indicator of social orientation
        social_words = len([w for w in words if w in ['we', 'us', 'our', 'they', 'them', 'their']])
        
        # Positive emotion words
        positive_words = len([w for w in words if w in [
            'happy', 'good', 'great', 'love', 'nice', 'awesome', 'excellent',
            'wonderful', 'amazing', 'fantastic', 'perfect', 'best'
        ]])
        
        # Negative emotion words
        negative_words = len([w for w in words if w in [
            'bad', 'sad', 'hate', 'terrible', 'awful', 'worst', 'horrible',
            'angry', 'upset', 'annoyed', 'frustrated'
        ]])
        
        # Cognitive words (think, know, understand)
        cognitive_words = len([w for w in words if w in [
            'think', 'know', 'understand', 'believe', 'consider', 'realize',
            'recognize', 'wonder', 'suppose', 'assume'
        ]])
        
        # Calculate percentages
        traits = {
            'self_focus': (first_person / total_words) * 100,
            'social_orientation': (social_words / total_words) * 100,
            'positive_emotion': (positive_words / total_words) * 100,
            'negative_emotion': (negative_words / total_words) * 100,
            'analytical_thinking': (cognitive_words / total_words) * 100,
            'total_words': total_words
        }
        
        # Interpretations
        interpretations = {
            'self_focus': 'high' if traits['self_focus'] > 5 else 'moderate' if traits['self_focus'] > 2 else 'low',
            'social_orientation': 'high' if traits['social_orientation'] > 3 else 'moderate' if traits['social_orientation'] > 1 else 'low',
            'emotional_positivity': 'positive' if traits['positive_emotion'] > traits['negative_emotion'] else 'negative' if traits['negative_emotion'] > traits['positive_emotion'] else 'neutral',
            'analytical_thinking': 'high' if traits['analytical_thinking'] > 4 else 'moderate' if traits['analytical_thinking'] > 2 else 'low'
        }
        
        return {
            'traits': traits,
            'interpretations': interpretations,
            'total_words_analyzed': total_words
        }
    
    def analyze_readability(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze readability and writing complexity.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Readability metrics
        """
        text_messages = [msg.message for msg in messages if not msg.is_media and len(msg.message) > 10]
        
        if not text_messages:
            return {'metrics': {}, 'message': 'Insufficient data'}
        
        combined_text = ' '.join(text_messages)
        
        try:
            metrics = {
                'flesch_reading_ease': textstat.flesch_reading_ease(combined_text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(combined_text),
                'gunning_fog': textstat.gunning_fog(combined_text),
                'smog_index': textstat.smog_index(combined_text),
                'avg_sentence_length': textstat.avg_sentence_length(combined_text),
                'avg_syllables_per_word': textstat.avg_syllables_per_word(combined_text),
                'lexicon_count': textstat.lexicon_count(combined_text),
            }
            
            # Interpretation
            fre = metrics['flesch_reading_ease']
            if fre >= 90:
                difficulty = 'Very Easy'
            elif fre >= 80:
                difficulty = 'Easy'
            elif fre >= 70:
                difficulty = 'Fairly Easy'
            elif fre >= 60:
                difficulty = 'Standard'
            elif fre >= 50:
                difficulty = 'Fairly Difficult'
            elif fre >= 30:
                difficulty = 'Difficult'
            else:
                difficulty = 'Very Difficult'
            
            return {
                'metrics': metrics,
                'difficulty_level': difficulty,
                'grade_level': f"Grade {int(metrics['flesch_kincaid_grade'])}"
            }
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return {'metrics': {}, 'error': str(e)}
    
    def analyze_formality(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Analyze formality level of communication.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Formality analysis
        """
        text_messages = [msg for msg in messages if not msg.is_media]
        combined_text = ' '.join([msg.message.lower() for msg in text_messages])
        words = re.findall(r'\b\w+\b', combined_text)
        
        if not words:
            return {'formality_score': 0, 'level': 'unknown'}
        
        formal_count = sum(1 for word in words if word in self.formal_words)
        informal_count = sum(1 for word in words if word in self.informal_words)
        
        # Count contractions
        contractions = len(re.findall(r"\w+'\w+", combined_text))
        
        # Count punctuation indicators
        exclamations = combined_text.count('!')
        questions = combined_text.count('?')
        
        # Calculate formality score (0-100)
        total_indicators = formal_count + informal_count + contractions + (exclamations // 2) + 1
        formality_score = ((formal_count * 100) - (informal_count * 50) - (contractions * 10) - (exclamations * 5)) / total_indicators
        
        # Normalize to 0-100
        formality_score = max(0, min(100, 50 + formality_score))
        
        # Determine level
        if formality_score >= 70:
            level = 'Very Formal'
        elif formality_score >= 55:
            level = 'Formal'
        elif formality_score >= 45:
            level = 'Neutral'
        elif formality_score >= 30:
            level = 'Informal'
        else:
            level = 'Very Informal'
        
        return {
            'formality_score': float(formality_score),
            'level': level,
            'indicators': {
                'formal_words': formal_count,
                'informal_words': informal_count,
                'contractions': contractions,
                'exclamations': exclamations,
                'questions': questions
            }
        }
    
    def analyze_comprehensive(
        self,
        messages: List[ParsedMessage]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining all methods.
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting comprehensive analysis of {len(messages)} messages")
        
        return {
            'sentiment': self.analyze_sentiment_progression(messages),
            'personality': self.analyze_personality_traits(messages),
            'readability': self.analyze_readability(messages),
            'formality': self.analyze_formality(messages),
            'topics_lda': self.extract_topics_lda(messages),
            'topics_bertopic': self.extract_topics_bertopic(messages)
        }
