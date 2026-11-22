import random

def get_small_dataset():
    """
    Returns a small, easy-to-trace dataset for Phase 2 & Phase 3 demonstration.
    """
    van_capacity = 15  # Max weight capacity in kg

    # Each parcel: (id, destination_node, weight_kg, priority_score, deadline_hrs)
    # Note: Higher priority_score = more urgent. Lower deadline_hrs = more urgent.
    parcels = [
        {"id": "P101", "dest": "Sector_14", "weight": 4, "value": 90, "deadline": 2},
        {"id": "P102", "dest": "Sohna_Road", "weight": 6, "value": 80, "deadline": 4},
        {"id": "P103", "dest": "Cyber_Hub", "weight": 5, "value": 100, "deadline": 1},
        {"id": "P104", "dest": "MG_Road", "weight": 3, "value": 60, "deadline": 3},
        {"id": "P105", "dest": "Sector_14", "weight": 7, "value": 110, "deadline": 5},
        {"id": "P106", "dest": "Golf_Course", "weight": 2, "value": 50, "deadline": 2},
    ]

    # Weighted Undirected Graph representing road distances (in km)
    # 'Warehouse' is the starting & ending hub
    city_graph = {
        "Warehouse": {"Sector_14": 4, "Sohna_Road": 6, "MG_Road": 8},
        "Sector_14": {"Warehouse": 4, "Cyber_Hub": 5, "MG_Road": 3},
        "Sohna_Road": {"Warehouse": 6, "MG_Road": 4, "Golf_Course": 7},
        "Cyber_Hub": {"Sector_14": 5, "MG_Road": 2, "Golf_Course": 6},
        "MG_Road": {"Warehouse": 8, "Sector_14": 3, "Sohna_Road": 4, "Cyber_Hub": 2, "Golf_Course": 3},
        "Golf_Course": {"Sohna_Road": 7, "Cyber_Hub": 6, "MG_Road": 3}
    }

    return van_capacity, parcels, city_graph


def generate_scaled_dataset(num_parcels, num_nodes=25, capacity=100):
    """
    Generates synthetic datasets of varying sizes for Phase 4 Performance Benchmarking.
    """
    random.seed(42)
    nodes = ["Warehouse"] + [f"Loc_{i}" for i in range(1, num_nodes)]
    
    # Build connected weighted graph
    graph = {node: {} for node in nodes}
    for i in range(num_nodes):
        # Ensure connectivity in a ring + random extra edges
        nxt = (i + 1) % num_nodes
        dist = random.randint(2, 15)
        graph[nodes[i]][nodes[nxt]] = dist
        graph[nodes[nxt]][nodes[i]] = dist
        
        for _ in range(2):
            target = random.choice(nodes)
            if target != nodes[i]:
                d = random.randint(3, 25)
                graph[nodes[i]][target] = d
                graph[target][nodes[i]] = d

    parcels = []
    for i in range(num_parcels):
        parcels.append({
            "id": f"PKG_{i+1}",
            "dest": random.choice(nodes[1:]),
            "weight": random.randint(1, 15),
            "value": random.randint(20, 150),
            "deadline": random.randint(1, 12)
        })
    print("Mini Courier Planner Started")    

    return capacity, parcels, graph