# Ground-truth evaluation set for the NexaForge maintenance agent.
#
# EVAL_QUESTIONS: a fixed list of realistic questions, including
# deliberately tricky/ambiguous ones and out-of-scope trick questions.
#
# EXPECTED_TOOL: ground truth for the EXACT tool the router should
# pick, one of: search_manual, check_schedule, machine_info,
# company_info, log_issue, escalate, out_of_scope.
#
# NOTE: this replaced the old binary EXPECTED_ESCALATE (True/False)
# after the system grew from 4 categories to 7. A True/False check
# can no longer tell "correctly routed to out_of_scope" apart from
# "correctly routed to search_manual" — both just look like
# escalate=False. Exact-tool matching is required to actually verify
# the new categories work.

EVAL_QUESTIONS = [
    # --- Should be answerable: CNC Mill X500 ---
    "What is the spindle speed range for the CNC Mill X500?",
    "How often should the X/Y/Z linear guideways be lubricated?",
    "What does error code E-322 mean?",
    "What should I do if the spindle will not start on the CNC Mill X500?",
    "What causes excessive vibration during milling?",
    "Why might coolant not be flowing to the nozzle?",
    "What's the recommended action if backlash exceeds 0.02 mm?",
    "What is the tool changer capacity on the CNC Mill X500?",
    "What pneumatic supply pressure is required?",
    "What is the coolant tank capacity?",

    # --- Should be answerable: Fervi Gear Head Bench Lathe T999 ---
    "What is the spindle speed range of the T999 gear-head bench lathe?",
    "How many main drive belts should we keep in stock for the T999 lathe?",
    "What should I check before starting the T999 lathe for the day?",
    "What causes poor surface finish or chatter on the lathe?",
    "What is the thread cutting range of the T999 lathe?",
    "How often should the drive belt tension be checked on the T999?",

    # --- Should be answerable: Production Flow (document content) ---
    "What machine is used for cutting to length in the production flow?",
    "What happens after milling in the NexaForge production process?",
    "Which machine performs deburring and finishing?",

    # --- Should be answerable: historical log content INSIDE a manual ---
    "Has Machine Asset #X500-07 had any coolant pump issues before?",
    "Which maintenance tasks require a Qualified Technician on the CNC Mill X500?",

    # --- Should be company_info: about NexaForge/platform itself ---
    "What is NexaForge?",
    "Who built this maintenance assistant platform?",

    # --- Should be out_of_scope: no relation to NexaForge at all ---
    "Who is the current Prime Minister of India?",
    "What's 15 times 23?",
    "Who am I?",

    # --- Should be escalate: equipment-related but needs a human ---
    "What's the warranty period on the spindle bearings?",
    "Who is the current supplier for coolant concentrate?",
    "Can you approve overtime for the night shift this week?",

    # --- HARD / AMBIGUOUS: genuinely tricky, could go either way ---
    "Is it safe to disable the chuck guard interlock just to finish a quick job faster?",
    "The CNC Mill keeps throwing E-322 every single day this week, should I keep running it?",
    "Can I substitute a different brand of coolant than what's specified in the manual?",
    "Is the CNC Mill X500 safe to run in an unheated shop during winter?",
    "My coworker says it's fine to run the lathe without safety glasses for a 30-second job, is he right?",
    "The CNC Mill manual and the T999 manual list different bearing service intervals, which one is correct?",
    "What should I do if a maintenance request I logged yesterday hasn't been picked up yet?",
    "Can I keep operating the Hydraulic Press if it's overdue for its oil check by a few hours?",
]

EXPECTED_TOOL = {
    # CNC Mill X500 — manual content
    "What is the spindle speed range for the CNC Mill X500?": "search_manual",
    "How often should the X/Y/Z linear guideways be lubricated?": "check_schedule",
    "What does error code E-322 mean?": "search_manual",
    "What should I do if the spindle will not start on the CNC Mill X500?": "search_manual",
    "What causes excessive vibration during milling?": "search_manual",
    "Why might coolant not be flowing to the nozzle?": "search_manual",
    "What's the recommended action if backlash exceeds 0.02 mm?": "search_manual",
    "What is the tool changer capacity on the CNC Mill X500?": "search_manual",
    "What pneumatic supply pressure is required?": "search_manual",
    "What is the coolant tank capacity?": "search_manual",

    # T999 Lathe — manual content
    "What is the spindle speed range of the T999 gear-head bench lathe?": "search_manual",
    "How many main drive belts should we keep in stock for the T999 lathe?": "search_manual",
    "What should I check before starting the T999 lathe for the day?": "search_manual",
    "What causes poor surface finish or chatter on the lathe?": "search_manual",
    "What is the thread cutting range of the T999 lathe?": "search_manual",
    "How often should the drive belt tension be checked on the T999?": "check_schedule",

    # Production flow / historical log — still manual/document content,
    # NOT live status, even though they name specific machines
    "What machine is used for cutting to length in the production flow?": "search_manual",
    "What happens after milling in the NexaForge production process?": "search_manual",
    "Which machine performs deburring and finishing?": "search_manual",
    "Has Machine Asset #X500-07 had any coolant pump issues before?": "search_manual",
    "Which maintenance tasks require a Qualified Technician on the CNC Mill X500?": "search_manual",

    # Company info
    "What is NexaForge?": "company_info",
    "Who built this maintenance assistant platform?": "company_info",

    # Out of scope — no relation to NexaForge at all
    "Who is the current Prime Minister of India?": "out_of_scope",
    "What's 15 times 23?": "out_of_scope",
    "Who am I?": "out_of_scope",

    # Escalate — equipment/operations-related, needs a human
    "What's the warranty period on the spindle bearings?": "escalate",
    "Who is the current supplier for coolant concentrate?": "escalate",
    "Can you approve overtime for the night shift this week?": "escalate",

    # Hard/ambiguous — labeled by what the manual ACTUALLY contains,
    # not by how "safety-sounding" the question is worded
    "Is it safe to disable the chuck guard interlock just to finish a quick job faster?": "search_manual",
    "The CNC Mill keeps throwing E-322 every single day this week, should I keep running it?": "search_manual",
    "Can I substitute a different brand of coolant than what's specified in the manual?": "escalate",
    "Is the CNC Mill X500 safe to run in an unheated shop during winter?": "search_manual",
    "My coworker says it's fine to run the lathe without safety glasses for a 30-second job, is he right?": "search_manual",
    "The CNC Mill manual and the T999 manual list different bearing service intervals, which one is correct?": "escalate",
    "What should I do if a maintenance request I logged yesterday hasn't been picked up yet?": "escalate",
    # This one is intentionally left as check_schedule, not escalate:
    # from the QUESTION TEXT ALONE (all the router can see), this is a
    # perfectly normal single-machine schedule question. The fact that
    # no Hydraulic Press manual is ingested yet is a *retrieval* gap,
    # not something a router could ever detect from wording alone —
    # so this question is expected to correctly route to
    # check_schedule, but its ANSWER should still come back
    # empty/not-found, which is a separate, honest failure mode.
    "Can I keep operating the Hydraulic Press if it's overdue for its oil check by a few hours?": "check_schedule",
}

# Ground truth: for answerable questions, a few keywords/phrases that
# MUST appear in the answer for it to be considered correct. This is
# what catches "the router picked the right tool, but the answer was
# still wrong" failures — e.g. the tool correctly avoided escalating,
# but retrieval missed the right table row and the answer said
# "not found" anyway. tool_correct alone can't see that; this can.
EXPECTED_KEYWORDS = {
    "What is the spindle speed range for the CNC Mill X500?": ["60", "12,000"],
    "How often should the X/Y/Z linear guideways be lubricated?": ["weekly"],
    "What does error code E-322 mean?": ["coolant", "pump"],
    "What's the recommended action if backlash exceeds 0.02 mm?": ["technician"],
    "What is the tool changer capacity on the CNC Mill X500?": ["24"],
    "What pneumatic supply pressure is required?": ["6.0", "8.0"],
    "What is the coolant tank capacity?": ["180"],
    "What is the spindle speed range of the T999 gear-head bench lathe?": ["70", "2,000"],
    "How many main drive belts should we keep in stock for the T999 lathe?": ["2"],
    "What is the thread cutting range of the T999 lathe?": ["0.4", "7"],
    "How often should the drive belt tension be checked on the T999?": ["monthly"],
    "Is it safe to disable the chuck guard interlock just to finish a quick job faster?": ["not", "disable"],
    "Is the CNC Mill X500 safe to run in an unheated shop during winter?": ["5", "40"],
    "My coworker says it's fine to run the lathe without safety glasses for a 30-second job, is he right?": ["safety glasses"],
}