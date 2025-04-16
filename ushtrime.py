import os
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

def calculate_score(requests, endpoints, cache_servers, video_sizes):
    total_saved_time = 0
    total_requests = 0

    for vid, endpoint_id, num_requests in requests:
        total_requests += num_requests
        endpoint = endpoints[endpoint_id]
        dc_latency = endpoint['data_center_latency']
        best_latency = dc_latency

        for cache_id, cache_latency in endpoint['cache_latencies'].items():
            if vid in cache_servers[cache_id]['videos']:
                best_latency = min(best_latency, cache_latency)

        saved = dc_latency - best_latency
        total_saved_time += saved * num_requests

    if total_requests == 0:
        return 0

    return (total_saved_time * 1000) // total_requests

def process_file(input_path):
    with open(input_path, "r") as f:
        V, E, R, C, X = map(int, f.readline().split())
        video_sizes = list(map(int, f.readline().split()))

        endpoints = []
        for _ in range(E):
            datacenter_latency, num_caches = map(int, f.readline().split())
            cache_latencies = {}
            for _ in range(num_caches):
                cache_id, latency = map(int, f.readline().split())
                cache_latencies[cache_id] = latency
            endpoints.append({
                'data_center_latency': datacenter_latency,
                'cache_latencies': cache_latencies
            })

        requests = []
        for _ in range(R):
            vid, endpoint_id, num_requests = map(int, f.readline().split())
            requests.append((vid, endpoint_id, num_requests))

    # Initialize caches
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]
    sorted_videos = sorted(range(V), key=lambda v: video_sizes[v])

    for vid in sorted_videos:
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                break

    # Generate submission
    submission = []
    for cache_id, cache in enumerate(cache_servers):
        if cache['videos']:
            sorted_vids = sorted(cache['videos'])
            submission.append(f"{cache_id} {' '.join(map(str, sorted_vids))}")

    # Save to output file
    output_filename = f"output_{os.path.splitext(input_path)[0]}.txt"
    with open(output_filename, "w") as out_file:
        out_file.write(f"{len(submission)}\n")
        for line in submission:
            out_file.write(f"{line}\n")

    # Calculate and print score
    score = calculate_score(requests, endpoints, cache_servers, video_sizes)
    print(f"File: {input_path} | Score: {score} | Output: {output_filename}")
        
    # Validate solution
    is_valid = validate_solution(cache_servers, video_sizes, X, V)
    print("Validation Successful." if is_valid else "Validation Failed.")

    if not is_valid:
        return

def main():
    for filename in os.listdir("."):
        if filename.endswith(".in"):
            process_file(filename)


if __name__ == "__main__":
    main()
