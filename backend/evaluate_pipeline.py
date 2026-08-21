import os
import sys
import json

# Ensure the script can find your local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.run import run_agent

def calculate_live_escalate_rate():
    # 1. Point to the generated questions for your specific manual
    json_path = os.path.join("generated_questions", "CNC Mill X500 (Model X500-3AX).json")
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}. Make sure the file exists!")
        return

    # 2. Load the questions
    with open(json_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    # --- THE FIX: Limit to the first 30 questions ---
    questions_data = questions_data[:30]
    # ------------------------------------------------

    total_questions = len(questions_data)
    if total_questions == 0:
        print("No questions found in the JSON file.")
        return

    escalated_count = 0

    print(f"Starting pipeline test with {total_questions} questions...")
    print("-" * 50)

    # 3. Loop through every question and send it to the LLM
    for i, q_item in enumerate(questions_data, start=1):
        question_text = q_item["question"]
        print(f"[{i}/{total_questions}] Asking: {question_text}")
        
        try:
            # Feed the question into your live RAG pipeline
            result = run_agent(question_text, session_id="pipeline_eval_test")
            
            # Fetch which tool the AI decided to use
            tool_used = result.get("tool_used")
            
            if tool_used == "escalate":
                escalated_count += 1
                print("  -> Result: ESCALATED ⚠️")
            else:
                print(f"  -> Result: Answered successfully using '{tool_used}'")
                
        except Exception as e:
            # If Groq throws a rate limit error, catch it so the script doesn't crash
            print(f"  -> Result: ERROR ({type(e).__name__}) - Skipping...")
            escalated_count += 1 # Count API failures as escalations for safety

    # 4. Calculate the Escalate Rate percentage
    escalate_rate = (escalated_count / total_questions) * 100

    # 5. Print the final report
    print("\n" + "="*50)
    print("   RAG PIPELINE ESCALATE RATE REPORT")
    print("="*50)
    print(f"Manual Tested:          CNC Mill X500")
    print(f"Total Questions Asked:  {total_questions}")
    print(f"Total Escalations:      {escalated_count}")
    print(f"Live Escalate Rate:     {escalate_rate:.2f}%")
    print("="*50)

if __name__ == "__main__":
    calculate_live_escalate_rate()