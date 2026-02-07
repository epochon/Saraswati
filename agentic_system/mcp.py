def mcp(sender, receiver, msg_type, payload, round_no):
    return {
        "round": round_no,
        "from": sender,
        "to": receiver,
        "type": msg_type,
        "payload": payload
    }
