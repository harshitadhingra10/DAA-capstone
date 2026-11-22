# Mini-Courier Planner 

## Phase 1: Courier Problem Design & System Architecture
- **Objective:** Automate courier van loading and delivery route planning from a central `Warehouse` hub.
- **Data Model:**
  - **Parcel Object:** `(id, destination_node, weight_kg, priority_value, deadline_hrs)`
  - **City Map:** Weighted undirected graph represented via an Adjacency Dictionary `{node: {neighbor: distance_km}}`.
- **Pipeline Workflow:**
  1. **Merge Sort** orders incoming parcels by urgency (`deadline` ascending, `value` descending).
  2. **0/1 Knapsack (Dynamic Programming)** selects the highest-value combination of parcels fitting within the van's weight capacity $W$.
  3. **Dijkstra's Algorithm** computes exact shortest road paths between the Warehouse and all selected delivery stops.
  4. **Nearest-Neighbor TSP Heuristic** sequences the delivery stops into an efficient closed tour starting and ending at the Warehouse.

## Phase 2 & 3: Complexity Analysis
| Algorithmic Component | Technique Used | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| **Parcel Prioritization** | Merge Sort | $O(N \log N)$ | $O(N)$ |
| **Box Filling / Selection** | 0/1 Knapsack (DP) | $O(N \cdot W)$ | $O(N \cdot W)$ |
| **Shortest Path Tree** | Dijkstra (Min-Heap) | $O((V + E) \log V)$ | $O(V)$ |
| **Delivery Tour Routing** | Nearest-Neighbor TSP | $O(K(V + E)\log V + K^2)$ | $O(V + K^2)$ |

*(Where $N$ = number of parcels, $W$ = van capacity, $V$ = graph intersections, $E$ = roads, $K$ = unique delivery stops)*

## Phase 4: Performance Optimization Suggestions
1. **Space Optimization in Knapsack:** Reduce the 2D DP table $O(N \cdot W)$ to a 1D array $O(W)$ when item backtracking is not required, or use branch-and-bound when $W$ is very large.
2. **2-Opt Local Search for TSP:** Nearest-Neighbor is a greedy $O(K^2)$ approximation that can occasionally cross paths; applying a 2-Opt swap post-processing step improves tour optimality.
3. **All-Pairs Caching (Floyd-Warshall / Precomputed Matrix):** For static city maps, precomputing all-pairs shortest paths once avoids re-running Dijkstra's algorithm on every dispatch cycle.

## Phase 5: How to Run
1. Install matplotlib (for runtime charts): `pip install matplotlib`
2. Run the application: `python courier_planner.py`
3. Check terminal output for the DP table, selected parcels, shortest route, and benchmark table, plus the generated `runtime_analysis.png` chart.