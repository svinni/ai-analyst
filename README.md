# AI Analyst Helper

An AI-powered analysis assistant built on Claude Opus 4.6 that guides you through a complete data analysis workflow — from framing the problem to delivering a compelling presentation.

## Skills

| # | Skill | What it does |
|---|-------|-------------|
| 1 | **Analysis Framing** | Sharpens your business question into a structured brief with scope, KPIs, assumptions, and stakeholder context |
| 2 | **Analysis Planning** | Builds a phased, methodology-driven plan with deliverables and a Quick Win |
| 3 | **Data Wrangling** | Profiles, cleans, and engineers features from your data — accepts a real file upload or a text description |
| 4 | **Deep Dive** | Full EDA, hypothesis tests, correlation analysis, and publication-quality visualizations |
| 5 | **Storytelling** | Produces a slide-by-slide deck outline, elevator pitch, data headline, and three memorable takeaways |

Each skill builds on the previous one in a persistent conversation — so the cleaned data from step 3 is available when Claude runs code in steps 4 and 5.

## How it works

- **Model**: Claude Opus 4.6 with adaptive thinking
- **Code execution**: Claude runs Python in a secure, sandboxed container (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn pre-installed). The container persists across all five skills in a session.
- **File uploads**: Upload real CSV, Excel, or JSON files via the Anthropic Files API
- **Streaming**: All responses stream in real time
- **Audience-aware storytelling**: Target your final story at executives, technical teams, business stakeholders, or a general audience

## Project structure

```
ai_analyst/
├── analyst.py       # Core AnalystHelper class — all five skills
├── main.py          # Interactive CLI, guided wizard, and demo mode
└── requirements.txt
```

## Setup

**1. Clone the repo**
```bash
git clone git@github.com:svinni/ai-analyst.git
cd ai-analyst
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set your Anthropic API key**
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Interactive menu
```bash
python main.py
```
Pick any skill from the menu. Skills accumulate context as you progress.

### Guided full-workflow wizard
```bash
python main.py --workflow
```
Walks you through all five skills in sequence with prompts at each step.

### Built-in demo
```bash
python main.py --demo
```
Runs a complete end-to-end analysis on a synthetic e-commerce revenue decline scenario — good for seeing all five skills in action before using your own data.

### Use as a Python module
```python
from analyst import AnalystHelper

analyst = AnalystHelper()

analyst.frame_analysis("Our churn rate increased 12% last quarter. Why?")
analyst.create_plan()
analyst.wrangle_data(file_path="customers.csv")   # or data_description="..."
analyst.deep_dive(focus_area="churn drivers by segment")
analyst.tell_story(audience="executive")          # or "technical" | "business" | "general"

# Ask follow-up questions at any point
analyst.ask("Which customer segment has the highest recovery potential?")

# Clean up uploaded files when done
analyst.cleanup()
```

## Requirements

- Python 3.9+
- [Anthropic API key](https://console.anthropic.com/)
- `anthropic` Python SDK (`pip install anthropic`)
