"""
Test script for visualization endpoints.

Fetches data from all visualization endpoints and generates interactive
HTML files with Plotly charts that you can open in your browser.
"""

import httpx
import json
from pathlib import Path
import asyncio


BASE_URL = "http://localhost:8000"
OUTPUT_DIR = Path("visualizations_output")


async def fetch_endpoint(client: httpx.AsyncClient, endpoint: str, description: str):
    """Fetch data from an endpoint."""
    print(f"📊 Fetching: {description}")
    print(f"   URL: {BASE_URL}{endpoint}")
    
    try:
        response = await client.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        data = response.json()
        print(f"   ✅ Success\n")
        return data
    except httpx.HTTPError as e:
        print(f"   ❌ Error: {e}\n")
        return None


def create_html_chart(chart_data: dict, title: str, filename: str):
    """Create an HTML file with a Plotly chart."""
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}
        #chart {{
            width: 100%;
            height: 600px;
        }}
        .data-section {{
            margin-top: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .data-section h2 {{
            margin-top: 0;
            color: #333;
        }}
        pre {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="subtitle">Interactive visualization from Mimic.AI backend</p>
        
        <div id="chart"></div>
        
        <div class="data-section">
            <h2>📊 Raw Data</h2>
            <pre>{json.dumps(chart_data.get('analysis', chart_data), indent=2)}</pre>
        </div>
    </div>
    
    <script>
        var data = {json.dumps(chart_data.get('chart', {}).get('data', []))};
        var layout = {json.dumps(chart_data.get('chart', {}).get('layout', {}))};
        
        // Ensure layout has responsive sizing
        layout.autosize = true;
        layout.margin = layout.margin || {{}};
        
        Plotly.newPlot('chart', data, layout, {{responsive: true}});
    </script>
</body>
</html>"""
    
    output_path = OUTPUT_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"   💾 Saved: {output_path}")


def create_index_html(visualizations: list):
    """Create an index page linking to all visualizations."""
    
    links_html = "\n".join([
        f'<li><a href="{viz["file"]}">{viz["title"]}</a> - {viz["description"]}</li>'
        for viz in visualizations
    ])
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mimic.AI Visualizations</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 40px;
            font-size: 1.2em;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        li:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        a {{
            text-decoration: none;
            color: #667eea;
            font-weight: 600;
            font-size: 1.1em;
        }}
        a:hover {{
            color: #764ba2;
        }}
        .description {{
            color: #666;
            margin-left: 10px;
            font-weight: normal;
            font-size: 0.9em;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
        }}
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Mimic.AI Visualizations</h1>
        <p class="subtitle">Interactive charts and analysis from your WhatsApp data</p>
        
        <ul>
            {links_html}
        </ul>
        
        <div class="footer">
            <p>Generated from Mimic.AI Backend | {len(visualizations)} visualizations available</p>
        </div>
    </div>
</body>
</html>"""
    
    index_path = OUTPUT_DIR / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return index_path


async def main():
    """Main test function."""
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("🎨 MIMIC.AI VISUALIZATION TEST SCRIPT")
    print("=" * 70)
    print()
    
    # First, check if server is running
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            print("✅ Server is running\n")
        except httpx.ConnectError:
            print("❌ Error: Server is not running!")
            print("   Please start the server with: python -m app.main")
            return
        
        # Get list of users first
        print("📋 Getting list of users...")
        users_response = await client.get(f"{BASE_URL}/users")
        users_data = users_response.json()
        users = users_data.get('users', [])
        print(f"   Found {len(users)} users: {', '.join(users)}\n")
        
        if not users:
            print("❌ No users found! Please upload a chat file first.")
            return
        
        # Use first user for user-specific visualizations
        test_user = users[0]
        print(f"🎯 Using '{test_user}' for user-specific visualizations\n")
        print("=" * 70)
        print()
        
        visualizations = []
        
        # 1. Network Graph
        print("1️⃣  NETWORK GRAPH VISUALIZATION")
        print("-" * 70)
        data = await fetch_endpoint(client, "/visualize/graph", "User-Topic Network Graph")
        if data:
            create_html_chart(data, "Network Graph - Users & Topics", "01_network_graph.html")
            visualizations.append({
                "title": "Network Graph",
                "file": "01_network_graph.html",
                "description": "Relationships between users and topics"
            })
        print()
        
        # 2. Sentiment Timeline
        print("2️⃣  SENTIMENT ANALYSIS")
        print("-" * 70)
        data = await fetch_endpoint(client, f"/visualize/sentiment/{test_user}", "Sentiment Timeline")
        if data:
            create_html_chart(data, f"Sentiment Timeline - {test_user}", "02_sentiment_timeline.html")
            visualizations.append({
                "title": "Sentiment Timeline",
                "file": "02_sentiment_timeline.html",
                "description": f"Emotional progression for {test_user}"
            })
        print()
        
        # 3. Topics (LDA)
        print("3️⃣  TOPIC MODELING (LDA)")
        print("-" * 70)
        data = await fetch_endpoint(client, "/visualize/topics?method=lda", "Topic Distribution (LDA)")
        if data:
            create_html_chart(data, "Topic Distribution - LDA Method", "03_topics_lda.html")
            visualizations.append({
                "title": "Topic Distribution (LDA)",
                "file": "03_topics_lda.html",
                "description": "Statistical topic extraction"
            })
        print()
        
        # 4. Topics (BERTopic)
        print("4️⃣  TOPIC MODELING (BERTopic)")
        print("-" * 70)
        data = await fetch_endpoint(client, "/visualize/topics?method=bertopic", "Topic Distribution (BERTopic)")
        if data:
            create_html_chart(data, "Topic Distribution - BERTopic Method", "04_topics_bertopic.html")
            visualizations.append({
                "title": "Topic Distribution (BERTopic)",
                "file": "04_topics_bertopic.html",
                "description": "Advanced transformer-based topics"
            })
        print()
        
        # 5. Personality Analysis
        print("5️⃣  PERSONALITY ANALYSIS")
        print("-" * 70)
        data = await fetch_endpoint(client, f"/visualize/personality/{test_user}", "Personality Traits")
        if data:
            create_html_chart(data, f"Personality Traits - {test_user}", "05_personality_radar.html")
            visualizations.append({
                "title": "Personality Traits",
                "file": "05_personality_radar.html",
                "description": f"Linguistic personality analysis for {test_user}"
            })
        print()
        
        # 6. Conversation Patterns
        print("6️⃣  CONVERSATION PATTERNS")
        print("-" * 70)
        data = await fetch_endpoint(client, "/visualize/patterns", "Conversation Pattern Analysis")
        if data:
            # Create multiple charts for different aspects
            
            # Response Times
            response_time_data = {
                'chart': data.get('response_times', {}).get('chart', {}),
                'analysis': data.get('response_times', {}).get('analysis', {})
            }
            create_html_chart(response_time_data, "Response Time Analysis", "06a_response_times.html")
            visualizations.append({
                "title": "Response Times",
                "file": "06a_response_times.html",
                "description": "Average response time by user"
            })
            
            # Activity Heatmap
            activity_data = {
                'chart': data.get('activity', {}).get('chart', {}),
                'analysis': data.get('activity', {}).get('analysis', {})
            }
            create_html_chart(activity_data, "Activity Patterns by Hour", "06b_activity_heatmap.html")
            visualizations.append({
                "title": "Activity Heatmap",
                "file": "06b_activity_heatmap.html",
                "description": "Message activity by hour of day"
            })
            
            # Message Lengths
            length_data = {
                'chart': data.get('message_lengths', {}).get('chart', {}),
                'analysis': data.get('message_lengths', {}).get('analysis', {})
            }
            create_html_chart(length_data, "Message Length Distribution", "06c_message_lengths.html")
            visualizations.append({
                "title": "Message Length Distribution",
                "file": "06c_message_lengths.html",
                "description": "Distribution of message lengths"
            })
        print()
        
        # 7. Formality Analysis
        print("7️⃣  FORMALITY ANALYSIS")
        print("-" * 70)
        data = await fetch_endpoint(client, f"/visualize/formality/{test_user}", "Formality Level")
        if data:
            create_html_chart(data, f"Formality Level - {test_user}", "07_formality_gauge.html")
            visualizations.append({
                "title": "Formality Level",
                "file": "07_formality_gauge.html",
                "description": f"Communication formality for {test_user}"
            })
        print()
        
        # 8. Conversation Suggestions
        print("9️⃣  CONVERSATION SUGGESTIONS")
        print("-" * 70)
        suggestions_data = await fetch_endpoint(client, f"/suggestions/starters/{test_user}", "Conversation Starters")
        if suggestions_data and suggestions_data.get('suggestions'):
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Conversation Suggestions - {test_user}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .subtitle {{ color: #666; margin-bottom: 40px; font-size: 14px; }}
        .suggestion {{ margin: 20px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 8px; transition: transform 0.2s; }}
        .suggestion:hover {{ transform: translateX(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .suggestion-type {{ display: inline-block; padding: 4px 12px; background: #667eea; color: white; border-radius: 12px; font-size: 12px; font-weight: bold; margin-bottom: 10px; }}
        .starter-text {{ font-size: 18px; font-weight: 600; color: #333; margin: 10px 0; }}
        .reasoning {{ color: #666; font-size: 14px; margin: 10px 0; }}
        .confidence {{ display: inline-block; padding: 2px 8px; background: #28a745; color: white; border-radius: 4px; font-size: 12px; }}
        .stats {{ margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>💡 Conversation Suggestions</h1>
        <p class="subtitle">AI-generated conversation starters for {test_user}</p>
        {''.join([f'<div class="suggestion"><span class="suggestion-type">{s["type"].replace("_", " ").title()}</span><div class="starter-text">"{s["starter"]}"</div><div class="reasoning">💭 {s["reasoning"]}</div><span class="confidence">Confidence: {int(s["confidence"] * 100)}%</span></div>' for s in suggestions_data['suggestions']])}
        <div class="stats"><strong>Analysis Stats:</strong><br>Total Messages Analyzed: {suggestions_data.get('total_analyzed_messages', 0)}<br>Recent Messages: {suggestions_data.get('recent_messages_count', 0)}</div>
    </div>
</body>
</html>"""
            output_path = OUTPUT_DIR / "09_conversation_suggestions.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   💾 Saved: {output_path}")
            visualizations.append({"title": "Conversation Suggestions", "file": "09_conversation_suggestions.html", "description": f"AI starters for {test_user}"})
        print()
        
        # 9. Relationship Insights
        print("🔟 RELATIONSHIP INSIGHTS")
        print("-" * 70)
        users_response = await fetch_endpoint(client, "/users", "Available Users")
        if users_response and users_response.get('users') and len(users_response['users']) >= 2:
            user1, user2 = users_response['users'][0], users_response['users'][1]
            compat_data = await fetch_endpoint(client, f"/insights/compatibility/{user1}/{user2}", f"Compatibility: {user1} & {user2}")
            dynamics_data = await fetch_endpoint(client, f"/insights/dynamics/{user1}/{user2}", f"Dynamics: {user1} & {user2}")
            conflicts_data = await fetch_endpoint(client, f"/insights/conflicts/{user1}/{user2}", f"Conflicts: {user1} & {user2}")
            
            if compat_data or dynamics_data:
                # Build insights HTML separately to avoid escaping issues
                insights_html = ''
                if compat_data and compat_data.get("insights"):
                    insights_items = ''.join([f'<div class="insight-box">• {insight}</div>' for insight in compat_data.get("insights", [])])
                    insights_html = f'<h2>💡 Compatibility Insights</h2>{insights_items}'
                
                # Build conflict details HTML
                conflicts_html = ''
                if conflicts_data:
                    divergence_html = ''
                    if conflicts_data.get('divergence_sources'):
                        divergence_items = []
                        for source in conflicts_data['divergence_sources']:
                            severity_color = {'high': '#dc3545', 'medium': '#ffc107', 'low': '#28a745'}.get(source['severity'], '#6c757d')
                            divergence_items.append(f'''
                                <div class="divergence-source" style="border-left-color: {severity_color};">
                                    <div class="source-header">
                                        <strong>{source['source']}</strong>
                                        <span class="severity-badge" style="background: {severity_color};">{source['severity'].upper()}</span>
                                    </div>
                                    <div class="source-description">{source['description']}</div>
                                    <div class="source-evidence">📊 Evidence: {source['evidence_count']} instances detected</div>
                                    <div class="source-recommendation">💡 Recommendation: {source['recommendation']}</div>
                                </div>
                            ''')
                        divergence_html = '<h2>🎯 Sources of Divergence</h2>' + ''.join(divergence_items)
                    
                    # Build detailed conflict examples
                    conflict_examples = ''
                    if conflicts_data.get('conflicts'):
                        examples = []
                        for conflict in conflicts_data['conflicts'][:5]:  # Top 5
                            types_str = ', '.join(conflict.get('conflict_types', []))
                            context_html = ''
                            if conflict.get('context'):
                                context_items = []
                                for ctx in conflict['context']:
                                    style = 'background: #ffe6e6; border-left: 3px solid #dc3545;' if ctx.get('is_conflict') else ''
                                    context_items.append(f'<div class="context-msg" style="{style}"><strong>{ctx["user"]}:</strong> {ctx["message"]}</div>')
                                context_html = '<div class="conflict-context">' + ''.join(context_items) + '</div>'
                            
                            examples.append(f'''
                                <div class="conflict-example">
                                    <div class="conflict-header">
                                        <span class="conflict-date">{conflict.get('date', 'Unknown')}</span>
                                        <span class="conflict-score-badge">Score: {conflict['conflict_score']}</span>
                                    </div>
                                    <div class="conflict-types">Types: {types_str}</div>
                                    <div class="conflict-reasoning">{conflict.get('reasoning', 'N/A')}</div>
                                    {context_html}
                                </div>
                            ''')
                        conflict_examples = '<h2>🔍 Detailed Conflict Analysis</h2>' + ''.join(examples)
                    
                    risk_color = {'high': '#dc3545', 'medium': '#ffc107', 'low': '#28a745', 'minimal': '#17a2b8'}.get(conflicts_data.get('risk_level', 'unknown'), '#6c757d')
                    conflicts_html = f'''
                        <h2>⚠️ Conflict Detection</h2>
                        <div class="insight-box">
                            <strong>Potential Conflicts:</strong> {conflicts_data.get("potential_conflicts_detected", 0)}<br>
                            <strong>Conflict Rate:</strong> {conflicts_data.get("conflict_rate", 0):.2f}%<br>
                            <strong>Risk Level:</strong> <span style="color: {risk_color}; font-weight: bold; text-transform: uppercase;">{conflicts_data.get("risk_level", "unknown")}</span>
                        </div>
                        {divergence_html}
                        {conflict_examples}
                    '''
                
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Relationship Insights - {user1} & {user2}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        h2 {{ color: #667eea; margin-top: 40px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
        .metric-card {{ padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 14px; opacity: 0.9; }}
        .metric-value {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .insight-box {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 4px; }}
        .health-score {{ background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }}
        #chart {{ width: 100%; height: 400px; margin: 20px 0; }}
        .divergence-source {{ margin: 20px 0; padding: 20px; background: white; border-left: 4px solid; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .source-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .severity-badge {{ padding: 4px 12px; color: white; border-radius: 12px; font-size: 11px; font-weight: bold; }}
        .source-description {{ margin: 10px 0; color: #333; line-height: 1.6; }}
        .source-evidence {{ margin: 8px 0; color: #666; font-size: 14px; }}
        .source-recommendation {{ margin: 8px 0; padding: 10px; background: #e3f2fd; border-radius: 4px; font-size: 14px; }}
        .conflict-example {{ margin: 20px 0; padding: 20px; background: #fff9e6; border-radius: 8px; border: 1px solid #ffc107; }}
        .conflict-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .conflict-date {{ color: #666; font-size: 14px; }}
        .conflict-score-badge {{ padding: 4px 8px; background: #dc3545; color: white; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .conflict-types {{ margin: 8px 0; color: #666; font-size: 13px; }}
        .conflict-reasoning {{ margin: 12px 0; padding: 12px; background: white; border-radius: 4px; line-height: 1.6; }}
        .conflict-context {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; }}
        .context-msg {{ margin: 8px 0; padding: 10px; background: white; border-radius: 4px; border-left: 3px solid #ccc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤝 Relationship Insights</h1>
        <p style="color: #666; font-size: 16px;">{user1} & {user2}</p>
        <div class="metric-grid">
            {f'<div class="metric-card"><div class="metric-label">Compatibility Score</div><div class="metric-value">{compat_data.get("compatibility_score", 0)}%</div></div>' if compat_data else ''}
            {f'<div class="metric-card health-score"><div class="metric-label">Relationship Health</div><div class="metric-value">{conflicts_data.get("health_score", 0)}/100</div></div>' if conflicts_data else ''}
            {f'<div class="metric-card"><div class="metric-label">Engagement Score</div><div class="metric-value">{dynamics_data.get("conversation_dynamics", {{}}).get("engagement_score", 0):.0f}/100</div></div>' if dynamics_data else ''}
        </div>
        {f'<h2>💬 Conversation Dynamics</h2><div id="chart"></div><div class="insight-box"><strong>Initiations:</strong> {json.dumps(dynamics_data.get("conversation_dynamics", {{}}).get("initiations", {{}}))} <br><strong>Avg Response Time:</strong> {dynamics_data.get("conversation_dynamics", {{}}).get("avg_response_time_minutes", 0):.1f} minutes</div>' if dynamics_data else ''}
        {insights_html}
        {conflicts_html}
    </div>
    <script>
        {f'var initiations = {json.dumps(dynamics_data.get("conversation_dynamics", {{}}).get("initiations", {{}}))};var data = [{{x: Object.keys(initiations), y: Object.values(initiations), type: "bar", marker: {{color: ["#667eea", "#764ba2"]}}}}];var layout = {{title: "Who Initiates Conversations", yaxis: {{title: "Number of Initiations"}}, plot_bgcolor: "#f8f9fa", paper_bgcolor: "white"}};Plotly.newPlot("chart", data, layout, {{responsive: true}});' if dynamics_data else ''}
    </script>
</body>
</html>"""
                output_path = OUTPUT_DIR / "10_relationship_insights.html"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   💾 Saved: {output_path}")
                visualizations.append({"title": "Relationship Insights", "file": "10_relationship_insights.html", "description": f"Compatibility: {user1} & {user2}"})
        print()
        
        # 10. Knowledge Base
        print("1️⃣1️⃣ KNOWLEDGE BASE")
        print("-" * 70)
        search_queries = ["quarantine", "Qatar", "tomorrow"]
        kb_results = []
        for query in search_queries:
            result = await fetch_endpoint(client, f"/knowledge/search?q={query}&limit=5", f"Search: '{query}'")
            if result and result.get('total_results', 0) > 0:
                kb_results.append((query, result))
        
        if kb_results:
            # Build search results HTML separately to avoid escaping issues
            search_sections = []
            for query, result in kb_results:
                results_html = []
                for r in result.get("results", [])[:3]:
                    msg_preview = r["message"][:200] + ("..." if len(r["message"]) > 200 else "")
                    results_html.append(f'<div class="result"><div class="result-message">{msg_preview}</div><div class="result-meta"><strong>{r["username"]}</strong> • {r["timestamp"][:10]} • <span class="relevance-badge">Relevance: {r["relevance_score"]:.1f}</span></div></div>')
                
                search_sections.append(f'<div class="search-section"><div class="query-title">🔍 "{query}"</div><div style="color: #666; font-size: 14px; margin-bottom: 15px;">Found {result.get("total_results", 0)} results</div>{"".join(results_html)}</div>')
            
            all_searches = ''.join(search_sections)
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Personal Knowledge Base</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .search-section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        .query-title {{ font-size: 20px; font-weight: bold; color: #667eea; margin-bottom: 15px; }}
        .result {{ margin: 15px 0; padding: 15px; background: white; border-left: 3px solid #667eea; border-radius: 4px; }}
        .result-message {{ color: #333; margin: 10px 0; }}
        .result-meta {{ font-size: 12px; color: #666; margin-top: 8px; }}
        .relevance-badge {{ display: inline-block; padding: 2px 8px; background: #28a745; color: white; border-radius: 12px; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Personal Knowledge Base</h1>
        <p style="color: #666;">Search results from conversation history</p>
        {all_searches}
    </div>
</body>
</html>"""
            output_path = OUTPUT_DIR / "11_knowledge_base.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   💾 Saved: {output_path}")
            visualizations.append({"title": "Knowledge Base Search", "file": "11_knowledge_base.html", "description": "Search results from history"})
        print()
        
        # 11. Comprehensive Analysis
        print("1️⃣2️⃣ COMPREHENSIVE ANALYSIS")
        print("-" * 70)
        data = await fetch_endpoint(client, f"/analyze/comprehensive/{test_user}", "Complete Analysis")
        if data:
            # Create a special page for comprehensive data
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Comprehensive Analysis - {test_user}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; margin-bottom: 30px; }}
        h2 {{ color: #667eea; margin-top: 30px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .metric {{
            display: inline-block;
            margin: 10px;
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            font-weight: 600;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .metric-value {{
            font-size: 1.5em;
            margin-top: 5px;
        }}
        pre {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Comprehensive Analysis: {test_user}</h1>
        
        <div class="metric">
            <div class="metric-label">Total Messages</div>
            <div class="metric-value">{data.get('total_messages', 0)}</div>
        </div>
        
        <h2>🎭 Personality Traits</h2>
        <div class="section">
            <pre>{json.dumps(data.get('nlp_analysis', {}).get('personality', {}), indent=2)}</pre>
        </div>
        
        <h2>😊 Sentiment Analysis</h2>
        <div class="section">
            <pre>{json.dumps(data.get('nlp_analysis', {}).get('sentiment', {}), indent=2)}</pre>
        </div>
        
        <h2>📝 Readability Metrics</h2>
        <div class="section">
            <pre>{json.dumps(data.get('nlp_analysis', {}).get('readability', {}), indent=2)}</pre>
        </div>
        
        <h2>🎩 Formality Analysis</h2>
        <div class="section">
            <pre>{json.dumps(data.get('nlp_analysis', {}).get('formality', {}), indent=2)}</pre>
        </div>
        
        <h2>💬 Conversation Patterns</h2>
        <div class="section">
            <pre>{json.dumps(data.get('conversation_patterns', {}), indent=2)}</pre>
        </div>
        
        <h2>🏷️ Topics (LDA)</h2>
        <div class="section">
            <pre>{json.dumps(data.get('nlp_analysis', {}).get('topics_lda', {}), indent=2)}</pre>
        </div>
        
        <h2>🏷️ Topics (BERTopic)</h2>
        <div class="section">
            <pre>{json.dumps(data.get('nlp_analysis', {}).get('topics_bertopic', {}), indent=2)}</pre>
        </div>
        
        <h2>📈 Graph Patterns</h2>
        <div class="section">
            <pre>{json.dumps(data.get('graph_patterns', {}), indent=2)}</pre>
        </div>
    </div>
</body>
</html>"""
            
            output_path = OUTPUT_DIR / "12_comprehensive_analysis.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   💾 Saved: {output_path}")
            
            visualizations.append({
                "title": "Comprehensive Analysis",
                "file": "12_comprehensive_analysis.html",
                "description": f"All metrics combined for {test_user}"
            })
        print()
        
        # Create index page
        print("=" * 70)
        print("📑 Creating index page...")
        index_path = create_index_html(visualizations)
        print(f"   💾 Saved: {index_path}")
        print()
        
        # Summary
        print("=" * 70)
        print("✅ VISUALIZATION GENERATION COMPLETE!")
        print("=" * 70)
        print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
        print(f"📊 Generated {len(visualizations)} visualizations")
        print()
        print("🌐 To view the visualizations:")
        print(f"   Open: {index_path.absolute()}")
        print()
        print("   Or open individual files:")
        for viz in visualizations:
            print(f"   - {viz['file']}: {viz['title']}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
