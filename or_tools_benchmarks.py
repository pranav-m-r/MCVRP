import json
import os
from parse_input import parse_and_save
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# ----------- CONSTANTS -----------
DATASET_NO = 1
CUMULATIVE_DIST = 5000000
DIST_SLACK = 0
CAP_SLACK = 0
PRECISION = 10
TIME_LIMIT = 60 

def get_dataset(dataset_no = DATASET_NO):
    file_path = os.path.join('cached_datasets', f"dataset_{dataset_no}.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue() / PRECISION:.2f}")
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data["num_vehicles"]):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data["demands"][node_index]
            plan_output += f" {node_index} Load({route_load}) -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f" {manager.IndexToNode(index)} Load({route_load})\n"
        plan_output += f"Distance of the route: {route_distance / PRECISION:.2f}m\n"
        plan_output += f"Load of the route: {route_load}\n"
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print(f"Total distance of all routes: {total_distance / PRECISION:.2f}m")
    print(f"Total load of all routes: {total_load}")
    

def find_solution(dataset_no=DATASET_NO):
    data = get_dataset(dataset_no)
    
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'], 
        data['starts'],
        data['ends']
    )
    
    routing = pywrapcp.RoutingModel(manager)
    
    # print("Testing IndexToNode calls:")
    # try:
    #     for i in range(manager.GetNumberOfIndices()):
    #         node = manager.IndexToNode(i)
    #         print(f"  Index {i} -> Node {node}")
    # except Exception as e:
    #     print(f"  Error during manual IndexToNode test: {e}")
    #     return
    
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes (handles OR-Tools internal indices)."""
        # print(f"from_index = {from_index}, to_index = {to_index}")
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]


    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # dimension_name = "Distance"
    # routing.AddDimension(
    #     evaluator_index=transit_callback_index,
    #     slack_max=DIST_SLACK,
    #     capacity=CUMULATIVE_DIST,
    #     fix_start_cumul_to_zero=True,
    #     name=dimension_name,
    # )
    
    def demand_callback(from_index):
        """Returns demand for a node, safe against OR-Tools internal indices."""
        node = manager.IndexToNode(from_index)
        return data["demands"][node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        evaluator_index=demand_callback_index,
        slack_max=CAP_SLACK,  
        vehicle_capacities=data["vehicle_capacities"],  
        fix_start_cumul_to_zero=True,
        name="Capacity",
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    # search_parameters.local_search_metaheuristic = (
    #     routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    # )
    search_parameters.time_limit.FromSeconds(TIME_LIMIT)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print(f"NO SOLUTION exists for the given parameters!!")
        
if __name__ == "__main__":
    parse_and_save(PRECISION)
    
    print("Dataset :", DATASET_NO)
    print("Cumulative Dist :", CUMULATIVE_DIST)
    print("Max Distance Slack:", DIST_SLACK)
    print("Max Capacity Slack:", CAP_SLACK)
    
    find_solution()