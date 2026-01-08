# src/routing_engine.py
from collections import deque
from typing import List, Dict, Any, Optional, Tuple


class RoutingEngine:
    """
    Computes bus routes between buildings or stops using data from DataLoader:
    - Buildings.json              → building → nearby bus stops
    - rutgers_bus_routes.json     → stop graph + edge→routes

    Strategy (Hybrid C):
      1. Resolve origin & destination:
         - if it's a building → use its nearby stops
         - if it's not a building but matches a bus stop → use that stop directly
      2. Try to find a direct single bus route between some origin_stop and dest_stop.
         - If found, use that direct line.
      3. Otherwise, run BFS on the stop graph to find the shortest stop path and
         compress it into route legs using edge→routes.
    """

    def __init__(self, data_loader) -> None:
        self.data = data_loader  # DataLoader instance

    # ----------------- internal helpers -----------------

    def _shortest_path_between_stops(self, start: str, goal: str) -> Optional[List[str]]:
        """
        Unweighted shortest path (BFS) on the stop graph.
        Nodes are canonical stop names from rutgers_bus_routes.json
        (e.g., "Hill Center", "Livingston Student Center").
        """
        if start == goal:
            return [start]

        graph = self.data.stop_graph
        if start not in graph or goal not in graph:
            return None

        q = deque([start])
        prev: Dict[str, Optional[str]] = {start: None}

        while q:
            u = q.popleft()
            for v in graph[u]:
                if v in prev:
                    continue
                prev[v] = u
                if v == goal:
                    # reconstruct path
                    path = [v]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    path.reverse()
                    return path
                q.append(v)

        return None

    def _best_bfs_path(
        self, origin_stops: List[str], dest_stops: List[str]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        Try all origin_stop × dest_stop pairs and choose the path
        with the fewest stop hops (for BFS fallback).
        """
        best: Optional[Tuple[str, str, List[str]]] = None

        for s in origin_stops:
            for t in dest_stops:
                path = self._shortest_path_between_stops(s, t)
                if not path:
                    continue
                if best is None or len(path) < len(best[2]):
                    best = (s, t, path)

        return best

    def _direct_path_between_stops(self, start: str, goal: str) -> Optional[Tuple[str, List[str]]]:
        """
        Look for a single bus route that contains both stops.
        Returns (route_id, stop_path) if found, else None.
        stop_path is the sublist of that route's stops from start → goal.
        """
        best: Optional[Tuple[str, List[str]]] = None

        for r in self.data.routes:
            rid = r.get("route_id")
            stops = [(s.get("stop_name") or "").strip() for s in r.get("stops", [])]
            if start not in stops or goal not in stops:
                continue

            i1 = stops.index(start)
            i2 = stops.index(goal)
            if i1 <= i2:
                sub = stops[i1 : i2 + 1]
            else:
                sub = list(reversed(stops[i2 : i1 + 1]))

            if not best or len(sub) < len(best[1]):
                best = (rid, sub)

        return best

    def _build_legs(self, path: List[str]) -> List[Dict[str, Any]]:
        """
        Given a list of stops [s0, s1, ..., sn], compress it into route legs:
        [
          { "route_id": "B", "from_stop": "Hill Center",
            "to_stop": "Livingston Student Center", "stops": [...] },
          ...
        ]
        Uses edge_to_routes from DataLoader to infer which bus line covers each edge.
        """
        legs: List[Dict[str, Any]] = []
        if len(path) < 2:
            return legs

        edges = list(zip(path, path[1:]))
        edge_routes = self.data.edge_to_routes  # (a, b) -> set(route_ids)

        i = 0
        while i < len(edges):
            a, b = edges[i]
            possible_routes = list(edge_routes.get((a, b), []))
            route = possible_routes[0] if possible_routes else None

            j = i + 1
            while j < len(edges):
                c, d = edges[j]
                routes_j = edge_routes.get((c, d), set())

                # if we already chose a route and it doesn't cover the next edge, stop the leg
                if route is not None and route not in routes_j:
                    break

                # if we don't yet have a route, and the next edge has one, adopt it
                if route is None and routes_j:
                    route = next(iter(routes_j))

                j += 1

            seg_stops = [path[k] for k in range(i, j + 1)]
            legs.append(
                {
                    "route_id": route,
                    "from_stop": seg_stops[0],
                    "to_stop": seg_stops[-1],
                    "stops": seg_stops,
                }
            )
            i = j

        return legs

    def _resolve_place(self, name: str):
        """
        Resolve a free-text place to either:
          - a real building (from Buildings.json) + its stops, or
          - a pseudo-building for a bus stop name (from routes.json)
        Returns (place_dict, [stop_names]) or (None, []).
        """
        if not name:
            return None, []

        # 1) Try building first
        b = self.data.resolve_building(name)
        if b:
            stops = self.data.get_building_stops(b)
            return b, stops

        # 2) Try as a bus stop directly
        stop = self.data.resolve_stop_name(name)
        if stop:
            pseudo = {
                "name": stop,
                "campus": None,
                "bus_stops": [stop],
            }
            return pseudo, [stop]

        return None, []

    # ----------------- public APIs -----------------

    def plan_building_to_building(self, origin_name: str, dest_name: str) -> Dict[str, Any]:
        """
        High-level planner:
        1. Resolve origin & destination text → building/stop objects + stop lists.
        2. Try to find a direct route on a single bus line.
        3. If none, run BFS across the stop graph and compress into route legs.
        """
        origin_place, origin_stops = self._resolve_place(origin_name)
        dest_place, dest_stops = self._resolve_place(dest_name)

        if not origin_place:
            return {
                "type": "error",
                "message": f"I couldn't find a building or bus stop named **{origin_name}**.",
            }
        if not dest_place:
            return {
                "type": "error",
                "message": f"I couldn't find a building or bus stop named **{dest_name}**.",
            }

        if not origin_stops:
            return {
                "type": "error",
                "message": f"I don't know any bus stops near **{origin_place['name']}**.",
            }
        if not dest_stops:
            return {
                "type": "error",
                "message": f"I don't know any bus stops near **{dest_place['name']}**.",
            }

        # -------- 1) Try ALL pairs for a direct single-route solution --------
        best_direct = None  # (start_stop, end_stop, route_id, stop_path)
        for s in origin_stops:
            for t in dest_stops:
                direct = self._direct_path_between_stops(s, t)
                if not direct:
                    continue
                rid, stop_path = direct
                if not best_direct or len(stop_path) < len(best_direct[3]):
                    best_direct = (s, t, rid, stop_path)

        if best_direct:
            start_stop, end_stop, rid, stop_path = best_direct
            legs = [
                {
                    "route_id": rid,
                    "from_stop": stop_path[0],
                    "to_stop": stop_path[-1],
                    "stops": stop_path,
                }
            ]
            return {
                "type": "bus_route",
                "origin_building": origin_place,
                "dest_building": dest_place,
                "origin_stop": start_stop,
                "dest_stop": end_stop,
                "stop_path": stop_path,
                "legs": legs,
            }

        # -------- 2) Fallback: BFS across graph + leg compression --------
        best_bfs = self._best_bfs_path(origin_stops, dest_stops)
        if not best_bfs:
            return {
                "type": "error",
                "message": (
                    f"I couldn't find any bus path between **{origin_place['name']}** "
                    f"and **{dest_place['name']}** using the JSON routes."
                ),
            }

        start_stop, end_stop, stop_path = best_bfs
        legs = self._build_legs(stop_path)

        return {
            "type": "bus_route",
            "origin_building": origin_place,
            "dest_building": dest_place,
            "origin_stop": start_stop,
            "dest_stop": end_stop,
            "stop_path": stop_path,
            "legs": legs,
        }

    def describe_plan(self, plan: Dict[str, Any]) -> str:
        """
        Turn a 'bus_route' plan into a human-readable answer.
        Uses ONLY canonical stop names from rutgers_bus_routes.json.
        """
        if plan.get("type") != "bus_route":
            return plan.get("message", "I couldn't find a valid bus route.")

        ob_name = plan["origin_building"]["name"]
        db_name = plan["dest_building"]["name"]
        origin_stop = plan["origin_stop"]
        dest_stop = plan["dest_stop"]
        legs = plan.get("legs", [])

        lines: List[str] = []

        # Starting walk
        lines.append(f"From **{ob_name}**, walk to **{origin_stop}**.")

        if not legs:
            # Extremely rare, but just in case
            lines.append(f"Then ride the next bus to **{dest_stop}** and walk to **{db_name}**.")
            return "\n".join(lines)

        # Bus legs
        lines.append("Then:")
        for i, leg in enumerate(legs, start=1):
            rid = leg.get("route_id")
            fs = leg["from_stop"]
            ts = leg["to_stop"]
            if rid:
                lines.append(f"{i}. Take route **{rid}** from **{fs}** to **{ts}**.")
            else:
                lines.append(f"{i}. Travel from **{fs}** to **{ts}** (route not identified in JSON).")

        # Ending walk
        lines.append(f"Get off at **{dest_stop}** and walk to **{db_name}**.")

        return "\n".join(lines)
