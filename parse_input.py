import re
import json
import math
import os
from numpy.random.tests import data

datasets = {}

def euclidian_distance(point1: tuple[int, int], point2: tuple[int, int]) -> float:
    dist = math.sqrt((abs(point1[0] - point2[0]) ** 2) + (abs(point1[1] - point2[1]) ** 2))
    return dist

def format_dataset(dataset : dict, precision) -> list[list[int]]:
    demand_dict = {}
    locations = []
    
    for i in range(len(dataset['target_locations'])):
        demand_dict[dataset['target_locations'][i]] = dataset['weights'][i]
        locations.append(dataset['target_locations'][i])

    for i in range(len(dataset['vehicle_locations'])):
        if dataset['vehicle_locations'][i] not in demand_dict:
            demand_dict[dataset['vehicle_locations'][i]] = 0
            locations.append(dataset['vehicle_locations'][i])
        
    # print("\n\ndemand dict = ", demand_dict)
        
    vehicle_locaitons = set(dataset['vehicle_locations'])
    demands = []
    starts = []
    ends = []
    distance_matrix = []
    for i in range(len(locations)):
        demands.append(demand_dict[locations[i]])
        if locations[i] in vehicle_locaitons:
            starts.append(i)
            ends.append(i)
        distances = []
        for j in range(len(locations)):
            distances.append(int(precision * euclidian_distance(locations[i], locations[j])))
        distance_matrix.append(distances)
    
    per_vehicle_cap = (sum(dataset['weights']) + len(starts) - 1) // len(starts)
    return {
        "distance_matrix" : distance_matrix,
        "num_vehicles": len(starts),
        "demands": demands,
        "vehicle_capacities": [per_vehicle_cap] * len(starts),
        "starts": starts,
        "ends": ends
    }
        
def parse_and_save(precision) -> None:
    """
    Parses and saves data as json
    
    Data in .txt file :
        Data set #1 
        Vehicle locations :117,290;120,176;182,177;158,266;140,40;166,17;180,24;35,45;60,113;60,208;
        Target locations :176,8;90,158;102,83;40,6;173,122;142,24;106,14;169,271;186,70;65,142;165,288;150,58;152,12;54,278;6,228;77,134;31,78;95,293;48,103;24,157;31,52;65,69;39,150;162,128;49,297;112,112;66,29;16,116;12,131;191,104;5,298;32,85;198,57;150,20;163,243;45,5;47,205;176,187;136,249;143,261;94,55;169,134;64,57;183,222;23,253;58,132;165,51;17,15;138,286;140,73;130,151;149,89;119,160;188,194;175,160;108,46;178,85;57,246;133,72;33,104;171,67;91,112;57,61;52,50;175,258;17,16;63,208;56,124;177,22;115,13;195,144;164,139;141,68;109,105;103,10;99,35;39,55;196,23;52,230;20,62;2,43;111,284;9,64;180,139;77,166;185,71;64,193;166,4;180,186;149,111;104,209;193,247;119,78;192,106;66,143;79,294;156,86;58,103;101,221;49,83;
        Weights = 78,28,100,39,36,50,23,51,48,13,87,71,80,69,40,71,57,11,20,24,86,71,34,39,80,25,40,71,83,94,52,60,78,68,89,49,71,79,34,50,10,41,97,77,13,82,29,77,43,47,85,95,51,92,90,58,33,19,45,61,30,51,62,25,86,97,85,37,83,10,97,90,41,19,69,74,95,80,18,61,17,70,88,44,45,87,21,27,72,92,54,41,59,52,72,36,38,48,60,84
    saved as :
        {
            'distance_matrix' : list[list[int]]
            'starts' : list[int]
            'ends' : list[int]
        }
    """
    file_name = 'CVRP_10Vehicles_100Targets.txt'
    pattern = r"Data set #(\d+)\nVehicle locations :(.*);\nTarget locations :(.*)\nWeights = (.*)"
    saved = 0
    
    cache_dir = 'cached_datasets'
    os.makedirs(cache_dir, exist_ok=True)
    
    with open(file_name, 'r') as input_file:
        data = input_file.read()
        
        matches = re.findall(pattern, data)
        
        for match in matches:
            ds_no = int(match[0])        
            vehicle_locations_str = match[1]  
            target_locations_str = match[2]   
            weights = match[3]   
            
            vehicle_locations = [tuple(map(int, s.split(','))) for s in vehicle_locations_str.split(';') if s.strip()]
            target_locations = [tuple(map(int, s.split(','))) for s in target_locations_str.split(';') if s.strip()]
            weights = list(map(int, weights.split(',')))
            
            dataset = {
                "vehicle_locations": vehicle_locations,
                "target_locations": target_locations,
                "weights": weights
            }
            
            dataset = format_dataset(dataset, precision)
            
            json_file_path = os.path.join('cached_datasets', f"dataset_{ds_no}.json")
            with open(json_file_path, 'w') as json_file:
                json.dump(dataset, json_file) 
            saved += 1
    print(f"Parsed and saved {saved} Datasets")



if __name__ == "__main__":
    dataset = {
        "vehicle_locations" : [(1, 2), (2, 3), (3, 4)],
        "target_locations" : [(3, 6), (1, 7), (2, 4)]
    }
    
    parse_and_save()

