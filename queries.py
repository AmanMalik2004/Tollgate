GROUPS = [
    ("How many days of paid annual leave do employees get?",
     ["What's the yearly vacation allowance?", "How much annual leave do I receive per year?"]),
    ("How many sick days do full-time employees get?",
     ["What is the paid sick leave allowance?", "How many sick days per year do I have?"]),
    ("How much is the home-office stipend?",
     ["What's the remote work equipment allowance?", "How much money do I get for my home office?"]),
    ("What are the core hours for remote employees?",
     ["During what hours must remote staff be reachable?", "When do I need to be online on Slack?"]),
    ("How long is parental leave for the primary caregiver?",
     ["How many weeks off does the main caregiver get?", "Primary caregiver parental leave length?"]),
    ("How much can I be reimbursed for meals during travel?",
     ["What's the daily meal limit on business trips?", "Meal reimbursement cap when travelling?"]),
    ("How many unused leave days can be carried over?",
     ["What's the carryover limit for annual leave?", "Can I roll over vacation days to next year?"]),
    ("Compare the remote work policy and the leave policy and explain how they work together.",
     ["Explain how the remote work rules and leave rules interact.",
      "How do the remote work and leave policies fit together?"]),
    ("Explain the approval process for travel expenses and why it matters.",
     ["Walk me through how expenses get approved and reimbursed.",
      "Why do large expenses need approval, and how does reimbursement work?"]),
    ("How long does expense reimbursement take?",
     ["How fast do I get my expense money back?", "What's the reimbursement turnaround time?"]),
]

# Related-sounding questions that are NOT in the cache. A cache hit on these = wrong answer.
UNRELATED = [
    "How many public holidays are there each year?",
    "What is the dress code in the office?",
    "What is the notice period for resigning?",
    "What is the company's health insurance coverage?",
    "Is there a gym membership benefit?",
    "How do I reset my work laptop password?",
    "What is the CEO's favorite color?",
]

# Nearly identical to a cached question, but the correct answer is DIFFERENT.
# A cache hit on any of these returns a wrong answer.
HARD_NEGATIVES = [
    "How long is parental leave for the secondary caregiver?",
    "How many days of unpaid leave do employees get?",
    "What are the core hours for office employees?",
    "How long does expense approval take?",
    "How much can I be reimbursed for hotel stays during travel?",
    "How many sick days do part-time employees get?",
    "How much is the stipend for office furniture?",
    "How many unused sick days can be carried over?",
]