from vrp.vrp import VrpSolver

def test_vrp_no_data_is_empty():
    solver = VrpSolver()
    solution = solver.vrp([],2,5)

    assert solution == []

def test_vrp_one_element_both_ends_free():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 3, 'coordinates': (-34.50124927145548, -58.48266215470423)}]
    solution = solver.vrp(query,vehicle_number=1,capacity=4, start_at=None, end_at=None)

    assert solution == [([-1,0,-1],3)]
    # -1 its a free/inexisting node. This is translated as: Only index 0, start wherever, end wherever.

def test_vrp_one_element_end_free():
    solver = VrpSolver()
    query= [{'name': 'Depot', 'address': 'Av. del Libertador 3120', 'count': 3, 'coordinates': (-34.50124927145548, -58.48266215470423)}]
    solution = solver.vrp(query,vehicle_number=1,capacity=4, start_at=0, end_at=None)

    assert solution == [([0,-1],0)]
    # The start point count will be ignored. If the startpoint also requires to load something create a startpoint, and a startpoint_count nodes. Set only the first one

def test_vrp_one_element_start_free():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 3, 'coordinates': (-34.50124927145548, -58.48266215470423)}]
    solution = solver.vrp(query,vehicle_number=1,capacity=4, start_at=None, end_at=0)

    assert solution == [([-1, 0], 0)]
    # If the only object is the endpoint, it will not load the count, therefore it just goes there

def test_vrp_one_element_fixed_start_and_end():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 3, 'coordinates': (-34.50124927145548, -58.48266215470423)}]
    solution = solver.vrp(query,vehicle_number=1,capacity=4, start_at=0, end_at=0)

    assert solution == []
    # Taking into account, starting from depot does not load the count, and actually there is no movement, there is no route.

def test_vrp_two_elements_free_ends_create_a_simple_route():
    solver = VrpSolver()
    query= [{'name': 'Depot', 'address': 'Av. del Libertador 3120', 'count': 3, 'coordinates': (-34.50124927145548, -58.48266215470423)},
            {'name': 'P1', 'address': 'Av. Maipú 3565', 'count': 1, 'coordinates': (-34.502925295393105, -58.494679009326596)},
            ]
    solution = solver.vrp(query,vehicle_number=1,capacity=4, start_at=None, end_at=None)
    assert solution == [([-1, 0, 1, -1], 4)]

def test_vrp_added_demand_is_more_than_one_vehicle_capacity():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 3, 'coordinates': (-34.50124927145548, -58.48266215470423)},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 1, 'coordinates': (-34.502925295393105, -58.494679009326596)},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196)},
            ]
    solution = solver.vrp(query,vehicle_number=2,capacity=4, start_at=None, end_at=None)
    assert solution == [([-1, 0, 1, -1], 4), ([-1, 2, -1], 2)]

def test_vrp_single_demand_is_more_than_one_vehicle_capacity():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. Maipú 3565', 'count': 5, 'coordinates': (-34.502925295393105, -58.494679009326596)}]
    solution = solver.vrp(query,vehicle_number=2,capacity=4, start_at=None, end_at=None, auto_split=False)
    assert solution == None
    # No vehicle will ever be able to supply that demand all at once. Therefore its not possible

def test_vrp_single_demand_is_more_than_one_vehicle_capacity_auto_split_on():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. Maipú 3565', 'count': 5, 'coordinates': (-34.502925295393105, -58.494679009326596)}]
    solution = solver.vrp(query,vehicle_number=2,capacity=4, start_at=None, end_at=None, auto_split=True)
    assert solution == [([-1, 0, -1], 4), ([-1, 1, -1], 1)]
    assert solver.query == [{'name': 'P1 (Part 1)', 'address': 'Av. Maipú 3565', 'count': 4, 'coordinates': (-34.502925295393105, -58.494679009326596)}, {'name': 'P1 (Part 2)', 'address': 'Av. Maipú 3565', 'count': 1, 'coordinates': (-34.502925295393105, -58.494679009326596)}]
    # Query changes, now its splitted

def test_vrp_zones_affect_routing():
    solver = VrpSolver()
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 0, 'coordinates': (-34.50124927145548, -58.48266215470423)},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 2, 'coordinates': (-34.502925295393105, -58.494679009326596)},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196)},
            {'name': 'P4', 'address': 'Av. del Libertador 3502', 'count': 2, 'coordinates': (-34.49745559061509, -58.48456863718224)},
            {'name': 'P5', 'address': 'Díaz Vélez 1945', 'count': 2, 'coordinates': (-34.50234009000904, -58.501433339121704)},
            ]
    solution_no_zones = solver.vrp(query,vehicle_number=4,capacity=4, start_at=0, end_at=0, auto_split=True)
    
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 0, 'coordinates': (-34.50124927145548, -58.48266215470423), 'zone':['A','B']},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 2, 'coordinates': (-34.502925295393105, -58.494679009326596), 'zone':['A']},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196), 'zone':['B']},
            {'name': 'P4', 'address': 'Av. del Libertador 3502', 'count': 2, 'coordinates': (-34.49745559061509, -58.48456863718224), 'zone':['B']},
            {'name': 'P5', 'address': 'Díaz Vélez 1945', 'count': 2, 'coordinates': (-34.50234009000904, -58.501433339121704), 'zone':['A']},
            ]
    solution_zones_1 = solver.vrp(query,vehicle_number=4,capacity=4, start_at=0, end_at=0, auto_split=True)
    
    query= [{'name': 'P1', 'address': 'Av. del Libertador 3120', 'count': 0, 'coordinates': (-34.50124927145548, -58.48266215470423), 'zone':['A','B']},
            {'name': 'P2', 'address': 'Av. Maipú 3565', 'count': 2, 'coordinates': (-34.502925295393105, -58.494679009326596), 'zone':['A']},
            {'name': 'P3', 'address': 'Av. del Libertador 13381', 'count': 2, 'coordinates': (-34.487119420976, -58.485538394774196), 'zone':['A']},
            {'name': 'P4', 'address': 'Av. del Libertador 3502', 'count': 2, 'coordinates': (-34.49745559061509, -58.48456863718224), 'zone':['B']},
            {'name': 'P5', 'address': 'Díaz Vélez 1945', 'count': 2, 'coordinates': (-34.50234009000904, -58.501433339121704), 'zone':['B']},
            ]
    solution_zones_2 = solver.vrp(query,vehicle_number=4,capacity=4, start_at=0, end_at=0, auto_split=True)

    assert solution_no_zones == [([0, 1, 4, 0], 4), ([0, 2, 3, 0], 4)]
    assert solution_zones_1 == [([0, 1, 4, 0], 4), ([0, 2, 3, 0], 4)]
    assert solution_zones_2 == [([0, 1, 2, 0], 4), ([0, 3, 4, 0], 4)]