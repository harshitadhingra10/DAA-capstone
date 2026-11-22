import time
import heapq
import matplotlib.pyplot as plt
from datasets import get_small_dataset, generate_scaled_dataset

# ==============================================================================
# PHASE 2A: PACKAGE PRIORITIZATION (MERGE SORT - O(N log N))
# ==============================================================================
def merge_sort_parcels(parcels):
    """
    Sorts parcels primarily by earliest deadline (ascending),
    and secondarily by highest priority value (descending).
    Time Complexity: O(N log N) | Space Complexity: O(N)
    """
    if len(parcels) <= 1:
        return parcels

    mid = len(parcels) // 2
    left_half = merge_sort_parcels(parcels[:mid])
    right_half = merge_sort_parcels(parcels[mid:])

    return _merge(left_half, right_half)


def _merge(left, right):
    sorted_list = []
    i = j = 0

    while i < len(left) and j < len(right):
        # Prioritize tighter deadline first; tie-break with higher value
        if (left[i]["deadline"], -left[i]["value"]) <= (right[j]["deadline"], -right[j]["value"]):
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list


# ==============================================================================
# PHASE 2B: BOX FILLING / OPTIMAL SELECTION (0/1 KNAPSACK DP - O(N * W))
# ==============================================================================
def knapsack_dp_select(parcels, capacity, show_table=False):
    """
    Selects the optimal subset of parcels that maximizes priority value
    without exceeding van weight capacity.
    Time Complexity: O(N * W) | Space Complexity: O(N * W)
    """
    n = len(parcels)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Build DP Table bottom-up
    for i in range(1, n + 1):
        w_i = parcels[i - 1]["weight"]
        v_i = parcels[i - 1]["value"]
        for w in range(capacity + 1):
            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], v_i + dp[i - 1][w - w_i])
            else:
                dp[i][w] = dp[i - 1][w]

    if show_table:
        print("\n[Phase 2] DP Table (Rows = Parcels 0..N, Cols = Weight 0..W):")
        for row in dp:
            print("  ", row)

    # Backtrack to find selected parcels
    selected_parcels = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_parcels.append(parcels[i - 1])
            w -= parcels[i - 1]["weight"]

    selected_parcels.reverse()
    max_value = dp[n][capacity]
    total_weight = sum(p["weight"] for p in selected_parcels)

    return selected_parcels, max_value, total_weight


# ==============================================================================
# PHASE 3A: INDIVIDUAL SHORTEST PATHS (DIJKSTRA'S ALGORITHM - O((V + E) log V))
# ==============================================================================
def dijkstra_shortest_paths(graph, start_node):
    """
    Computes shortest distance and path tree from start_node to all other nodes.
    Time Complexity: O((V + E) log V) | Space Complexity: O(V)
    """
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start_node] = 0
    pq = [(0, start_node)]

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)

        if curr_dist > distances[curr_node]:
            continue

        for neighbor, weight in graph[curr_node].items():
            distance = curr_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = curr_node
                heapq.heappush(pq, (distance, neighbor))

    return distances, previous


def reconstruct_path(previous, start, target):
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()
    return path if path[0] == start else []


# ==============================================================================
# PHASE 3B: OVERALL DELIVERY ROUTE (NEAREST-NEIGHBOR TSP APPROXIMATION - O(K^2))
# ==============================================================================
def plan_tsp_nearest_neighbor(graph, hub, delivery_stops):
    """
    Finds an approximate shortest tour starting at hub, visiting all unique
    delivery_stops, and returning to hub using Dijkstra pairwise distances.
    Time Complexity: O(K * (V + E) log V + K^2) where K = number of stops.
    """
    unique_stops = list(set(delivery_stops))
    all_points = [hub] + unique_stops

    # Precompute shortest distances & paths between all required stops
    dist_matrix = {}
    path_matrix = {}
    for point in all_points:
        dists, prevs = dijkstra_shortest_paths(graph, point)
        dist_matrix[point] = dists
        path_matrix[point] = prevs

    # Greedy Nearest-Neighbor Heuristic
    unvisited = set(unique_stops)
    current = hub
    tour_stops = [hub]
    full_road_sequence = [hub]
    total_distance = 0

    while unvisited:
        nearest_stop = min(unvisited, key=lambda stop: dist_matrix[current][stop])
        leg_dist = dist_matrix[current][nearest_stop]
        leg_path = reconstruct_path(path_matrix[current], current, nearest_stop)

        total_distance += leg_dist
        tour_stops.append(nearest_stop)
        full_road_sequence.extend(leg_path[1:])  # Avoid duplicating intermediate node

        unvisited.remove(nearest_stop)
        current = nearest_stop

    # Return to Warehouse Hub
    return_dist = dist_matrix[current][hub]
    return_path = reconstruct_path(path_matrix[current], current, hub)
    total_distance += return_dist
    tour_stops.append(hub)
    full_road_sequence.extend(return_path[1:])

    return tour_stops, full_road_sequence, total_distance, dist_matrix[hub]


# ==============================================================================
# EXECUTION & PHASE 4: PERFORMANCE TESTING + CHART GENERATION
# ==============================================================================
def run_demo():
    print("=" * 70)
    print("MINI-COURIER PLANNER: ALGORITHMIC PROTOTYPE DEMONSTRATION")
    print("=" * 70)

    capacity, parcels, graph = get_small_dataset()
    print(f"\n[Phase 1] Loaded {len(parcels)} parcels | Van Capacity: {capacity} kg | Graph Nodes: {len(graph)}")

    # Phase 2A: Sorting
    sorted_parcels = merge_sort_parcels(parcels)
    print("\n[Phase 2A] Parcels Sorted by Urgency (Deadline ASC, Value DESC):")
    for p in sorted_parcels:
        print(f"  - {p['id']} | Dest: {p['dest']:<12} | Weight: {p['weight']}kg | Value: {p['value']} | Deadline: {p['deadline']}h")

    # Phase 2B: Knapsack DP
    selected, max_val, used_weight = knapsack_dp_select(sorted_parcels, capacity, show_table=True)
    print(f"\n[Phase 2B] Optimal Packing Plan (Used Weight: {used_weight}/{capacity} kg | Total Value: {max_val}):")
    for p in selected:
        print(f"  * Selected {p['id']} -> {p['dest']} ({p['weight']}kg, Value: {p['value']})")

    # Phase 3: Shortest Paths & TSP Route
    stops = [p["dest"] for p in selected]
    tour_stops, road_seq, total_km, hub_dists = plan_tsp_nearest_neighbor(graph, "Warehouse", stops)

    print("\n[Phase 3A] Dijkstra Shortest Distances from Warehouse:")
    for node, d in hub_dists.items():
        print(f"  - Warehouse -> {node:<12}: {d} km")

    print("\n[Phase 3B] Final Nearest-Neighbor Delivery Route:")
    print(f"  - Stop Order   : {' -> '.join(tour_stops)}")
    print(f"  - Full Path    : {' -> '.join(road_seq)}")
    print(f"  - Total Length : {total_km} km")


def run_benchmarks():
    print("\n" + "=" * 70)
    print("[Phase 4] RUNNING SCALABILITY BENCHMARKS...")
    print("=" * 70)

    input_sizes = [10, 50, 100, 250, 500, 1000]
    sort_times = []
    dp_times = []
    route_times = []

    print(f"{'Parcels (N)':<12} | {'MergeSort (ms)':<15} | {'Knapsack DP (ms)':<17} | {'Dijkstra+TSP (ms)':<18}")
    print("-" * 70)

    for n in input_sizes:
        cap, parcels, graph = generate_scaled_dataset(num_parcels=n, num_nodes=30, capacity=150)

        t0 = time.perf_counter()
        sorted_p = merge_sort_parcels(parcels)
        t1 = time.perf_counter()

        selected, _, _ = knapsack_dp_select(sorted_p, cap, show_table=False)
        t2 = time.perf_counter()

        stops = [p["dest"] for p in selected]
        plan_tsp_nearest_neighbor(graph, "Warehouse", stops)
        t3 = time.perf_counter()

        ms_sort = (t1 - t0) * 1000
        ms_dp = (t2 - t1) * 1000
        ms_route = (t3 - t2) * 1000

        sort_times.append(ms_sort)
        dp_times.append(ms_dp)
        route_times.append(ms_route)

        print(f"{n:<12} | {ms_sort:<15.4f} | {ms_dp:<17.4f} | {ms_route:<18.4f}")

    # Plot Runtime Chart
    plt.figure(figsize=(9, 5))
    plt.plot(input_sizes, sort_times, marker='o', label='Merge Sort O(N log N)')
    plt.plot(input_sizes, dp_times, marker='s', label='0/1 Knapsack DP O(N * W)')
    plt.plot(input_sizes, route_times, marker='^', label='Dijkstra + NN-TSP')
    plt.title('Mini-Courier Planner: Algorithmic Runtime Comparison')
    plt.xlabel('Number of Parcels (N)')
    plt.ylabel('Execution Time (milliseconds)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("runtime_analysis.png", dpi=300)
    print("\nSaved runtime chart as 'runtime_analysis.png'!")


if __name__ == "__main__":
    run_demo()
    run_benchmarks()



def run_custom_input():
    print("\n" + "=" * 70)
    print("[CUSTOM INPUT MODE] Enter your own test case")
    print("=" * 70)
    cap = int(input("Enter Van Capacity (kg): "))
    n = int(input("Enter Number of Parcels: "))
    
    custom_parcels = []
    for i in range(n):
        print(f"\nParcel {i+1}:")
        pid = input("  Parcel ID (e.g. P1): ")
        dest = input("  Destination (Sector_14 / Sohna_Road / Cyber_Hub / MG_Road / Golf_Course): ")
        w = int(input("  Weight (kg): "))
        v = int(input("  Priority Value (e.g. 50-100): "))
        d = int(input("  Deadline (hours): "))
        custom_parcels.append({"id": pid, "dest": dest, "weight": w, "value": v, "deadline": d})
    
    _, _, graph = get_small_dataset()
    sorted_p = merge_sort_parcels(custom_parcels)
    selected, max_val, used_w = knapsack_dp_select(sorted_p, cap, show_table=True)
    
    print(f"\nSelected Parcels ({used_w}/{cap} kg | Value: {max_val}): {[p['id'] for p in selected]}")
    if selected:
        stops = [p["dest"] for p in selected]
        tour, road, km, _ = plan_tsp_nearest_neighbor(graph, "Warehouse", stops)
        print(f"Delivery Route: {' -> '.join(tour)} (Total: {km} km)")


if __name__ == "__main__":
    run_demo()
    run_benchmarks()
    choice = input("\nDo you want to test a custom unseen dataset? (y/n): ").strip().lower()
    if choice == 'y':
        run_custom_input()
    print("Mini Courier Planner Started")    
        