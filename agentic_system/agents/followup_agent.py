def followup_decision(status, days_pending):
    if status == "SUBMITTED" and days_pending > 7:
        return "ESCALATE"
    return "WAIT"
