# Advanced Features Examples

Quick examples for testing the new Conversation Suggestions, Relationship Insights, and Personal Knowledge Base features.

## 🚀 Quick Test Commands

### Conversation Suggestions

```bash
# Get conversation starters for Eric Gao
curl http://localhost:8000/suggestions/starters/Eric%20Gao

# Get topic recommendations
curl http://localhost:8000/suggestions/topics/Eric%20Gao

# Predict response
curl -X POST http://localhost:8000/suggestions/predict-response \
  -H "Content-Type: application/json" \
  -d '{"user_context": "Eric Gao", "query": "Want to grab dinner?"}'
```

### Relationship Insights

```bash
# Analyze compatibility between two users
curl http://localhost:8000/insights/compatibility/Eric%20Gao/Sunaya

# Check interaction frequency
curl http://localhost:8000/insights/interaction/Eric%20Gao/Sunaya

# Emotional support analysis
curl http://localhost:8000/insights/support/Eric%20Gao/Sunaya

# Detect potential conflicts
curl http://localhost:8000/insights/conflicts/Eric%20Gao/Sunaya

# Full conversation dynamics
curl http://localhost:8000/insights/dynamics/Eric%20Gao/Sunaya
```

### Personal Knowledge Base

```bash
# Search for specific topic
curl "http://localhost:8000/knowledge/search?q=quarantine&limit=5"

# Find when you discussed "qatar"
curl http://localhost:8000/knowledge/topic/qatar

# When was "Lorenzo" last mentioned?
curl http://localhost:8000/knowledge/last-mention/Lorenzo

# Extract facts from conversations
curl http://localhost:8000/knowledge/facts

# Build knowledge graph for "Eric"
curl http://localhost:8000/knowledge/entity/Eric

# Semantic search (meaning-based)
curl "http://localhost:8000/knowledge/semantic-search?q=work&limit=10"
```

## 🐍 Python Examples

```python
import requests

BASE_URL = "http://localhost:8000"

# === CONVERSATION SUGGESTIONS ===

# Get conversation starters
response = requests.get(f"{BASE_URL}/suggestions/starters/Eric Gao")
starters = response.json()
print("Conversation Starters:")
for suggestion in starters['suggestions']:
    print(f"  - {suggestion['starter']}")
    print(f"    Reason: {suggestion['reasoning']}\n")

# Get topic recommendations
response = requests.get(f"{BASE_URL}/suggestions/topics/Eric Gao")
topics = response.json()
print("Recommended Topics:")
for rec in topics['recommendations']:
    print(f"  - {rec['topic']}: {rec['reason']}")

# Predict response
response = requests.post(f"{BASE_URL}/suggestions/predict-response", json={
    "user_context": "Eric Gao",
    "query": "Want to grab lunch tomorrow?"
})
prediction = response.json()
print(f"Predicted response length: {prediction['predicted_response_length']} words")


# === RELATIONSHIP INSIGHTS ===

# Compatibility analysis
response = requests.get(f"{BASE_URL}/insights/compatibility/Eric Gao/Sunaya")
compat = response.json()
print(f"\nCompatibility Score: {compat['compatibility_score']}%")
print("Insights:")
for insight in compat['insights']:
    print(f"  - {insight}")

# Interaction frequency
response = requests.get(f"{BASE_URL}/insights/interaction/Eric Gao/Sunaya")
interaction = response.json()
print(f"\nTotal Interactions: {interaction['total_interactions']}")
print(f"Longest Streak: {interaction['frequency']['longest_streak_days']} days")
print(f"Interaction Balance: {interaction['frequency']['interaction_balance']}%")

# Emotional support
response = requests.get(f"{BASE_URL}/insights/support/Eric Gao/Sunaya")
support = response.json()
print("\nEmotional Support Patterns:")
for user, patterns in support['support_patterns'].items():
    print(f"  {user}: {patterns}")

# Conflict detection
response = requests.get(f"{BASE_URL}/insights/conflicts/Eric Gao/Sunaya")
conflicts = response.json()
print(f"\nPotential Conflicts: {conflicts['potential_conflicts_detected']}")
print(f"Relationship Health Score: {conflicts['health_score']}/100")

# Conversation dynamics
response = requests.get(f"{BASE_URL}/insights/dynamics/Eric Gao/Sunaya")
dynamics = response.json()
print("\nConversation Dynamics:")
print(f"  Initiations: {dynamics['conversation_dynamics']['initiations']}")
print(f"  Avg Response Time: {dynamics['conversation_dynamics']['avg_response_time_minutes']} min")
print(f"  Engagement Score: {dynamics['conversation_dynamics']['engagement_score']}/100")


# === PERSONAL KNOWLEDGE BASE ===

# Search conversations
response = requests.get(f"{BASE_URL}/knowledge/search", params={
    'q': 'quarantine',
    'limit': 5
})
results = response.json()
print(f"\nSearch Results for 'quarantine': {results['total_results']} found")
for result in results['results']:
    print(f"  [{result['username']}]: {result['message'][:80]}...")

# Find topic discussions
response = requests.get(f"{BASE_URL}/knowledge/topic/qatar")
timeline = response.json()
print(f"\nDiscussions about 'qatar':")
print(f"  First mentioned: {timeline['first_mentioned']}")
print(f"  Last mentioned: {timeline['last_mentioned']}")
print(f"  Total discussions: {timeline['total_discussions']}")

# Recall last mention
response = requests.get(f"{BASE_URL}/knowledge/last-mention/Lorenzo")
mention = response.json()
if mention['found']:
    print(f"\nLast mentioned 'Lorenzo':")
    print(f"  {mention['last_mention']['days_ago']} days ago")
    print(f"  By: {mention['last_mention']['username']}")
    print(f"  Message: {mention['last_mention']['message']}")

# Extract facts
response = requests.get(f"{BASE_URL}/knowledge/facts")
facts = response.json()
print(f"\nExtracted {facts['total_facts_extracted']} facts")
print("Categories:")
for category, items in facts['facts_by_category'].items():
    print(f"  {category}: {len(items)} facts")

# Entity knowledge graph
response = requests.get(f"{BASE_URL}/knowledge/entity/Eric")
graph = response.json()
print(f"\nKnowledge about 'Eric':")
print(f"  Mentioned {graph['total_mentions']} times")
print(f"  Related entities: {', '.join(graph['related_entities'][:5])}")

# Semantic search
response = requests.get(f"{BASE_URL}/knowledge/semantic-search", params={
    'q': 'work job office',
    'limit': 5
})
results = response.json()
print(f"\nSemantic search results: {results['total_results']} found")
print(f"Expanded search terms: {', '.join(results['expanded_terms'])}")
```

## 📊 Example Use Cases

### Use Case 1: Conversation Assistant
```python
# Get suggestions before starting a conversation
starters = requests.get(f"{BASE_URL}/suggestions/starters/Eric Gao").json()
print(f"Try: {starters['suggestions'][0]['starter']}")

# Predict how they might respond
prediction = requests.post(f"{BASE_URL}/suggestions/predict-response", json={
    "user_context": "Eric Gao",
    "query": starters['suggestions'][0]['starter']
}).json()
print(f"Expected response length: ~{prediction['predicted_response_length']} words")
```

### Use Case 2: Relationship Health Check
```python
# Full relationship analysis
compatibility = requests.get(f"{BASE_URL}/insights/compatibility/Eric Gao/Sunaya").json()
conflicts = requests.get(f"{BASE_URL}/insights/conflicts/Eric Gao/Sunaya").json()
dynamics = requests.get(f"{BASE_URL}/insights/dynamics/Eric Gao/Sunaya").json()

print(f"Compatibility: {compatibility['compatibility_score']}%")
print(f"Health Score: {conflicts['health_score']}/100")
print(f"Engagement: {dynamics['conversation_dynamics']['engagement_score']}/100")
```

### Use Case 3: Memory Recall
```python
# "When did we discuss going to Qatar?"
timeline = requests.get(f"{BASE_URL}/knowledge/topic/qatar").json()
print(f"You discussed Qatar on these dates:")
for discussion in timeline['timeline']:
    print(f"  - {discussion['date']}: {discussion['message_count']} messages")

# "What did I say about Lorenzo?"
search = requests.get(f"{BASE_URL}/knowledge/search", params={
    'q': 'Lorenzo',
    'username': 'Eric Gao',
    'limit': 3
}).json()
for result in search['results']:
    print(f"  {result['message']}")
```

## 🎯 Integration Tips

### For Frontend Developers
1. **Conversation Page**: Use `/suggestions/starters` to show conversation prompts
2. **User Profile**: Display `/insights/compatibility` scores
3. **Search Bar**: Implement `/knowledge/search` and `/knowledge/semantic-search`
4. **Timeline View**: Show `/knowledge/topic/{topic}` discussions
5. **Relationship Dashboard**: Combine all `/insights/*` endpoints

### Performance Notes
- Knowledge base searches scale with message count
- Cache frequent queries on frontend
- Use `limit` parameter to control response size
- Semantic search is more expensive than keyword search

## 🔮 Next Steps

After testing these features:
1. Integrate into your frontend application
2. Add user authentication for production
3. Implement caching for frequently accessed data
4. Add real-time updates via WebSockets
5. Enhance semantic search with embeddings (future)

---

**See also:**
- `VISUALIZATION_GUIDE.md` - Guide for visualization features
- `QUICKSTART.md` - Basic setup and usage
- API Docs: http://localhost:8000/docs
