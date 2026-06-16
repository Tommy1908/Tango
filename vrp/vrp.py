import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from distance_matrix.distance_matrix import build_distance_matrix_manhattan

class VrpSolver:
    def __init__(self):
        self.query = []
        self.solution = []

    def vrp(self, data, vehicle_number=35, capacity=19, auto_split=True, start_at=None, end_at=None, search_time=1):
        self.solution = []
        self.query = []

        # If any localization requires more than vehicle capacity, will fail.
        # Auto split prevents that and allow 2 (or more) vehicles to go to that localization instead
        if auto_split:
            query = self.split(data, capacity)
        else:
            query = data
        self.query = query

        if len(query)==0:
            return []
        
        distance_matrix, virtual_node_id = self.get_matrix(query, start_at, end_at)

        # Start/End nodes
        vehicle_start_nodes = [virtual_node_id if start_at is None else start_at] * vehicle_number
        vehicle_end_nodes = [virtual_node_id if end_at is None else end_at] * vehicle_number  

        # Index manager
        manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix), 
            vehicle_number, 
            vehicle_start_nodes, 
            vehicle_end_nodes
        )
        routing = pywrapcp.RoutingModel(manager)

        # Distance callback for cost
        def distance_zones_cost_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node])

        transit_callback_index = routing.RegisterTransitCallback(distance_zones_cost_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        routing.SetFixedCostOfAllVehicles(200000)

        # Capacity dimension
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            if virtual_node_id is not None and from_node == virtual_node_id:
                return 0
            if start_at is not None and from_node == start_at:
                return 0
            return query[from_node]['count']

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  
            [capacity] * vehicle_number,  
            True,  
            "Capacity"
        )

        # Heuristics
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.SAVINGS
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = search_time

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            print("Routes optimized\n")
            capacity_dimension = routing.GetDimensionOrDie("Capacity")
            
            total_load = 0
            active_vehicles = 0

            for vehicle_id in range(vehicle_number):
                index = routing.Start(vehicle_id)
                route_names = []
                coordinates_route = []
                route_index = []

                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    if virtual_node_id is not None and node == virtual_node_id:
                        route_names.append("Free Start")
                        route_index.append(-1)
                    else:
                        route_names.append(f"{query[node]['name']} ({query[node]['count']} pax)")
                        coordinates_route.append(query[node]['coordinates'])
                        route_index.append(node)

                    index = solution.Value(routing.NextVar(index))

                end_node = manager.IndexToNode(index)
                if virtual_node_id is not None and end_node == virtual_node_id:
                    route_names.append("Free End")
                    route_index.append(-1)
                else:
                    route_names.append(query[end_node]['name'])
                    coordinates_route.append(query[end_node]['coordinates'])
                    route_index.append(end_node)

                used_capacity = solution.Value(capacity_dimension.CumulVar(index))
                if not (len(route_index) == 2 and route_index[0]==0 and route_index[1]==0):
                    self.solution.append((route_index,used_capacity))

                if used_capacity > 0:  
                    active_vehicles += 1
                    total_load += used_capacity

                    print(f"   Vehicle {vehicle_id}:")
                    print(f"   Route: {' -> '.join(route_names)}")
                    print(f"   Load: {used_capacity}/{capacity}")

                    if len(coordinates_route) >= 2:
                        base_url = "https://www.google.com/maps/dir/"
                        coordinates_url = [f"{lat},{lng}" for lat, lng in coordinates_route]
                        map_link = base_url + "/".join(coordinates_url)
                        print(f"      Map: {map_link}\n")
                    else:
                        print("      Only one destination, not available\n")

            print("=" * 60)
            print(f"SUMMARY:")
            print(f"     Total demand solved: {total_load}")
            print(f"     Total active vehicles: {active_vehicles}")
            print("=" * 60)
        else:
            print("Couldn't find a valid solution")
            return None
        return self.solution

    def split(self, data, max_vehicle_capacity):
        splitted_data = []
        for localization in data:

            capacity_demanded_left = localization['count']
            if capacity_demanded_left <= max_vehicle_capacity:
                splitted_data.append(localization)
            else:
                # Localization requires more than total capacity
                parts = 1
                while capacity_demanded_left > 0:
                    splitted_capacity = min(capacity_demanded_left, max_vehicle_capacity)

                    # Clone keeping data
                    cloned_localization = localization.copy()
                    cloned_localization['count'] = splitted_capacity
                    cloned_localization['name'] = f"{localization['name']} (Part {parts})"

                    splitted_data.append(cloned_localization)
                    capacity_demanded_left -= splitted_capacity
                    parts += 1
        return splitted_data

    def get_matrix(self, query, start_at, end_at):
        real_nodes = len(query)

        # Distance matrix
        coords = [localization['coordinates'] for localization in query]
        manhattan_matrix = build_distance_matrix_manhattan(coords, multiplier=1)

        # Return base matrix if no virtual node is needed
        if start_at is not None and end_at is not None:
            virtual_node_id = None
        else:
            # Virtual node (distance 0 to all of them)
            extended_matrix = np.zeros((real_nodes + 1, real_nodes + 1))
            extended_matrix[:real_nodes, :real_nodes] = manhattan_matrix
            virtual_node_id = real_nodes

            if end_at is not None:
                # Going from virtual node to any is free, other way is inf 
                for i in range(real_nodes):
                    extended_matrix[i, virtual_node_id] = 9999999

            if start_at is not None:
                # Going to virtual node from any is free, other way is inf 
                for i in range(real_nodes):
                    extended_matrix[virtual_node_id, i] = 9999999
            manhattan_matrix = extended_matrix


        # Add extra costs and penalties to matrix
        matrix_size = len(manhattan_matrix)
        zone_penalty = 10000
        for i in range(matrix_size):
            for j in range(matrix_size):
                # No penalties on virtual node
                if virtual_node_id is not None and (i == virtual_node_id or j == virtual_node_id):
                    continue
                # No penalties on the end
                if end_at is not None and j == end_at:
                    continue

                from_zone = query[i].get('zone', [])
                to_zone = query[j].get('zone', [])

                # If they dont share the same zone, add penalty
                if not (set(from_zone) & set(to_zone)):
                    manhattan_matrix[i][j] += zone_penalty

        return manhattan_matrix, virtual_node_id

if __name__ == "__main__": # pragma: no cover
    solver = VrpSolver()

    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 0, 'coordinates': (-34.50124927145548, -58.48266215470423)},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 2, 'coordinates': (-34.502925295393105, -58.494679009326596)},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196)},
            {'name': 'P4', 'address': 'Av. del Libertador 3502', 'count': 2, 'coordinates': (-34.49745559061509, -58.48456863718224)},
            {'name': 'P5', 'address': 'Díaz Vélez 1945', 'count': 2, 'coordinates': (-34.50234009000904, -58.501433339121704)},
            ]
    solution1 = solver.vrp(query,vehicle_number=4,capacity=4, start_at=0, end_at=0, auto_split=True)
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 0, 'coordinates': (-34.50124927145548, -58.48266215470423), 'zone':['A','B']},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 2, 'coordinates': (-34.502925295393105, -58.494679009326596), 'zone':['A']},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196), 'zone':['B']},
            {'name': 'P4', 'address': 'Av. del Libertador 3502', 'count': 2, 'coordinates': (-34.49745559061509, -58.48456863718224), 'zone':['B']},
            {'name': 'P5', 'address': 'Díaz Vélez 1945', 'count': 2, 'coordinates': (-34.50234009000904, -58.501433339121704), 'zone':['A']},
            ]
    solution2 = solver.vrp(query,vehicle_number=4,capacity=4, start_at=0, end_at=0, auto_split=True)
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 0, 'coordinates': (-34.50124927145548, -58.48266215470423), 'zone':['A','B']},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 2, 'coordinates': (-34.502925295393105, -58.494679009326596), 'zone':['A']},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196), 'zone':['A']},
            {'name': 'P4', 'address': 'Av. del Libertador 3502', 'count': 2, 'coordinates': (-34.49745559061509, -58.48456863718224), 'zone':['B']},
            {'name': 'P5', 'address': 'Díaz Vélez 1945', 'count': 2, 'coordinates': (-34.50234009000904, -58.501433339121704), 'zone':['B']},
            ]
    solution3 = solver.vrp(query,vehicle_number=4,capacity=4, start_at=0, end_at=0, auto_split=True)
    print(solution1)
    print(solution2)
    print(solution3)
