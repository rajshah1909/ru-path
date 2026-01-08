# src/parking_logic.py

class ParkingRecommendationEngine:
    """
    Rule-based engine that uses rupath_parking_base.json to answer:
      - Where can I park with PERMIT on CAMPUS?
      - What lots / hours / notes exist for a permit?
    """

    def __init__(self, data_loader):
        self.data = data_loader

    def reset(self):
        # No per-session state yet; stub exists for /api/reset
        pass

    def find_parking(self, permit_name: str, campus: str | None = None):
        permits = self.data.permits or {}

        if not permit_name:
            return {"type": "error", "message": "I need a permit name to look up parking rules."}

        # case-insensitive match
        exact_key = None
        for k in permits.keys():
            if k.lower() == permit_name.lower():
                exact_key = k
                break

        if exact_key is None:
            return {
                "type": "error",
                "message": f"I couldn't find a permit called '{permit_name}' in rupath_parking_base.json.",
            }

        permit_block = permits[exact_key]
        entries = []

        for campus_name, rules in permit_block.items():
            if campus and campus.lower() not in campus_name.lower():
                continue
            for rule in rules:
                entries.append(
                    {
                        "campus": campus_name,
                        "access_type": rule.get("Type"),
                        "lots": rule.get("Lots", []),
                        "hours": rule.get("Hours", {}),
                        "notes": rule.get("Notes"),
                    }
                )

        if not entries:
            if campus:
                return {
                    "type": "error",
                    "message": f"'{exact_key}' doesn't seem to allow parking on {campus} in the current JSON.",
                }
            return {
                "type": "error",
                "message": f"I couldn't find any lots for the permit '{exact_key}' in the JSON.",
            }

        return {"type": "parking", "permit": exact_key, "entries": entries}

    def describe_parking(self, result: dict) -> str:
        if not result or result.get("type") != "parking":
            return result.get("message", "I couldn't find matching parking rules in the JSON.")

        permit = result["permit"]
        lines = [f"Parking options for **{permit}**:"]

        for e in result["entries"]:
            lots = ", ".join(e["lots"]) if e["lots"] else "no specific lots listed"
            hours = (
                ", ".join(f"{k}: {v}" for k, v in e["hours"].items())
                if e["hours"]
                else "see Rutgers parking website"
            )
            note = f" Notes: {e['notes']}" if e.get("notes") else ""
            lines.append(
                f"- **{e['campus']}** ({e['access_type']}): {lots}. Hours: {hours}.{note}"
            )

        return "\n".join(lines)
