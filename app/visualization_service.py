"""Visualization service for generating chart data.

Creates Plotly-compatible JSON for frontend visualization.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VisualizationService:
    """Service for generating visualization data."""
    
    def create_sentiment_timeline_chart(
        self,
        sentiment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create sentiment timeline chart data.
        
        Args:
            sentiment_data: Sentiment analysis data with timeline
            
        Returns:
            Plotly-compatible chart data
        """
        from datetime import datetime
        from collections import defaultdict
        
        timeline = sentiment_data.get('timeline', [])
        
        if not timeline:
            return {'data': [], 'layout': {}}
        
        # Group by user and date (day)
        users_by_date = defaultdict(lambda: defaultdict(list))
        
        for entry in timeline:
            username = entry['username']
            # Parse timestamp and extract date
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            date = timestamp.date().isoformat()  # Get YYYY-MM-DD
            
            users_by_date[username][date].append(entry['compound'])
        
        # Aggregate by day (average sentiment per day)
        users = {}
        for username, dates in users_by_date.items():
            users[username] = {'x': [], 'y': [], 'name': username}
            
            # Sort by date
            sorted_dates = sorted(dates.items())
            
            for date, sentiments in sorted_dates:
                avg_sentiment = sum(sentiments) / len(sentiments)
                users[username]['x'].append(date)
                users[username]['y'].append(avg_sentiment)
        
        # Create traces
        traces = []
        for username, data in users.items():
            traces.append({
                'x': data['x'],
                'y': data['y'],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': username,
                'line': {'shape': 'spline', 'width': 2},
                'marker': {'size': 8}
            })
        
        layout = {
            'title': 'Sentiment Progression Over Time',
            'xaxis': {'title': 'Time', 'type': 'date'},
            'yaxis': {'title': 'Sentiment Score', 'range': [-1, 1]},
            'hovermode': 'closest'
        }
        
        return {
            'data': traces,
            'layout': layout
        }
    
    def create_topic_distribution_chart(
        self,
        topics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create topic distribution chart data.
        
        Args:
            topics_data: Topic analysis data
            
        Returns:
            Plotly-compatible chart data
        """
        topics = topics_data.get('topics', [])
        
        if not topics:
            return {'data': [], 'layout': {}}
        
        # Extract topic labels and counts
        labels = []
        values = []
        
        for topic in topics:
            if 'keywords' in topic:
                label = ', '.join(topic['keywords'][:3])
                labels.append(label)
                values.append(topic.get('document_count', topic.get('weights', [1])[0] * 100))
        
        trace = {
            'type': 'bar',
            'x': labels,
            'y': values,
            'marker': {'color': 'rgb(55, 83, 109)'}
        }
        
        layout = {
            'title': f'Topic Distribution ({topics_data.get("method", "").upper()})',
            'xaxis': {'title': 'Topics'},
            'yaxis': {'title': 'Relevance/Count'},
            'margin': {'b': 150}
        }
        
        return {
            'data': [trace],
            'layout': layout
        }
    
    def create_personality_radar_chart(
        self,
        personality_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create personality traits radar chart.
        
        Args:
            personality_data: Personality analysis data
            
        Returns:
            Plotly-compatible chart data
        """
        traits = personality_data.get('traits', {})
        
        if not traits:
            return {'data': [], 'layout': {}}
        
        categories = [
            'Self Focus',
            'Social Orientation',
            'Positive Emotion',
            'Negative Emotion',
            'Analytical Thinking'
        ]
        
        values = [
            traits.get('self_focus', 0),
            traits.get('social_orientation', 0),
            traits.get('positive_emotion', 0),
            traits.get('negative_emotion', 0),
            traits.get('analytical_thinking', 0)
        ]
        
        trace = {
            'type': 'scatterpolar',
            'r': values,
            'theta': categories,
            'fill': 'toself',
            'name': 'Personality Traits'
        }
        
        layout = {
            'polar': {
                'radialaxis': {
                    'visible': True,
                    'range': [0, max(values) * 1.2 if values else 10]
                }
            },
            'title': 'Personality Trait Analysis'
        }
        
        return {
            'data': [trace],
            'layout': layout
        }
    
    def create_activity_heatmap(
        self,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create activity heatmap by hour and day.
        
        Args:
            activity_data: Activity pattern data
            
        Returns:
            Plotly-compatible chart data
        """
        hourly = activity_data.get('hourly_distribution', [])
        
        if not hourly:
            return {'data': [], 'layout': {}}
        
        hours = [entry['hour'] for entry in hourly]
        counts = [entry['count'] for entry in hourly]
        
        trace = {
            'type': 'bar',
            'x': hours,
            'y': counts,
            'marker': {'color': counts, 'colorscale': 'Viridis'}
        }
        
        layout = {
            'title': 'Activity by Hour of Day',
            'xaxis': {'title': 'Hour (24h format)', 'dtick': 1},
            'yaxis': {'title': 'Message Count'},
            'bargap': 0.1
        }
        
        return {
            'data': [trace],
            'layout': layout
        }
    
    def create_response_time_distribution(
        self,
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create response time distribution chart.
        
        Args:
            response_data: Response time analysis data
            
        Returns:
            Plotly-compatible chart data
        """
        by_user = response_data.get('by_user', {})
        
        if not by_user:
            return {'data': [], 'layout': {}}
        
        users = list(by_user.keys())
        avg_times = [by_user[user]['average_seconds'] / 60 for user in users]  # Convert to minutes
        
        trace = {
            'type': 'bar',
            'x': users,
            'y': avg_times,
            'marker': {'color': 'rgb(158, 202, 225)'}
        }
        
        layout = {
            'title': 'Average Response Time by User',
            'xaxis': {'title': 'User'},
            'yaxis': {'title': 'Average Response Time (minutes)'}
        }
        
        return {
            'data': [trace],
            'layout': layout
        }
    
    def create_message_length_distribution(
        self,
        length_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create message length distribution chart.
        
        Args:
            length_data: Message length analysis data
            
        Returns:
            Plotly-compatible chart data
        """
        distribution = length_data.get('distribution', {})
        
        if not distribution:
            return {'data': [], 'layout': {}}
        
        categories = ['Short (<50)', 'Medium (50-150)', 'Long (>150)']
        values = [
            distribution.get('short', 0),
            distribution.get('medium', 0),
            distribution.get('long', 0)
        ]
        
        trace = {
            'type': 'pie',
            'labels': categories,
            'values': values,
            'hole': 0.4
        }
        
        layout = {
            'title': 'Message Length Distribution'
        }
        
        return {
            'data': [trace],
            'layout': layout
        }
    
    def create_formality_gauge(
        self,
        formality_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create formality level gauge chart.
        
        Args:
            formality_data: Formality analysis data
            
        Returns:
            Plotly-compatible chart data
        """
        score = formality_data.get('formality_score', 50)
        level = formality_data.get('level', 'Neutral')
        
        trace = {
            'type': 'indicator',
            'mode': 'gauge+number+delta',
            'value': score,
            'title': {'text': f'Formality Level: {level}'},
            'gauge': {
                'axis': {'range': [0, 100]},
                'bar': {'color': 'darkblue'},
                'steps': [
                    {'range': [0, 30], 'color': 'lightcoral'},
                    {'range': [30, 45], 'color': 'lightyellow'},
                    {'range': [45, 55], 'color': 'lightgreen'},
                    {'range': [55, 70], 'color': 'lightblue'},
                    {'range': [70, 100], 'color': 'darkblue'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        }
        
        layout = {
            'title': 'Communication Formality Level'
        }
        
        return {
            'data': [trace],
            'layout': layout
        }
    
    def create_network_graph(
        self,
        graph_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create network graph visualization.
        
        Args:
            graph_data: Graph structure with nodes and edges
            
        Returns:
            Plotly-compatible network graph data
        """
        import networkx as nx
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        if not nodes:
            return {'data': [], 'layout': {}}
        
        # Create NetworkX graph for layout calculation
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node['id'], **node)
        
        # Add edges
        for edge in edges:
            G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1))
        
        # Calculate layout using spring layout
        try:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        except:
            # Fallback to simple circular layout
            pos = nx.circular_layout(G)
        
        # Create edge traces
        edge_trace = {
            'x': [],
            'y': [],
            'mode': 'lines',
            'line': {'width': 0.5, 'color': '#888'},
            'hoverinfo': 'none',
            'showlegend': False
        }
        
        # Add edges
        for edge in edges:
            source = edge['source']
            target = edge['target']
            if source in pos and target in pos:
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                edge_trace['x'].extend([x0, x1, None])
                edge_trace['y'].extend([y0, y1, None])
        
        # Create node traces (separate for users and topics)
        user_trace = {
            'x': [],
            'y': [],
            'mode': 'markers+text',
            'marker': {
                'size': [],
                'color': '#FF6B6B',
                'line': {'width': 2, 'color': 'white'}
            },
            'text': [],
            'textposition': 'top center',
            'hoverinfo': 'text',
            'hovertext': [],
            'name': 'Users',
            'showlegend': True
        }
        
        topic_trace = {
            'x': [],
            'y': [],
            'mode': 'markers+text',
            'marker': {
                'size': [],
                'color': '#4ECDC4',
                'line': {'width': 2, 'color': 'white'}
            },
            'text': [],
            'textposition': 'top center',
            'hoverinfo': 'text',
            'hovertext': [],
            'name': 'Topics',
            'showlegend': True
        }
        
        # Add nodes
        for node in nodes:
            node_id = node['id']
            if node_id not in pos:
                continue
                
            x, y = pos[node_id]
            
            if node['type'] == 'user':
                user_trace['x'].append(x)
                user_trace['y'].append(y)
                user_trace['marker']['size'].append(node.get('size', 20))
                user_trace['text'].append(node.get('label', ''))
                user_trace['hovertext'].append(f"{node['label']}<br>Messages: {node.get('value', 0)}")
            else:  # topic
                topic_trace['x'].append(x)
                topic_trace['y'].append(y)
                topic_trace['marker']['size'].append(node.get('size', 15))
                topic_trace['text'].append(node.get('label', ''))
                topic_trace['hovertext'].append(f"Topic: {node['label']}<br>Frequency: {node.get('value', 0)}")
        
        layout = {
            'title': 'Conversation Network: Users & Topics',
            'showlegend': True,
            'hovermode': 'closest',
            'xaxis': {
                'showgrid': False, 
                'zeroline': False, 
                'showticklabels': False,
                'title': ''
            },
            'yaxis': {
                'showgrid': False, 
                'zeroline': False, 
                'showticklabels': False,
                'title': ''
            },
            'plot_bgcolor': 'rgba(240,240,240,0.9)',
            'paper_bgcolor': 'white',
            'margin': {'t': 50, 'b': 10, 'l': 10, 'r': 10}
        }
        
        return {
            'data': [edge_trace, user_trace, topic_trace],
            'layout': layout
        }
