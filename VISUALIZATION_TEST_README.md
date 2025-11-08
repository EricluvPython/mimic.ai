# Visualization Test Script

This script tests all visualization endpoints and generates interactive HTML charts.

## 🚀 Quick Start

### Option 1: PowerShell Script (Easiest)
```powershell
.\run_viz_test.ps1
```
This will:
1. Check if the server is running
2. Generate all visualizations
3. Automatically open them in your browser

### Option 2: Direct Python
```powershell
python test_visualizations.py
```
Then manually open `visualizations_output/index.html` in your browser.

## 📋 Prerequisites

1. **Server must be running:**
   ```powershell
   python -m app.main
   ```

2. **Data must be uploaded:**
   - Upload at least one chat file via `POST /upload`
   - Or use the Swagger UI at http://localhost:8000/docs

## 📊 What Gets Generated

The script creates interactive HTML files in `visualizations_output/`:

1. **`index.html`** - Main dashboard with links to all visualizations
2. **`01_network_graph.html`** - User-Topic relationship network
3. **`02_sentiment_timeline.html`** - Sentiment progression over time
4. **`03_topics_lda.html`** - Statistical topic modeling (LDA)
5. **`04_topics_bertopic.html`** - Advanced topic modeling (BERTopic)
6. **`05_personality_radar.html`** - Personality trait analysis
7. **`06a_response_times.html`** - Response time analysis
8. **`06b_activity_heatmap.html`** - Activity by hour of day
9. **`06c_message_lengths.html`** - Message length distribution
10. **`07_formality_gauge.html`** - Communication formality level
11. **`08_comprehensive_analysis.html`** - All metrics combined

## 🎨 Chart Types

- **Line Charts**: Sentiment timeline
- **Bar Charts**: Topics, response times, activity
- **Radar Charts**: Personality traits
- **Pie Charts**: Message length distribution
- **Gauge Charts**: Formality level
- **Network Graphs**: User-topic relationships

## 🔧 Troubleshooting

### "Server is not running"
```powershell
# Start the server in another terminal
python -m app.main
```

### "No users found"
```powershell
# Upload a chat file first
curl -X POST "http://localhost:8000/upload" -F "file=@sample_chat.txt"
```

### Charts not loading
- Make sure you have internet connection (loads Plotly from CDN)
- Try refreshing the page
- Check browser console for errors

### BERTopic fails
- This is normal for small datasets
- Use LDA topics instead (also generated)
- BERTopic requires ~10+ diverse messages

## 📁 File Structure

```
visualizations_output/
├── index.html                      # Main dashboard
├── 01_network_graph.html          # Network visualization
├── 02_sentiment_timeline.html     # Sentiment analysis
├── 03_topics_lda.html             # LDA topics
├── 04_topics_bertopic.html        # BERTopic topics
├── 05_personality_radar.html      # Personality traits
├── 06a_response_times.html        # Response time chart
├── 06b_activity_heatmap.html      # Activity patterns
├── 06c_message_lengths.html       # Length distribution
├── 07_formality_gauge.html        # Formality analysis
└── 08_comprehensive_analysis.html # Complete analysis
```

## 🎯 Demo Tips

For your hackathon demo:

1. **Run this script before the demo** to have all visualizations ready
2. **Open index.html** as a starting point
3. **Navigate to specific charts** to show different analyses
4. **Use comprehensive analysis** to show all metrics at once

## 💡 Using in Your Frontend

The same data can be fetched via API:

```javascript
// Example: Fetch sentiment visualization
fetch('http://localhost:8000/visualize/sentiment/Sunaya')
  .then(r => r.json())
  .then(data => {
    // data.chart contains Plotly-ready chart data
    Plotly.newPlot('chart-div', data.chart.data, data.chart.layout);
    
    // data.analysis contains raw analysis results
    console.log(data.analysis);
  });
```

## 📝 Notes

- Charts are fully interactive (zoom, pan, hover for details)
- All visualizations use Plotly.js
- Data is fetched in real-time from the API
- First run may take longer (BERTopic downloads models)

## 🆘 Need Help?

Check the API documentation: http://localhost:8000/docs
