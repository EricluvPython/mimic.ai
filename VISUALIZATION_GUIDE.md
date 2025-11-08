# Advanced Visualization & NLP Analysis - Setup Guide

## 🎯 New Features Implemented

### 1. **Advanced NLP Analysis**
- **BERTopic**: State-of-the-art topic modeling
- **LDA**: Statistical topic extraction
- **Sentiment Analysis**: VADER sentiment with timeline
- **Personality Insights**: Linguistic pattern analysis
- **Readability Metrics**: Flesch-Kincaid, Gunning Fog, SMOG index
- **Formality Detection**: Communication style analysis

### 2. **Conversation Pattern Analysis**
- Response time analysis
- Turn-taking patterns
- Question frequency
- Activity patterns (by hour/day)
- Message length distribution

### 3. **Visualization API**
- Network graph visualization
- Sentiment timeline charts
- Topic distribution charts
- Personality radar charts
- Activity heatmaps
- Formality gauge charts

---

## 📦 Installation Steps

### Step 1: Install New Dependencies

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install new packages
pip install -r requirements.txt

# Download spaCy model (optional, for NER)
# python -m spacy download en_core_web_sm
```

### Step 2: Restart the Server

```powershell
# Stop the current server (Ctrl+C)
# Then restart
python -m app.main
```

---

## 🧪 Testing the New Endpoints

### 1. **Network Graph Visualization**
```bash
curl http://localhost:8000/visualize/graph
```

### 2. **Sentiment Analysis**
```bash
curl "http://localhost:8000/visualize/sentiment/Sunaya"
```

### 3. **Topic Modeling (LDA)**
```bash
curl "http://localhost:8000/visualize/topics?method=lda"
```

### 4. **Topic Modeling (BERTopic)**
```bash
curl "http://localhost:8000/visualize/topics?method=bertopic"
```

### 5. **Personality Analysis**
```bash
curl "http://localhost:8000/visualize/personality/Eric%20Gao"
```

### 6. **Conversation Patterns**
```bash
curl http://localhost:8000/visualize/patterns
```

### 7. **Formality Analysis**
```bash
curl "http://localhost:8000/visualize/formality/Sunaya"
```

### 8. **Comprehensive Analysis**
```bash
curl "http://localhost:8000/analyze/comprehensive/Sunaya"
```

---

## 📊 Visualization Data Format

All visualization endpoints return Plotly-compatible JSON:

```json
{
  "chart": {
    "data": [...],  // Plotly traces
    "layout": {     // Plotly layout
      "title": "Chart Title",
      "xaxis": {...},
      "yaxis": {...}
    }
  },
  "analysis": {...}  // Raw analysis data
}
```

### Frontend Integration Example

```javascript
// Fetch sentiment visualization
const response = await fetch('http://localhost:8000/visualize/sentiment/Sunaya');
const result = await response.json();

// Use with Plotly.js
Plotly.newPlot('chart-div', result.chart.data, result.chart.layout);

// Or use raw analysis data
console.log(result.analysis.overall.compound); // Overall sentiment score
```

---

## 🎨 Available Visualizations

### 1. **Network Graph**
- Shows relationships between users and topics
- Node size = activity level
- Edges = interaction strength

### 2. **Sentiment Timeline**
- Line chart showing sentiment over time
- Separate trace for each user
- Compound score (-1 to 1)

### 3. **Topic Distribution**
- Bar chart of top topics
- Supports both LDA and BERTopic
- Shows relevance/frequency

### 4. **Personality Radar**
- 5-dimension radar chart
- Self-focus, social orientation, emotions, analytical thinking
- Based on linguistic patterns (LIWC-inspired)

### 5. **Activity Heatmap**
- Bar chart by hour of day
- Color-coded by activity level
- Helps identify peak communication times

### 6. **Response Time Distribution**
- Bar chart showing average response times per user
- Helps understand engagement levels

### 7. **Message Length Distribution**
- Pie chart: Short/Medium/Long messages
- Shows communication style preferences

### 8. **Formality Gauge**
- Gauge chart (0-100)
- Categories: Very Informal → Very Formal
- Based on formal/informal word usage

---

## 📈 Analysis Metrics Explained

### Sentiment Analysis
- **Compound**: Overall sentiment (-1 to 1)
- **Positive**: Positive emotion percentage
- **Negative**: Negative emotion percentage
- **Neutral**: Neutral content percentage

### Personality Traits
- **Self Focus**: First-person pronoun usage
- **Social Orientation**: Social word usage
- **Positive/Negative Emotion**: Emotion word frequency
- **Analytical Thinking**: Cognitive word usage

### Readability
- **Flesch Reading Ease**: 0-100 (higher = easier)
- **Flesch-Kincaid Grade**: US grade level
- **Gunning Fog**: Years of education needed
- **SMOG Index**: Years of education needed

### Formality
- **Score**: 0-100 (higher = more formal)
- **Indicators**: Formal words, informal words, contractions, punctuation

### Conversation Patterns
- **Response Time**: Average time between messages
- **Turn Length**: Average consecutive messages
- **Question Rate**: Percentage of messages that are questions
- **Activity Peaks**: Most active hours/days

---

## 🔍 Use Cases

### 1. **User Profiling**
```http
GET /analyze/comprehensive/username
```
Complete profile with all metrics

### 2. **Communication Style Comparison**
```http
GET /visualize/personality/user1
GET /visualize/personality/user2
```
Compare personality traits

### 3. **Conversation Health**
```http
GET /visualize/sentiment/username
```
Monitor sentiment trends

### 4. **Topic Trends**
```http
GET /visualize/topics?method=bertopic
```
See what people are discussing

### 5. **Engagement Analysis**
```http
GET /visualize/patterns
```
Response times, activity patterns

---

## 🎯 Next Steps for Frontend

### Recommended Visualization Library
**Plotly.js** (https://plotly.com/javascript/)

```html
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<div id="sentiment-chart"></div>

<script>
fetch('http://localhost:8000/visualize/sentiment/Sunaya')
  .then(r => r.json())
  .then(data => {
    Plotly.newPlot('sentiment-chart', data.chart.data, data.chart.layout);
  });
</script>
```

### Alternative: Chart.js, D3.js, Recharts
The API returns standardized data that can be adapted to any charting library.

---

## 🐛 Troubleshooting

### Import Errors
```powershell
pip install -r requirements.txt --upgrade
```

### BERTopic Memory Issues
If BERTopic fails, use LDA instead:
```http
GET /visualize/topics?method=lda
```

### Slow Performance
- BERTopic can be slow on large datasets
- Consider limiting message count for analysis
- Use caching for frequently requested analyses

---

## 📝 Notes

- First-time BERTopic usage downloads sentence transformers (~500MB)
- Some analyses require minimum message counts (5-10 messages)
- Sentiment analysis works best with longer messages
- Topic modeling requires diverse vocabulary

---

**Questions?** Check the API docs at http://localhost:8000/docs
