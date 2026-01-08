# src/data_loader.py
import json
import os
import difflib
from collections import defaultdict


class DataLoader:
    """
    Loads all RU-PATH JSON data and builds helper indexes:
    - permits & lots from rupath_parking_base.json
    - buildings + their nearby bus stops from Buildings.json (+ synthetic Yard entry)
    - routes, stop graph, and edge→routes from rutgers_bus_routes.json
    """

    def __init__(self, buildings_path=None, bus_routes_path=None, parking_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.buildings_path = buildings_path or os.path.join(base_dir, "Buildings.json")
        self.bus_routes_path = bus_routes_path or os.path.join(base_dir, "rutgers_bus_routes.json")
        self.parking_path = parking_path or os.path.join(base_dir, "rupath_parking_base.json")

        # main containers
        self.buildings_by_name = {}      # key: normalized name -> {name, campus, bus_stops}
        self.building_stop_map = {}      # key: normalized name -> [canonical stop names]
        self.alias_to_building_key = {}  # alias (normalized) -> canonical building key

        print("📂 Loading all RU-PATH dataset files...")
        self._load_parking()
        self._load_buildings()
        self._load_bus_routes()
        print("✅ All datasets loaded successfully!")

    # ---------- helpers ----------

    def _safe_load(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ JSON file not found: {path}")
        except Exception as e:
            print(f"⚠️ Error reading {path}: {e}")
        return default

    def _norm(self, text: str) -> str:
        return "".join(ch.lower() for ch in text if ch.isalnum() or ch.isspace()).strip()

    # ---------- parking ----------

    def _load_parking(self):
        data = self._safe_load(self.parking_path, {})
        self.parking_raw = data
        self.parking_rules = data  # for compatibility with any older code
        self.permits = data.get("Permits", {})
        self.lots = data.get("Lots", {})

    # ---------- buildings ----------

    def _load_buildings(self):
        raw = self._safe_load(self.buildings_path, {})
        self.buildings = raw
        self.buildings_by_name = {}

        # load from JSON
        for campus, buildings in raw.items():
            for b in buildings:
                name = (b.get("name") or "").strip()
                if not name:
                    continue
                key = self._norm(name)
                self.buildings_by_name[key] = {
                    "name": name,
                    "campus": campus,
                    "bus_stops": b.get("bus_stops", []),
                }

        # ---- synthetic Yard building ----
        yard_name = "The Yard @ College Avenue"
        yard_campus = "College Avenue"
        yard_bus_stops = ["The Yard", "College Avenue Student Center"]
        yard_key = self._norm(yard_name)

        self.buildings_by_name[yard_key] = {
            "name": yard_name,
            "campus": yard_campus,
            "bus_stops": yard_bus_stops,
        }

        # ---- alias map for fuzzy building names ----
        alias_map = {
            # Yard variants
            "the yard": yard_name,
            "yard": yard_name,
            "yard at college ave": yard_name,
            "yard at college avenue": yard_name,
            "yard college ave": yard_name,
            "yard college avenue": yard_name,
            # Common spelling issues
            "hill centre": "Hill Center",
            "hill cntr": "Hill Center",
            "hillcenter": "Hill Center",
            "hill center bus stop": "Hill Center",
            "busch student centre": "Busch Student Center",
        }

        self.alias_to_building_key = {}
        for alias, canonical in alias_map.items():
            alias_key = self._norm(alias)
            canon_key = self._norm(canonical)
            self.alias_to_building_key[alias_key] = canon_key

    # ---------- buses & routes ----------

    def _load_bus_routes(self):
        raw = self._safe_load(self.bus_routes_path, {})
        self.bus_data = raw
        self.routes = raw.get("routes", [])

        # Collect route stop names (canonical names used for the graph)
        route_stop_names = []
        for r in self.routes:
            for stop in r.get("stops", []):
                nm = (stop.get("stop_name") or "").strip()
                if nm:
                    route_stop_names.append(nm)

        self.route_stop_names = sorted(set(route_stop_names))

        # For fuzzy matching we also know building stop labels
        extra_stops = []
        for b in self.buildings_by_name.values():
            for s in b["bus_stops"]:
                extra_stops.append((s or "").strip())
        self.all_stop_names = sorted(set(route_stop_names + extra_stops))

        # Build stop graph + edge→routes map
        self.stop_graph = defaultdict(set)
        self.edge_to_routes = defaultdict(set)

        for r in self.routes:
            rid = r.get("route_id")
            stops = [(s.get("stop_name") or "").strip() for s in r.get("stops", [])]
            for i in range(len(stops) - 1):
                a, b = stops[i], stops[i + 1]
                if not a or not b:
                    continue
                self.stop_graph[a].add(b)
                self.stop_graph[b].add(a)
                self.edge_to_routes[(a, b)].add(rid)
                self.edge_to_routes[(b, a)].add(rid)

        # Pre-resolve building → actual route stop names
        self.building_stop_map = {}
        for key, b in self.buildings_by_name.items():
            resolved = []
            for label in b["bus_stops"]:
                canon = self.resolve_stop_name(label)
                if canon:
                    resolved.append(canon)
            # unique in order
            seen = set()
            uniq = []
            for s in resolved:
                if s not in seen:
                    seen.add(s)
                    uniq.append(s)
            self.building_stop_map[key] = uniq

    # ---------- lookup APIs used by engines ----------

    def resolve_building(self, name):
        """Return building dict or None, with aliases + fuzzy match."""
        if not name:
            return None
        key = self._norm(name)

        # direct match
        if key in self.buildings_by_name:
            return self.buildings_by_name[key]

        # alias mapping (e.g., "yard" -> "The Yard @ College Avenue")
        alias_key = self.alias_to_building_key.get(key)
        if alias_key and alias_key in self.buildings_by_name:
            return self.buildings_by_name[alias_key]

        # fuzzy by key
        candidates = list(self.buildings_by_name.keys())
        matches = difflib.get_close_matches(key, candidates, n=1, cutoff=0.6)
        if matches:
            return self.buildings_by_name[matches[0]]
        return None

    def resolve_stop_name(self, label):
        """
        Map a user / Buildings.json bus_stop label or free-text stop name
        to the closest real route stop name.
        Always returns one of route_stop_names (nodes in the graph) or None.
        """
        if not label:
            return None
        label_clean = label.strip()

        # Exact match first
        for s in self.route_stop_names:
            if s.lower() == label_clean.lower():
                return s

        # Fuzzy by lowercased text
        match = difflib.get_close_matches(
            label_clean.lower(),
            [s.lower() for s in self.route_stop_names],
            n=1,
            cutoff=0.5,
        )
        if match:
            lower_to_canon = {s.lower(): s for s in self.route_stop_names}
            return lower_to_canon.get(match[0])
        return None

    def get_building_stops(self, building):
        """building is the dict returned by resolve_building() or a pseudo-building."""
        if not building:
            return []
        key = self._norm(building["name"])
        return self.building_stop_map.get(key, [])
