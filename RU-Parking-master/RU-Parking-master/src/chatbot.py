# src/chatbot.py
import os
import re

from .parking_logic import ParkingRecommendationEngine
from .routing_engine import RoutingEngine


class ParkingChatbot:
    """
    Chat layer:
      1. Try to answer from JSON (parking + bus routing).
      2. If JSON can't handle it, fall back to DeepSeek (if DEEPSEEK_API_KEY is set).

    Supports:
      - "parking" only
      - "bus" only
      - "both" (explain that user can ask one type at a time)
    """

    def __init__(self, data_loader):
        self.data = data_loader
        self.logic = ParkingRecommendationEngine(data_loader)
        self.routing = RoutingEngine(data_loader)
        self.sessions = {}

    # ---------- session helper ----------

    def _get_ctx(self, session_id):
        if not session_id:
            session_id = "default"
        ctx = self.sessions.setdefault(session_id, {})
        if "mode" not in ctx:
            ctx["mode"] = None   # "parking", "bus", "both"
        return ctx, session_id

    # ---------- main entrypoint ----------

    def chat(self, user_message: str, session_id: str | None = None) -> str:
        ctx, session_id = self._get_ctx(session_id)
        text = (user_message or "").strip()
        if not text:
            return "Please type a question about Rutgers **parking** or **buses**."

        lower = text.lower()
        tokens = re.findall(r"\b\w+\b", lower)
        token_set = set(tokens)

        # word-level detection (no more 'bus' inside 'busch' bug)
        wants_parking = any(w in token_set for w in ["park", "parking", "lot", "permit", "commuter", "resident"])
        wants_bus = any(w in token_set for w in ["bus", "buses", "route", "routes", "shuttle", "shuttles", "stop", "stops"])

        # detect origin/destination
        origin_name, dest_name = self._extract_origin_dest(text)

        # ---------- explicit mode commands ----------

        if lower in {"parking", "parking question", "park"}:
            ctx["mode"] = "parking"
            return (
                "Tell me your permit type and campus, for example:\n"
                "- \"Livingston Commuter permit on Busch\"\n"
                "- \"College Ave Commuter permit on Livingston\""
            )

        if lower in {"bus", "bus question", "buses"}:
            ctx["mode"] = "bus"
            return (
                "For bus routes, tell me both your starting building and destination, for example:\n"
                "- \"From Hill Center to Livingston Student Center\"\n"
                "- \"From The Yard to Busch Student Center\""
            )

        if lower in {"both", "parking and bus", "bus and parking"}:
            ctx["mode"] = "both"
            return (
                "Great, I can help with **both parking and buses**.\n\n"
                "Ask one question at a time, for example:\n"
                "- Parking: \"I have a Livingston Commuter permit, where can I park on Busch?\"\n"
                "- Bus: \"From Hill Center to The Yard, which bus should I take?\""
            )

        mode = ctx.get("mode")

        # ---------- decision: parking vs bus ----------

        is_bus_like = wants_bus or ("from " in lower and " to " in lower) or (
            "starting building" in lower and "destination" in lower
        )
        is_parking_like = wants_parking

        intent = None
        if is_bus_like and not is_parking_like:
            intent = "bus"
        elif is_parking_like and not is_bus_like:
            intent = "parking"
        elif is_bus_like and is_parking_like:
            intent = mode or "parking"  # default to parking
        else:
            intent = mode

        # ---------- simple help ----------

        if lower in {"help", "menu", "options"} or intent is None:
            return (
                "Hi! I can help with:\n"
                "- **Parking rules** (permits, allowed lots, time windows)\n"
                "- **Bus routes** between buildings or major stops\n\n"
                "Say **\"parking\"**, **\"bus\"**, or **\"both\"** to get started.\n"
                "Or ask something like:\n"
                "- \"Where can I park with a Livingston Commuter permit on Busch?\"\n"
                "- \"From Hill Center to The Yard, which bus should I take?\""
            )

        ctx["mode"] = intent  # keep mode consistent

        # ---------- bus routing from JSON ----------

        if intent == "bus":
            if origin_name and dest_name:
                plan = self.routing.plan_building_to_building(origin_name, dest_name)
                if plan.get("type") == "bus_route":
                    return self.routing.describe_plan(plan)
                return self._deepseek_fallback(user_message, fallback_msg=plan.get("message"))

            if origin_name or dest_name:
                missing = "origin" if not origin_name else "destination"
                return (
                    f"Tell me your {missing} as well, for example:\n"
                    "\"From Hill Center to The Yard\"."
                )
            return (
                "For bus routes, tell me both your starting building and destination, for example:\n"
                "\"From Hill Center to Livingston Student Center\"."
            )

        # ---------- parking from JSON ----------

        if intent == "parking":
            permit, campus = self._extract_permit_and_campus(text)
            if not permit and "commuter" in token_set:
                permit = self._guess_permit_name(lower)

            if permit:
                ans = self.logic.find_parking(permit, campus)
                if ans.get("type") == "parking":
                    return self.logic.describe_parking(ans)
                return self._deepseek_fallback(user_message, fallback_msg=ans.get("message"))

            return (
                "Tell me your permit type and campus, for example:\n"
                "\"Livingston Commuter permit on Busch\" or\n"
                "\"College Ave Commuter – where can I park on Livingston?\""
            )

        # ---------- generic question → DeepSeek / fallback ----------

        return self._deepseek_fallback(user_message)

    # ---------- tiny NLU helpers ----------

    def _extract_origin_dest(self, text: str):
        """
        Very simple patterns:
          - 'from X to Y'
          - 'starting building X ... destination Y'
        """
        lower = text.lower()
        origin = dest = None

        # pattern 1: "from X to Y"
        if "from " in lower and " to " in lower:
            try:
                after_from = text.lower().split("from ", 1)[1]
                part_origin, part_dest = after_from.split(" to ", 1)
                origin = part_origin.strip(" ,.;:\"'")
                dest = part_dest.strip(" ,.;:\"'")
            except ValueError:
                pass

        # pattern 2: "starting building X ... destination Y"
        if (not origin) and "starting building" in lower and "destination" in lower:
            try:
                s = text
                after_start = s.lower().split("starting building", 1)[1]
                part1, part2 = after_start.split("destination", 1)
                origin = (
                    part1.replace("is", "").replace(":", "").strip(" ,.;:\"'")
                )
                dest = part2.replace("is", "").replace(":", "").strip(" ,.;:\"'")
            except Exception:
                pass

        return origin, dest

    def _extract_permit_and_campus(self, text: str):
        lower = text.lower()
        permit = None
        campus = None

        for p in self.data.permits.keys():
            if p.lower() in lower:
                permit = p
                break

        campuses = [
            "busch",
            "livingston",
            "college ave",
            "college avenue",
            "cook",
            "douglass",
            "cook/douglass",
        ]
        for c in campuses:
            if c in lower:
                campus = c
                break

        return permit, campus

    def _guess_permit_name(self, lower: str):
        for p in self.data.permits.keys():
            first_word = p.split()[0].lower()
            if first_word in lower and "commuter" in lower:
                return p
        return None

    # ---------- DeepSeek / LLM fallback ----------

    def _deepseek_fallback(self, user_message: str, fallback_msg: str | None = None) -> str:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return fallback_msg or (
                "I couldn't answer that directly from the RU-PATH JSON data. "
                "Please check the official Rutgers Parking & Transportation website "
                "or the Rutgers mobile app for the latest info."
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are RU-PATH, a Rutgers New Brunswick Parking & Transit assistant. "
                            "Use real Rutgers rules when possible; if unsure, say you are unsure "
                            "and recommend checking the official Rutgers website or app."
                        ),
                    },
                    {"role": "user", "content": user_message},
                ],
                max_tokens=400,
            )
            return resp.choices[0].message.content
        except Exception as e:
            if fallback_msg:
                return fallback_msg + f"\n\n(DeepSeek fallback error: {e})"
            return (
                "I couldn't answer that from the RU-PATH JSON data, and the DeepSeek API call failed. "
                "Please double-check using the official Rutgers Parking & Transportation website."
            )
