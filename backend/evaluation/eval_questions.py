# Ground-truth evaluation set for the NexaForge maintenance agent.
#
# EVAL_QUESTIONS: a fixed list of realistic questions — mostly answerable
# from the ingested manuals (CNC Mill X500, Fervi Gear Head Bench Lathe
# T999, NexaForge Production Flow), plus a few deliberately out-of-scope
# "trick" questions.
#
# EXPECTED_ESCALATE: ground truth for whether the agent SHOULD classify
# the question as "escalate". True = correctly unanswerable from the
# manuals. Anything not listed here defaults to False (should be
# answered, not escalated).

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

    # --- Should be answerable: Production Flow ---
    "What machine is used for cutting to length in the production flow?",
    "What happens after milling in the NexaForge production process?",
    "Which machine performs deburring and finishing?",

    # --- Should be answerable: cross-document / maintenance-log style ---
    "Has Machine Asset #X500-07 had any coolant pump issues before?",
    "Which maintenance tasks require a Qualified Technician on the CNC Mill X500?",

    # --- Should escalate: genuinely not in any manual ---
    "What's the warranty period on the spindle bearings?",
    "Who is the current supplier for coolant concentrate?",
    "What's the current stock market price of NexaForge shares?",
    "Can you approve overtime for the night shift this week?",
]

# Ground truth for whether the agent SHOULD classify the question as
# "escalate". True = correctly unanswerable from the manuals. Anything
# not listed here defaults to False (should be answered, not escalated).
EXPECTED_ESCALATE = {
    "What's the warranty period on the spindle bearings?": True,
    "Who is the current supplier for coolant concentrate?": True,
    "What's the current stock market price of NexaForge shares?": True,
    "Can you approve overtime for the night shift this week?": True,
}

# Ground truth: for answerable questions, a few keywords/phrases that
# MUST appear in the answer for it to be considered correct. This is
# what catches "the router picked the right tool, but the answer was
# still wrong" failures — e.g. the tool correctly avoided escalating,
# but retrieval missed the right table row and the answer said
# "not found" anyway. escalate_correct alone can't see that; this can.
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
}