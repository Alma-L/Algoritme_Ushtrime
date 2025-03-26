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

def main():
    V = 5  # Number of videos
    E = 2  # Number of endpoints
    R = 4  # Number of request descriptions
    C = 3  # Number of cache servers
    X = 100  # Capacity of each cache server (MB)

    # Video sizes
    video_sizes = [50, 50, 80, 30, 110]

    # Endpoints data (not used in current implementation)
    endpoints = [
        {'data_center_latency': 1000, 'cache_latencies': {0: 100, 2: 200, 1: 300}},
        {'data_center_latency': 500, 'cache_latencies': {}}
    ]

    # Request data (not used in current implementation)
    requests = [
        (3, 0, 1500),
        (0, 1, 1000),
        (4, 0, 500),
        (1, 0, 1000)
    ]

    # Initialize cache servers with tracking of remaining capacity
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]

    # Sort videos by size (smallest first) to maximize storage efficiency
    sorted_videos = sorted(range(V), key=lambda v: video_sizes[v])

    # Distribute videos using first-fit algorithm
    for vid in sorted_videos:
        placed = False
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                placed = True
                break
        if not placed:
            print(f"Warning: Video Indexed {vid} (size {video_sizes[vid]}MB) could not be stored in any cache!")

    # Generate output in required format
    submission = []
    for cache_id, cache in enumerate(cache_servers):
        if cache['videos']:
            # Convert video IDs to sorted list for consistent output
            sorted_vids = sorted(cache['videos'])
            submission.append(f"{cache_id} {' '.join(map(str, sorted_vids))}")

    # Print submission (header + cache lines)
    print(len(submission))
    for line in submission:
        print(line)

    # Validation checks
    def validate_solution():
        valid = True

        # Check 1: Verify cache capacity constraints
        for cid, cache in enumerate(cache_servers):
            total_size = sum(video_sizes[vid] for vid in cache['videos'])
            if total_size > X:
                print(f"Validation Error: Cache {cid} exceeds capacity ({total_size}/{X}MB)")
                valid = False
        
        # Check 2: Verify video uniqueness across caches
        all_videos = set()
        for cache in cache_servers:
            for vid in cache['videos']:
                if vid in all_videos:
                    print(f"Validation Error: Video {vid} appears in multiple caches")
                    valid = False
                all_videos.add(vid)

        # Check 3: Verify output format
        try:
            for line in submission:
                parts = line.split()
                cache_id = int(parts[0])
                videos = list(map(int, parts[1:]))
                
                # Check video IDs are valid
                for vid in videos:
                    if vid < 0 or vid >= V:
                        print(f"Validation Error: Invalid video ID {vid} in cache {cache_id}")
                        valid = False
        except ValueError:
            print("Validation Error: Non-integer values in output")
            valid = False
        
        if valid:
            print("Validation Successful: All constraints satisfied")
        return valid

    # Run validation checks
    validate_solution()

if __name__ == "__main__":
    main()