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

    # --- HARD / AMBIGUOUS: genuinely tricky, could go either way ---
    # These are deliberately borderline so escalation accuracy isn't
    # artificially perfect — a reasonable router could plausibly get
    # these wrong, unlike the obviously off-topic questions above.
    "Is it safe to disable the chuck guard interlock just to finish a quick job faster?",
    "The CNC Mill keeps throwing E-322 every single day this week, should I keep running it?",
    "Can I substitute a different brand of coolant than what's specified in the manual?",
    "Is the CNC Mill X500 safe to run in an unheated shop during winter?",
    "My coworker says it's fine to run the lathe without safety glasses for a 30-second job, is he right?",
    "The CNC Mill manual and the T999 manual list different bearing service intervals, which one is correct?",
    "What should I do if a maintenance request I logged yesterday hasn't been picked up yet?",
    "Can I keep operating the Hydraulic Press if it's overdue for its oil check by a few hours?",
]

# Ground truth for whether the agent SHOULD classify the question as
# "escalate". True = correctly unanswerable from the manuals. Anything
# not listed here defaults to False (should be answered, not escalated).
EXPECTED_ESCALATE = {
    "What's the warranty period on the spindle bearings?": True,
    "Who is the current supplier for coolant concentrate?": True,
    "What's the current stock market price of NexaForge shares?": True,
    "Can you approve overtime for the night shift this week?": True,

    # Hard/ambiguous ones — labeled False where the manual actually
    # DOES contain a direct answer (even though the question SOUNDS
    # like it needs human judgment), and True where it genuinely
    # doesn't, regardless of how "answerable" it sounds on the surface.
    "Is it safe to disable the chuck guard interlock just to finish a quick job faster?": False,
    # False: the lathe manual explicitly says never disable guards/interlocks —
    # this is a direct quote from Section 2, not a judgment call.

    "The CNC Mill keeps throwing E-322 every single day this week, should I keep running it?": False,
    # False: E-322 has a documented troubleshooting entry (clean strainer, cool
    # pump). The "keep running" framing sounds like a decision, but the manual
    # answer (clean the strainer) is directly retrievable.

    "Can I substitute a different brand of coolant than what's specified in the manual?": True,
    # True: no manual specifies an approved coolant brand or discusses
    # substitution — genuinely not covered.

    "Is the CNC Mill X500 safe to run in an unheated shop during winter?": False,
    # False: the manual states an explicit operating temperature range
    # (5°C-40°C) — directly answerable from the spec table.

    "My coworker says it's fine to run the lathe without safety glasses for a 30-second job, is he right?": False,
    # False: the lathe manual's safety section explicitly requires ANSI
    # safety glasses at all times — directly answerable, no judgment needed.

    "The CNC Mill manual and the T999 manual list different bearing service intervals, which one is correct?": True,
    # True: comparing/reconciling two separate documents' schedules isn't
    # something either manual addresses on its own — needs a human call.

    "What should I do if a maintenance request I logged yesterday hasn't been picked up yet?": True,
    # True: no manual covers ticket/request follow-up procedures — that's
    # an operational/process question, not equipment content.

    "Can I keep operating the Hydraulic Press if it's overdue for its oil check by a few hours?": True,
    # True: no manual was ingested for the Hydraulic Press yet, so there's
    # nothing to retrieve this from regardless of how the question is framed.
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

    # Hard/ambiguous questions expected to be answered (not escalated) —
    # keywords proving the answer actually came from the right manual
    # content, not a vague/generic-sounding non-answer.
    "Is it safe to disable the chuck guard interlock just to finish a quick job faster?": ["not", "disable"],
    "Is the CNC Mill X500 safe to run in an unheated shop during winter?": ["5", "40"],
    "My coworker says it's fine to run the lathe without safety glasses for a 30-second job, is he right?": ["safety glasses"],
}