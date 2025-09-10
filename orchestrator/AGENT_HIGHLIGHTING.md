# Agent Selection Highlighting Feature

## Overview

This application includes a visual feedback system that shows which agent was selected after task execution. When a user submits a prompt, the system automatically:

1. Classifies the prompt to determine the most appropriate agent
2. Processes the request using the selected agent
3. Highlights the selected agent's card with a colored border and glow effect

## Visual Indicators

| Agent | Color | Description |
|-------|-------|-------------|
| **Coder** | 🔵 Blue | Technical implementation, code, architecture, deployment |
| **Analyst** | 🟢 Green | Data analysis, statistics, research, verification |
| **Travel** | 🟡 Yellow | Travel planning, tourism, practical advice |
| **None** | ⚫ No color | General queries that don't fit specific categories |

## How It Works

### Backend Classification
The `autogen_router.py` module:
- Uses a classifier to analyze the user's prompt
- Returns a response with the format: `{"selected": "agent_type", "response": "..."}`
- Supports four agent types: `"coder"`, `"analyst"`, `"travel"`, `"none"`

### Frontend Visualization  
The `app.js` script:
- Receives the API response with the selected agent
- Applies CSS classes to highlight the appropriate agent card
- Clears previous highlights before showing new ones

### CSS Styling
The `styles.css` file defines the visual effects:
```css
/* Base selected state */
.agent-card.selected {
  background: var(--highlight);
}

/* Agent-specific colors */
.agent-card.selected-coder {
  border-color: var(--primary);  /* Blue */
  box-shadow: 0 0 0 2px rgba(74,168,255,.25), 0 12px 32px rgba(0,0,0,.35);
}

.agent-card.selected-analyst {
  border-color: var(--ok);  /* Green */
  box-shadow: 0 0 0 2px rgba(46,204,113,.25), 0 12px 32px rgba(0,0,0,.35);
}

.agent-card.selected-travel {
  border-color: var(--warn);  /* Yellow */
  box-shadow: 0 0 0 2px rgba(255,204,0,.25), 0 12px 32px rgba(0,0,0,.35);
}
```

## Example Usage

### Coder Agent (Blue Highlight)
**Prompt:** "Flask で WebSocket の再接続処理を組み込みたい。堅牢な実装例は？"  
**Result:** Coder agent card displays with blue border and glow

### Analyst Agent (Green Highlight)  
**Prompt:** "データ分析を行いたい。統計的な手法を教えて。"  
**Result:** Analyst agent card displays with green border and glow

### Travel Agent (Yellow Highlight)
**Prompt:** "京都の旅行プランを作って。おすすめの観光地は？"  
**Result:** Travel agent card displays with yellow border and glow

### No Agent (No Highlight)
**Prompt:** "今日の天気はどうですか？"  
**Result:** No agent card is highlighted

## Testing

Run the test script to verify functionality:
```bash
python test_agent_highlighting.py
```

This will test all four agent types and verify that the correct selections are made.

## Implementation Details

### JavaScript Logic (`app.js`)
```javascript
// Clear all highlights
function clearHighlights(){
  Object.values(agentEls).forEach(el =>
    el.classList.remove(
      "selected",
      "selected-coder", 
      "selected-analyst",
      "selected-travel"
    )
  );
}

// Apply highlight based on selected agent
if(data.selected && agentEls[data.selected]){
  agentEls[data.selected].classList.add("selected", `selected-${data.selected}`);
}
```

### Agent Classification Logic (`autogen_router.py`)
The system uses keyword matching and machine learning classification to determine the appropriate agent based on the user's prompt content and intent.

## Browser Compatibility

This feature works in all modern browsers that support:
- CSS3 box-shadow and border effects
- ES6 JavaScript features
- Fetch API for AJAX requests

## Troubleshooting

If highlighting doesn't work:
1. Check browser console for JavaScript errors
2. Verify the API response includes a `selected` field
3. Ensure CSS classes are properly loaded
4. Test with the mock implementation using `test_agent_highlighting.py`