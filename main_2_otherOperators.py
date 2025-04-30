import os
from collections import defaultdict

def validate_solution(cache_servers, video_sizes, X, V):
    valid = True
    print("\nRunning validation checks...")

    if any(v < 0 for v in video_sizes):
        print("Validation Error: Negative video size found.")
        valid = False
    if any(cache['remaining_capacity'] < 0 for cache in cache_servers):
        print("Validation Error: Cache remaining capacity is negative.")
        valid = False

    for cid, cache in enumerate(cache_servers):
        total_size = sum(video_sizes[vid] for vid in cache['videos'])
        if total_size > X:
            print(f"Validation Error: Cache {cid} exceeds capacity. Total size: {total_size}/{X}MB")
            valid = False

    all_videos = set()
    for cache in cache_servers:
        for vid in cache['videos']:
            if vid in all_videos:
                print(f"Validation Error: Video {vid} appears in multiple caches")
                valid = False
            all_videos.add(vid)

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

            for vid in videos:
                if vid < 0 or vid >= V:
                    print(f"Validation Error: Invalid video ID {vid} in cache {cache_id}")
                    valid = False

            if len(videos) != len(set(videos)):
                print(f"Validation Error: Duplicate video IDs found in cache {cache_id}")
                valid = False
    except ValueError:
        print("Validation Error: Non-integer values in output")
        valid = False

    if valid:
        print("Validation Successful: All constraints satisfied")
    else:
        print("Validation Failed: One or more validation errors found.")
    
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

def process_file(input_path, input_filename):
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
        video_request_counts = defaultdict(int)
        for _ in range(R):
            vid, endpoint_id, num_requests = map(int, f.readline().split())
            requests.append((vid, endpoint_id, num_requests))
            video_request_counts[vid] += num_requests

    # Initialize caches
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]

    # --- Operator 1: Sort Videos by Impact Score (Requests per MB) ---  impact = total_requests / video_size
    sorted_videos_operator_1 = sorted(
        range(V),
        key=lambda v: video_request_counts[v] / video_sizes[v] if video_sizes[v] > 0 else 0,
        reverse=True
    )

    for vid in sorted_videos_operator_1:
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                break

    score_operator_1 = calculate_score(requests, endpoints, cache_servers, video_sizes)
    print(f"File: {input_path} | Score with Operator 1 (Video Sorted by Impact): {score_operator_1}")

    # Reset cache servers for Operator 2
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]

    # --- Operator 2: Best-fit Cache Selection based on Latency Savings ---  Place the video in the cache connected to endpoints with the most requests and best latencies.
    for vid in sorted_videos_operator_1:  # reuse the sorted videos for consistency
        cache_weights = defaultdict(int)
        for vid_r, ep_id, reqs in requests:
            if vid_r != vid:
                continue
            endpoint = endpoints[ep_id]
            for cid, latency in endpoint['cache_latencies'].items():
                gain = endpoint['data_center_latency'] - latency
                if gain > 0:
                    cache_weights[cid] += reqs * gain

        sorted_caches = sorted(cache_weights.items(), key=lambda x: -x[1])
        for cache_id, _ in sorted_caches:
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                break

    score_operator_2 = calculate_score(requests, endpoints, cache_servers, video_sizes)
    print(f"File: {input_path} | Score with Operator 2 (Best-fit Cache Selection by Latency): {score_operator_2}")

    output_lines = []
    for cache_id, cache in enumerate(cache_servers):
        if cache['videos']:
            line = f"{cache_id} {' '.join(map(str, sorted(cache['videos'])))}"
            output_lines.append(line)

    # Save to output file
    os.makedirs("output", exist_ok=True)
    output_filename = f"output/output_latency_based{os.path.splitext(input_filename)[0]}.txt"
    with open(output_filename, 'w') as f:
        f.write(f"{len(output_lines)}\n")
        f.write("\n".join(output_lines) + "\n")

    # Validate solution
    is_valid = validate_solution(cache_servers, video_sizes, X, V)
    if is_valid:
        print(f"File: {input_path} | Validation Successful.")
    else:
        print(f"File: {input_path} | Validation Failed. See error messages above.")

# Main function to iterate over files
def main():
    input_folder = "input"
    if not os.path.exists(input_folder):
        print(f"Folder '{input_folder}' does not exist.")
        return

    for filename in os.listdir(input_folder):
        if filename.endswith(".in"):
            filepath = os.path.join(input_folder, filename)
            process_file(filepath, filename)

if __name__ == "__main__":
    main()
