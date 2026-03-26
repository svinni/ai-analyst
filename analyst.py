"""
AI Analyst Helper — Core Module

Skills:
  1. Analysis Framing   — Define the problem, scope, and key questions
  2. Analysis Planning  — Structured, step-by-step analysis plan
  3. Data Wrangling     — Clean, transform, and profile data
  4. Deep Dive          — EDA, statistical analysis, and visualizations
  5. Storytelling       — Craft a compelling narrative and presentation
"""

import os
from pathlib import Path
from typing import Optional
import anthropic

SYSTEM_PROMPT = """You are a senior data analyst and storyteller with deep expertise in transforming raw data into compelling business insights.

You guide users through a complete analysis workflow:
  1. Framing      — Sharpen the problem, define success metrics and scope
  2. Planning     — Build a rigorous, actionable analysis plan
  3. Wrangling    — Profile, clean, and engineer features from raw data
  4. Deep Dive    — EDA, statistics, visualizations, pattern recognition
  5. Storytelling — Craft a presentation-ready narrative with clear recommendations

You have access to a Python sandbox (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, statsmodels, and more). Use it for ALL data tasks — always show your code, annotate it clearly, and interpret the output.

Core principles:
- Ask clarifying questions if the problem is ambiguous
- Lead with insights, support with data
- Every chart must have a clear title, axis labels, and a "so what" interpretation
- Recommendations must be concrete, prioritized, and tied to data
- Write code a senior analyst would be proud of"""


class AnalystHelper:
    """
    Orchestrates the five analyst skills in a persistent conversation,
    optionally reusing a code-execution container across turns.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.history: list[dict] = []
        self.container_id: Optional[str] = None
        self.uploaded_file_ids: list[str] = []
        self.context = {
            "problem": None,
            "framing": None,
            "plan": None,
            "wrangling": None,
            "findings": None,
            "story": None,
        }

    # ─────────────────────────────────────────────
    # Public skills
    # ─────────────────────────────────────────────

    def frame_analysis(self, problem: str) -> str:
        """Skill 1 — Frame the analysis problem."""
        self.context["problem"] = problem

        prompt = f"""I need to frame an analysis project. Here is the problem:

**Problem statement**: {problem}

Please produce a concise Analysis Brief covering:

1. **Problem Restatement** — sharpen and clarify the core question
2. **Key Business Questions** — 3–5 specific questions this analysis must answer
3. **Success Metrics** — how we will know the analysis is successful
4. **Scope & Boundaries** — what is in/out of scope
5. **Key Assumptions** — important assumptions we're making
6. **Stakeholder Perspective** — who needs this and why
7. **Potential Challenges** — what might complicate the analysis

Be thorough but concise. Format as a structured brief."""

        text = self._chat(prompt, skill_label="ANALYSIS FRAMING")
        self.context["framing"] = text
        return text

    def create_plan(self) -> str:
        """Skill 2 — Build a detailed analysis plan."""
        if not self.context["problem"]:
            return _warn("Run frame_analysis() first.")

        prompt = """Based on the framing above, create a detailed Analysis Plan.

Include:
1. **Data Requirements** — what data, format, time period, granularity
2. **Analysis Phases** — break work into clear, sequenced phases
3. **Methodology** — statistical / ML techniques per phase
4. **Deliverables** — what each phase produces
5. **Risk Mitigation** — how to handle data gaps, quality issues, etc.

Close with a **Quick Win**: the single highest-impact analysis to run first."""

        text = self._chat(prompt, skill_label="ANALYSIS PLANNING")
        self.context["plan"] = text
        return text

    def wrangle_data(
        self,
        file_path: Optional[str] = None,
        data_description: Optional[str] = None,
    ) -> str:
        """Skill 3 — Profile, clean, and engineer features.

        Args:
            file_path:        Path to a local CSV, Excel, or JSON file to upload.
            data_description: Plain-text description of the data (if no file).
        """
        if file_path:
            file_id = self._upload_file(file_path)
            if not file_id:
                return _warn(f"Could not upload {file_path}.")

            user_content = [
                {"type": "text", "text": _wrangle_with_file_prompt(Path(file_path).name)},
                {"type": "container_upload", "file_id": file_id},
            ]
            text = self._chat(
                user_content,
                skill_label="DATA WRANGLING",
                use_files_beta=True,
            )

        elif data_description:
            prompt = f"""I have described my dataset below. Please:
1. Create a realistic synthetic sample (≥50 rows) matching the description
2. Run a full data profiling report (shape, dtypes, nulls, uniques, stats)
3. Identify and fix data quality issues in the sample
4. Demonstrate feature engineering relevant to the analysis plan

**Data description**:
{data_description}

Write executable pandas code and interpret every output."""
            text = self._chat(prompt, skill_label="DATA WRANGLING")

        else:
            prompt = """Let's prepare for data wrangling.
Please help me:
1. Define exactly what data we need (sources, schema, time range)
2. Build a data collection checklist
3. Design the target data schema
4. Outline the wrangling strategy for this analysis

If no real data is available yet, generate a representative mock dataset and demonstrate the full wrangling pipeline on it."""
            text = self._chat(prompt, skill_label="DATA WRANGLING")

        self.context["wrangling"] = text
        return text

    def deep_dive(self, focus_area: Optional[str] = None) -> str:
        """Skill 4 — EDA, statistical analysis, and visualizations."""
        focus = f"\n\n**Special focus**: {focus_area}" if focus_area else ""

        prompt = f"""Time for the deep dive.{focus}

Please conduct a comprehensive analysis:

**1. Exploratory Data Analysis**
   - Univariate distributions for all key variables
   - Bivariate relationships and correlations
   - Time trends (if applicable)
   - Segment comparisons

**2. Statistical Analysis**
   - Hypothesis tests where relevant (state H0, H1, p-value, conclusion)
   - Confidence intervals for key estimates
   - Effect sizes

**3. Visualizations** (create 4–6 publication-quality charts)
   - Each chart: clear title, axis labels, annotation of the key insight
   - Save each as a PNG file (e.g., fig1_distribution.png)
   - After each chart, write 1–2 sentences interpreting what it shows

**4. Anomaly & Pattern Detection**
   - Outliers, unusual segments, surprising correlations

**5. Top Findings**
   - 5 most important findings, ranked by business impact
   - Data evidence for each
   - Business implication in plain language

Write clean, well-commented Python. Print a summary after each section."""

        text = self._chat(prompt, skill_label="DEEP DIVE ANALYSIS")
        self.context["findings"] = text
        return text

    def tell_story(self, audience: str = "executive") -> str:
        """Skill 5 — Craft a presentation-ready narrative.

        Args:
            audience: 'executive' | 'technical' | 'business' | 'general'
        """
        audience_profiles = {
            "executive": (
                "C-suite executives. Lead with the bottom line, quantify business impact, "
                "keep it under 10 slides, one key message per slide."
            ),
            "technical": (
                "Data scientists / analysts. Include methodology details, statistical rigor, "
                "code snippets, and reproducibility notes."
            ),
            "business": (
                "Business unit managers and operational stakeholders. Focus on implications, "
                "process changes, and what they need to do differently."
            ),
            "general": (
                "Mixed audience. Use plain language, avoid jargon, rely on visual analogies."
            ),
        }
        audience_desc = audience_profiles.get(audience, audience_profiles["executive"])

        prompt = f"""Based on everything we have discovered, craft a complete presentation story.

**Target audience**: {audience.title()} — {audience_desc}

Structure the deck as follows:

---
### SLIDE 1 — TITLE & HOOK
- Headline: the single most compelling finding (≤15 words)
- Sub-headline: why this matters now

### SLIDE 2 — THE SITUATION
- Background & context
- The question we set out to answer

### SLIDE 3 — THE DATA
- What we analysed (sources, coverage, time period, sample size)
- Key variables

### SLIDES 4–6 — THREE KEY INSIGHTS
(One slide per insight)
- Finding headline
- Supporting metric / statistic
- Chart reference (which PNG)
- Business implication (1 sentence)

### SLIDE 7 — THE NARRATIVE
- How the three insights connect into one coherent story
- The "so what" moment

### SLIDE 8 — RECOMMENDATIONS
- 3 concrete, prioritised actions
- Responsible owner (role, not name)
- Expected impact (quantified where possible)

### SLIDE 9 — NEXT STEPS
- This week / this quarter / further analysis needed
---

Then provide:
- **The Elevator Pitch** (≤30 seconds / ≤60 words): if you had 30 seconds in a lift, what would you say?
- **The Data Headline**: a punchy news-style headline for this analysis
- **Three Memorable Takeaways**: what should the audience still remember tomorrow morning?"""

        text = self._chat(prompt, skill_label="STORYTELLING & PRESENTATION")
        self.context["story"] = text
        return text

    def ask(self, question: str) -> str:
        """Free-form follow-up question within the current analysis context."""
        return self._chat(question, skill_label="FOLLOW-UP")

    def summary(self) -> dict:
        """Return a high-level summary of the analysis session."""
        completed = [k for k, v in self.context.items() if v]
        return {
            "problem": self.context["problem"],
            "phases_completed": completed,
            "conversation_turns": len(self.history) // 2,
            "files_uploaded": len(self.uploaded_file_ids),
            "container_id": self.container_id,
        }

    def cleanup(self):
        """Delete any uploaded files from the Files API."""
        for fid in self.uploaded_file_ids:
            try:
                self.client.beta.files.delete(fid)
                print(f"  Deleted file {fid}")
            except Exception as e:
                print(f"  Could not delete {fid}: {e}")
        self.uploaded_file_ids.clear()

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    def _chat(
        self,
        user_content,
        skill_label: str = "",
        use_files_beta: bool = False,
    ) -> str:
        """Append user turn, stream the response, and return full text."""
        _print_header(skill_label)

        self.history.append({"role": "user", "content": user_content})

        full_text = ""
        final_message = None

        # Loop to handle pause_turn (server-side tool loop limit)
        current_messages = list(self.history)

        while True:
            kwargs: dict = {
                "model": "claude-opus-4-6",
                "max_tokens": 16000,
                "thinking": {"type": "adaptive"},
                "system": SYSTEM_PROMPT,
                "messages": current_messages,
                "tools": [{"type": "code_execution_20260120", "name": "code_execution"}],
            }

            if self.container_id:
                kwargs["container"] = self.container_id

            if use_files_beta:
                kwargs["extra_headers"] = {"anthropic-beta": "files-api-2025-04-14"}

            print()  # blank line before streaming output

            with self.client.messages.stream(**kwargs) as stream:
                for event in stream:
                    _handle_stream_event(event, collect=lambda t: None)
                    if event.type == "content_block_delta" and hasattr(event, "delta"):
                        if event.delta.type == "text_delta":
                            print(event.delta.text, end="", flush=True)
                            full_text += event.delta.text

                final_message = stream.get_final_message()

            # Track container for state persistence
            if hasattr(final_message, "container") and final_message.container:
                self.container_id = final_message.container.id

            if final_message.stop_reason == "pause_turn":
                # Server-side tool loop hit its limit — resume automatically
                print("\n\n[Resuming analysis...]\n")
                current_messages = list(self.history) + [
                    {"role": "assistant", "content": final_message.content}
                ]
                continue

            break  # end_turn or max_tokens

        print("\n")

        if final_message:
            self.history.append({"role": "assistant", "content": final_message.content})

        return full_text

    def _upload_file(self, file_path: str) -> Optional[str]:
        """Upload a local file via the Files API and return its file_id."""
        path = Path(file_path)
        if not path.exists():
            print(f"  File not found: {file_path}")
            return None

        mime_map = {
            ".csv": "text/csv",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".json": "application/json",
            ".txt": "text/plain",
            ".pdf": "application/pdf",
        }
        mime = mime_map.get(path.suffix.lower(), "application/octet-stream")

        print(f"  Uploading {path.name} ...")
        try:
            with open(path, "rb") as f:
                uploaded = self.client.beta.files.upload(
                    file=(path.name, f, mime),
                )
            self.uploaded_file_ids.append(uploaded.id)
            print(f"  Uploaded as {uploaded.id}")
            return uploaded.id
        except Exception as e:
            print(f"  Upload failed: {e}")
            return None


# ─────────────────────────────────────────────
# Module-level helpers
# ─────────────────────────────────────────────

def _wrangle_with_file_prompt(filename: str) -> str:
    return f"""I have uploaded the file **{filename}**. Please perform a full data wrangling pipeline:

**1. Load & Profile**
   - Load the file, print shape, dtypes, memory usage
   - Show first 5 rows

**2. Data Quality Report**
   - Missing values per column (count + %)
   - Duplicate rows
   - Outlier detection (IQR method) for numeric columns
   - Cardinality of categorical columns

**3. Cleaning**
   - Handle missing values (document strategy for each column)
   - Drop / fix duplicates
   - Fix data type issues
   - Cap or flag outliers as appropriate

**4. Feature Engineering** (if relevant to the analysis plan)
   - Derive useful columns (e.g. date parts, ratios, flags)
   - Encode categoricals where needed

**5. Summary Statistics**
   - Descriptive stats for numeric columns
   - Value counts for key categoricals

After cleaning, save the result as **cleaned_data.csv** and print its shape.
Comment every decision you make."""


def _print_header(label: str):
    if label:
        bar = "─" * 60
        print(f"\n{bar}")
        print(f"  {label}")
        print(bar)


def _handle_stream_event(event, collect):
    """Print non-text progress indicators."""
    if event.type == "content_block_start" and hasattr(event, "content_block"):
        kind = event.content_block.type
        if kind == "thinking":
            print("[Thinking] ", end="", flush=True)
        elif kind == "server_tool_use":
            print("\n[Executing code] ", end="", flush=True)
        elif kind == "bash_code_execution_tool_result":
            print("[Code result] ", end="", flush=True)


def _warn(msg: str) -> str:
    print(f"  Warning: {msg}")
    return msg
