def main():
    V = 5  # Number of videos
    E = 2  # Number of endpoints
    R = 4  # Number of request descriptions
    C = 3  # Number of cache servers
    X = 100  # Capacity of each cache server (MB)

    # Video sizes
    video_sizes = [50, 50, 80, 30, 110]

    # Endpoints
    endpoints = [
        {
            'data_center_latency': 1000,
            'cache_latencies': {0: 100, 2: 200, 1: 300}
        },
        {
            'data_center_latency': 500,
            'cache_latencies': {}
        }
    ]

    # Requests
    requests = [
        (3, 0, 1500),
        (0, 1, 1000),
        (4, 0, 500),
        (1, 0, 1000)
    ]

    # Initialize cache servers
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]

    # Sort videos by size (smallest first) to optimize storage
    sorted_videos = sorted(range(V), key=lambda v: video_sizes[v])

    # Distribute videos fairly across caches
    for vid in sorted_videos:
        placed = False
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                placed = True
                break
        if not placed:
            print(f"Warning: Video {vid} could not be stored in any cache!")

    # Generate the output
    submission = []
    for cache_id, cache in enumerate(cache_servers):
        if cache['videos']:
            submission.append(f"{cache_id} {' '.join(map(str, cache['videos']))}")

    # Print results
    print(len(submission))
    for line in submission:
        print(line)


if __name__ == "__main__":
    main()
