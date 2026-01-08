# src/routing_engine.py
from collections import deque
from typing import List, Dict, Any, Optional, Tuple


class RoutingEngine:
    """
    Computes bus routes between buildings using data from DataLoader:
    - Buildings.json  → building → nearby bus stops
    - rutgers_bus_routes.json → stop graph + edge→routes
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

    def _best_stop_path(
        self, origin_stops: List[str], dest_stops: List[str]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        Try all origin_stop × dest_stop pairs and choose the path
        with the fewest bus hops.
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

    def _build_legs(self, path: List[str]) -> List[Dict[str, Any]]:
        """
        Given a list of stops [s0, s1, ..., sn], compress it into route legs:
        [
          { "route_id": "B", "from_stop": "Hill Center", "to_stop": "Livingston Student Center", "stops": [...] },
          ...
        ]
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
            # choose any route that covers the first edge (usually unique)
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

    # ----------------- public APIs -----------------

    def plan_building_to_building(self, origin_name: str, dest_name: str) -> Dict[str, Any]:
        """
        High-level planner:
        1. Resolve fuzzy building names → building dicts.
        2. Get nearby bus stops for each building.
        3. Find best stop-to-stop path over the bus graph.
        4. Convert that path into route legs.
        """
        # 1) resolve buildings (fuzzy)
        origin_b = self.data.resolve_building(origin_name)
        dest_b = self.data.resolve_building(dest_name)

        if not origin_b:
            return {
                "type": "error",
                "message": f"I couldn't find a building named **{origin_name}** in my data.",
            }
        if not dest_b:
            return {
                "type": "error",
                "message": f"I couldn't find a building named **{dest_name}** in my data.",
            }

        # 2) nearby stops per building (already mapped to canonical route stop names)
        origin_stops = self.data.get_building_stops(origin_b)
        dest_stops = self.data.get_building_stops(dest_b)

        if not origin_stops:
            return {
                "type": "error",
                "message": f"I don't know any bus stops near **{origin_b['name']}**.",
            }
        if not dest_stops:
            return {
                "type": "error",
                "message": f"I don't know any bus stops near **{dest_b['name']}**.",
            }

        # 3) best stop-to-stop path
        best = self._best_stop_path(origin_stops, dest_stops)
        if not best:
            return {
                "type": "error",
                "message": (
                    f"I couldn't find any bus path between **{origin_b['name']}** "
                    f"and **{dest_b['name']}** using the JSON routes."
                ),
            }

        start_stop, end_stop, stop_path = best

        # 4) route legs (A, B, H, LX, etc.)
        legs = self._build_legs(stop_path)

        return {
            "type": "bus_route",
            "origin_building": origin_b,
            "dest_building": dest_b,
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
