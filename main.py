#!/usr/bin/env python3
"""
AI Analyst Helper — Interactive CLI

Usage:
  python main.py              # interactive menu
  python main.py --demo       # run a built-in demo analysis
  python main.py --workflow   # guided full-workflow wizard
"""

import sys
from analyst import AnalystHelper


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                    AI ANALYST HELPER                         ║
║                                                              ║
║  1. Frame    2. Plan    3. Wrangle    4. Deep Dive    5. Story║
╚══════════════════════════════════════════════════════════════╝
"""

MENU = """
┌─────────────────────────────────────────────┐
│  SKILLS                                     │
│   1  Frame the Analysis                     │
│   2  Create Analysis Plan                   │
│   3  Wrangle Data                           │
│   4  Deep Dive Analysis                     │
│   5  Tell the Story / Build Presentation    │
│                                             │
│  UTILITIES                                  │
│   6  Ask a Follow-up Question               │
│   7  Show Session Summary                   │
│   8  Run Full Workflow (wizard)             │
│   9  Exit                                   │
└─────────────────────────────────────────────┘
"""


# ─────────────────────────────────────────────────────────────
# Interactive menu
# ─────────────────────────────────────────────────────────────

def run_interactive():
    print(BANNER)
    analyst = AnalystHelper()

    handlers = {
        "1": _skill_frame,
        "2": _skill_plan,
        "3": _skill_wrangle,
        "4": _skill_deep_dive,
        "5": _skill_story,
        "6": _skill_followup,
        "7": _skill_summary,
        "8": _run_full_workflow,
    }

    while True:
        print(MENU)
        choice = input("Select (1-9): ").strip()

        if choice == "9":
            _exit(analyst)
            break

        handler = handlers.get(choice)
        if handler:
            handler(analyst)
        else:
            print("  Invalid choice — please enter 1–9.")


# ─────────────────────────────────────────────────────────────
# Skill handlers
# ─────────────────────────────────────────────────────────────

def _skill_frame(analyst: AnalystHelper):
    print()
    problem = _prompt_multiline(
        "Describe your business problem or analytical question\n"
        "(Enter a blank line when done)"
    )
    if problem:
        analyst.frame_analysis(problem)


def _skill_plan(analyst: AnalystHelper):
    if not analyst.context["problem"]:
        print("  Please run Analysis Framing first (option 1).")
        return
    analyst.create_plan()


def _skill_wrangle(analyst: AnalystHelper):
    print("\n  Data source options:")
    print("    1  Upload a local file (CSV, Excel, JSON)")
    print("    2  Describe data in text")
    print("    3  Let the AI propose a mock dataset")
    sub = input("  Choose (1-3): ").strip()

    if sub == "1":
        path = input("  File path: ").strip()
        analyst.wrangle_data(file_path=path)
    elif sub == "2":
        desc = _prompt_multiline(
            "  Describe your dataset (columns, rows, time range, etc.)\n"
            "  (blank line when done)"
        )
        analyst.wrangle_data(data_description=desc)
    else:
        analyst.wrangle_data()


def _skill_deep_dive(analyst: AnalystHelper):
    focus = input(
        "\n  Optional focus area (e.g. 'churn drivers' or press Enter to skip): "
    ).strip()
    analyst.deep_dive(focus_area=focus or None)


def _skill_story(analyst: AnalystHelper):
    print("\n  Target audience:")
    print("    1  Executive (C-suite) — default")
    print("    2  Technical (data team)")
    print("    3  Business (managers / stakeholders)")
    print("    4  General (mixed)")
    sub = input("  Choose (1-4, default=1): ").strip() or "1"
    audience_map = {"1": "executive", "2": "technical", "3": "business", "4": "general"}
    analyst.tell_story(audience=audience_map.get(sub, "executive"))


def _skill_followup(analyst: AnalystHelper):
    question = _prompt_multiline(
        "  Your question (blank line when done)"
    )
    if question:
        analyst.ask(question)


def _skill_summary(analyst: AnalystHelper):
    s = analyst.summary()
    print("\n  ── SESSION SUMMARY ─────────────────────")
    print(f"  Problem      : {s['problem'] or '(not set)'}")
    print(f"  Phases done  : {', '.join(s['phases_completed']) or 'none'}")
    print(f"  Turns        : {s['conversation_turns']}")
    print(f"  Files        : {s['files_uploaded']}")
    print(f"  Container ID : {s['container_id'] or 'none'}")
    print("  ────────────────────────────────────────")


# ─────────────────────────────────────────────────────────────
# Guided full workflow
# ─────────────────────────────────────────────────────────────

def _run_full_workflow(analyst: AnalystHelper):
    """Walk the user through all five skills in sequence."""
    print("\n  ── FULL WORKFLOW WIZARD ─────────────────")
    print("  This will guide you through all five skills.\n")

    # 1. Frame
    problem = _prompt_multiline(
        "  STEP 1 — What is your analysis problem or question?\n"
        "  (blank line when done)"
    )
    if not problem:
        print("  No problem entered. Exiting wizard.")
        return
    analyst.frame_analysis(problem)
    _pause()

    # 2. Plan
    analyst.create_plan()
    _pause()

    # 3. Wrangle
    print("\n  STEP 3 — Data Wrangling")
    print("  Do you have a data file to upload? (y/n)")
    if input("  > ").strip().lower() == "y":
        path = input("  File path: ").strip()
        analyst.wrangle_data(file_path=path)
    else:
        desc = _prompt_multiline(
            "  Describe your data briefly (or press Enter to use a mock dataset)\n"
            "  (blank line when done)"
        )
        analyst.wrangle_data(data_description=desc or None)
    _pause()

    # 4. Deep dive
    focus = input("\n  STEP 4 — Deep Dive. Specific focus? (Enter to skip): ").strip()
    analyst.deep_dive(focus_area=focus or None)
    _pause()

    # 5. Story
    print("\n  STEP 5 — Storytelling")
    print("  Target audience? (1=Executive, 2=Technical, 3=Business, 4=General)")
    sub = input("  > ").strip() or "1"
    audience_map = {"1": "executive", "2": "technical", "3": "business", "4": "general"}
    analyst.tell_story(audience=audience_map.get(sub, "executive"))

    print("\n  ── ANALYSIS COMPLETE ────────────────────")
    _skill_summary(analyst)


# ─────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────

DEMO_PROBLEM = (
    "Our e-commerce platform's monthly revenue has dropped 18% over the last "
    "three quarters. Leadership wants to understand the root causes and identify "
    "the highest-impact levers to reverse the trend before end of year."
)

DEMO_DATA_DESC = """
We have three tables:
- orders: order_id, customer_id, order_date, product_category, revenue, units_sold, discount_pct, return_flag
- customers: customer_id, acquisition_channel, customer_segment, country, first_order_date, lifetime_orders
- products: product_id, category, subcategory, unit_price, unit_cost, brand

Dataset covers Jan 2023 – Dec 2024, ~85,000 orders across 5 product categories
(Electronics, Apparel, Home & Garden, Sports, Beauty).
"""


def run_demo():
    print(BANNER)
    print("  DEMO: E-Commerce Revenue Decline Analysis\n")
    analyst = AnalystHelper()

    analyst.frame_analysis(DEMO_PROBLEM)
    _pause("  Press Enter to continue to Analysis Planning...")

    analyst.create_plan()
    _pause("  Press Enter to continue to Data Wrangling...")

    analyst.wrangle_data(data_description=DEMO_DATA_DESC)
    _pause("  Press Enter to continue to Deep Dive...")

    analyst.deep_dive()
    _pause("  Press Enter to continue to Storytelling...")

    analyst.tell_story(audience="executive")

    print("\n  ── DEMO COMPLETE ──")
    _skill_summary(analyst)
    analyst.cleanup()


# ─────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────

def _prompt_multiline(prompt: str) -> str:
    """Collect multi-line input until a blank line."""
    print(f"\n  {prompt}")
    lines = []
    while True:
        line = input("  > ")
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _pause(msg: str = "  Press Enter to continue..."):
    input(msg)


def _exit(analyst: AnalystHelper):
    print("\n  Cleaning up uploaded files...")
    analyst.cleanup()
    print("  Goodbye!\n")


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    elif "--workflow" in sys.argv:
        analyst = AnalystHelper()
        _run_full_workflow(analyst)
        analyst.cleanup()
    else:
        run_interactive()
