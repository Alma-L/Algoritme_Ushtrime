
"""
Problem Approach:
Basic Greedy Caching with First-Fit Strategy

Key Characteristics:
1. Greedy Heuristic:
   - Processes videos in original order (0 → V-1)
   - Places each video in first cache with sufficient space
   - Never revisits previous placement decisions

2. Validation Focus:
   - Ensures cache capacity constraints (X=100MB)
   - Validates output format requirements
   - Checks for duplicate video placements (bonus safety)
"""

def validate_solution(cache_servers, video_sizes, X, V):
    valid = True
    print("\nRunning validation checks...")
    
    # Check 1: Video sizes and cache capacity constraints
    if any(v < 0 for v in video_sizes):
        print("Validation Error: Negative video size found.")
        valid = False
    if any(cache['remaining_capacity'] < 0 for cache in cache_servers):
        print("Validation Error: Cache remaining capacity is negative.")
        valid = False

    # Check 2: Cache capacity constraints
    for cid, cache in enumerate(cache_servers):
        total_size = sum(video_sizes[vid] for vid in cache['videos'])
        if total_size > X:
            print(f"Validation Error: Cache {cid} exceeds capacity. Total size: {total_size}/{X}MB")
            valid = False

    # Check 3: Video uniqueness across caches
    all_videos = set()
    for cache in cache_servers:
        for vid in cache['videos']:
            if vid in all_videos:
                print(f"Validation Error: Video {vid} appears in multiple caches")
                valid = False
            all_videos.add(vid)

    # Check 4: Submission format validation
    submission = []
    for cache_id, cache in enumerate(cache_servers):
        if cache['videos']:
            sorted_vids = sorted(cache['videos'])
            submission.append(f"{cache_id} {' '.join(map(str, sorted_vids))}")

    try:
        for line in submission:
            parts = line.split()
            cache_id = int(parts[0])
            videos = list(map(int, parts[1:]))

            # Check video IDs validity
            for vid in videos:
                if vid < 0 or vid >= V:
                    print(f"Validation Error: Invalid video ID {vid} in cache {cache_id}")
                    valid = False

            # Check for duplicates in cache
            if len(videos) != len(set(videos)):
                print(f"Validation Error: Duplicate video IDs found in cache {cache_id}")
                valid = False
    except ValueError:
        print("Validation Error: Non-integer values in output")
        valid = False

    if valid:
        print("Validation Successful: All constraints satisfied")
    return valid

def calculate_score(cache_servers, endpoints, requests):
    total_time_saved_ms = 0
    total_requests = sum(rn for (_, _, rn) in requests)
    
    for Rv, Re, Rn in requests:
        endpoint = endpoints[Re]
        LD = endpoint['data_center_latency']
        connected_caches = endpoint['cache_latencies'].keys()
        
        min_latency = LD
        for cache_id in connected_caches:
            if Rv in cache_servers[cache_id]['videos']:
                Lc = endpoint['cache_latencies'][cache_id]
                if Lc < min_latency:
                    min_latency = Lc
        
        time_saved = max(LD - min_latency, 0) * Rn
        total_time_saved_ms += time_saved
    
    if total_requests == 0:
        return 0
    return (total_time_saved_ms * 1000) // total_requests

def main():
    # Configuration - kept as original
    V = 5  # Number of videos
    E = 2  # Number of endpoints
    R = 4  # Number of request descriptions
    C = 3  # Number of cache servers
    X = 100  # Capacity of each cache server (MB)

    video_sizes = [50, -50, 80, 30, 150]  # Video 4 exceeds cache capacity
    endpoints = [
        {'data_center_latency': 1000, 'cache_latencies': {0: 100, 2: 200, 1: 300}},
        {'data_center_latency': 500, 'cache_latencies': {}}
    ]
    requests = [
        (3, 0, 1500),
        (0, 1, 1000),
        (4, 0, 500),
        (1, 0, 1000)
    ]

    # Initialize cache servers
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]

    # Video distribution logic
    sorted_videos = sorted(range(V), key=lambda v: video_sizes[v])
    for vid in sorted_videos:
        placed = False
        print(f"\nAttempting to place Video {vid} (size {video_sizes[vid]}MB)...")
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                print(f"  Video {vid} can be placed in Cache {cache_id}: Remaining capacity = {cache_servers[cache_id]['remaining_capacity']}MB")
                print(f"  Placing Video {vid} in Cache {cache_id}...")
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                print(f"  After placing Video {vid}: Cache {cache_id} remaining capacity {cache_servers[cache_id]['remaining_capacity']}MB")
                placed = True
                break
        if not placed:
            print(f"Warning: Video {vid} (size {video_sizes[vid]}MB) could not be stored in any cache!")

    # Generate output
    submission = []
    print("\nFinal cache states:")
    for cache_id, cache in enumerate(cache_servers):
        if cache['videos']:
            sorted_vids = sorted(cache['videos'])
            submission.append(f"{cache_id} {' '.join(map(str, sorted_vids))}")
            print(f"  Cache {cache_id}: Stored Videos {sorted_vids}, Remaining Capacity: {cache['remaining_capacity']}MB")

    print(f"\nTotal number of caches used: {len(submission)}")
    for line in submission:
        print(line)

    # Validation and scoring
    validate_solution(cache_servers, video_sizes, X, V)
    score = calculate_score(cache_servers, endpoints, requests)
    print(f"\nCalculated Score: {score}")

if __name__ == "__main__":
    main()