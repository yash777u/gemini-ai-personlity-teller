"""
🧪 Backend Service Test Unit
Tests the scoring logic and AI results generation with mock data.
"""

import json
import os
from scoring import calculate_scores
from ai_results import generate_results
from dotenv import load_dotenv

# Load key for AI test
load_dotenv()

def run_backend_test():
    print("🚀 Starting Backend Service Test...")
    
    # 1. Load questions
    q_path = "question.txt"
    if not os.path.exists(q_path):
        print(f"❌ Error: {q_path} not found.")
        return

    with open(q_path, "r") as f:
        questions_data = json.load(f)
        questions = questions_data["questions"]

    # 2. Mock Response Data (Realistic-ish)
    # 50 questions, mostly middle-high scores
    mock_responses = {
        # EXT
        "EXT1": 5, "EXT2": 2, "EXT3": 4, "EXT4": 2, "EXT5": 5,
        "EXT6": 1, "EXT7": 5, "EXT8": 2, "EXT9": 5, "EXT10": 1,
        # AGR
        "AGR1": 2, "AGR2": 4, "AGR3": 1, "AGR4": 5, "AGR5": 2,
        "AGR6": 5, "AGR7": 1, "AGR8": 5, "AGR9": 5, "AGR10": 5,
        # CSN
        "CSN1": 5, "CSN2": 1, "CSN3": 5, "CSN4": 1, "CSN5": 5,
        "CSN6": 1, "CSN7": 5, "CSN8": 1, "CSN9": 5, "CSN10": 5,
        # EST
        "EST1": 2, "EST2": 5, "EST3": 2, "EST4": 5, "EST5": 1,
        "EST6": 1, "EST7": 1, "EST8": 1, "EST9": 1, "EST10": 1,
        # OPN
        "OPN1": 5, "OPN2": 1, "OPN3": 5, "OPN4": 1, "OPN5": 5,
        "OPN6": 1, "OPN7": 5, "OPN8": 4, "OPN9": 5, "OPN10": 5
    }

    # 3. Test Scoring Engine
    print("\n📊 Testing Scoring Engine...")
    scores = calculate_scores(mock_responses, questions)
    
    print(f"✅ Overall Score: {scores['overall_pct']}% ({scores['overall_level']})")
    for cat, data in scores["category_scores"].items():
        print(f"   - {cat}: {data['pct']}% ({data['level']})")
    
    if scores["flags"]:
        print("\n🚩 Flags Detected:")
        for flag in scores["flags"]:
            print(f"   - {flag}")
    else:
        print("\n✨ No unusual patterns detected (Mock data is clean).")

    # 4. Test AI Results (Optional: requires GEMINI_API_KEY)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("\n🤖 Testing AI Results (Gemini API)...")
        results = generate_results(api_key, scores)
        
        if "error" in results:
            print(f"❌ Gemini Error: {results['error']}")
        else:
            print("✅ AI Results generated successfully!")
            print(f"   - Summary (Section B) preview: {results['b'][:100]}...")
    else:
        print("\n⚠️ Skipping AI test: GEMINI_API_KEY not found in .env")

    print("\n🏁 Test Completed Successfully!")

if __name__ == "__main__":
    run_backend_test()
