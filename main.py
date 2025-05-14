"""
Enhanced Video Caching System with Optimization Strategies and Iterative Local Search

Key Improvements:
1. Request-aware video prioritization
2. Endpoint latency optimization
3. Size-aware placement
4. Cache popularity tracking
5. Better validation checks
6. Iterative Local Search for further optimization
"""

import os
from collections import defaultdict
import copy
import random

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

    # Check 4: Validate all videos exist
    for cache in cache_servers:
        for vid in cache['videos']:
            if vid < 0 or vid >= V:
                print(f"Validation Error: Invalid video ID {vid}")
                valid = False

    if valid:
        print("Validation Successful: All constraints satisfied")
    else:
        print("Validation Failed: One or more validation errors found.")
    
    return valid

def calculate_score(requests, endpoints, cache_servers, video_sizes):
    """Calculate score with optimized video-cache lookup"""
    total_saved_time = 0
    total_requests = sum(r[2] for r in requests)  # Precompute total requests
    
    # Build video to cache mapping for faster access
    video_cache_map = defaultdict(set)
    for cache_id, cache in enumerate(cache_servers):
        for vid in cache['videos']:
            video_cache_map[vid].add(cache_id)

    for vid, endpoint_id, num_requests in requests:
        endpoint = endpoints[endpoint_id]
        best_latency = endpoint['data_center_latency']
        
        # Check all caches that have this video
        for cache_id in video_cache_map.get(vid, set()):
            if cache_id in endpoint['cache_latencies']:
                cache_latency = endpoint['cache_latencies'][cache_id]
                best_latency = min(best_latency, cache_latency)
        
        saved_time = (endpoint['data_center_latency'] - best_latency) * num_requests
        total_saved_time += saved_time

    return (total_saved_time * 1000) // total_requests if total_requests > 0 else 0

def basic_cache_placement(requests, endpoints, video_sizes, C, X):
    """Original greedy placement strategy for comparison"""
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]
    
    # Sort videos by size (smallest first)
    sorted_videos = sorted(range(len(video_sizes)), key=lambda v: video_sizes[v])
    
    for vid in sorted_videos:
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers[cache_id]['remaining_capacity']:
                cache_servers[cache_id]['videos'].add(vid)
                cache_servers[cache_id]['remaining_capacity'] -= video_sizes[vid]
                break
    
    return cache_servers

def preprocess_requests(requests, endpoints, video_sizes):
    """Calculate video importance metrics for enhanced placement"""
    video_stats = defaultdict(lambda: {
        'total_demand': 0,
        'endpoints': set(),
        'latency_potential': 0
    })

    for vid, endpoint_id, num_requests in requests:
        stats = video_stats[vid]
        stats['total_demand'] += num_requests
        stats['endpoints'].add(endpoint_id)
        
        endpoint = endpoints[endpoint_id]
        dc_latency = endpoint['data_center_latency']
        min_latency = min(endpoint['cache_latencies'].values()) if endpoint['cache_latencies'] else dc_latency
        stats['latency_potential'] += (dc_latency - min_latency) * num_requests
    
    return video_stats

def find_optimal_cache(vid, video_size, endpoints, video_stats, cache_servers):
    """Find best cache for a video considering multiple factors"""
    best_cache = None
    best_score = -1
    
    for endpoint_id in video_stats['endpoints']:
        endpoint = endpoints[endpoint_id]
        for cache_id, latency in endpoint['cache_latencies'].items():
            cache = cache_servers[cache_id]
            
            if video_size <= cache['remaining_capacity']:
                # Calculate placement score
                latency_improvement = endpoint['data_center_latency'] - latency
                demand_factor = video_stats['total_demand'] / len(video_stats['endpoints'])
                score = latency_improvement * demand_factor
                
                # Prefer caches with more remaining capacity when scores are equal
                if score > best_score or (score == best_score and cache['remaining_capacity'] > cache_servers[best_cache]['remaining_capacity']):
                    best_score = score
                    best_cache = cache_id
    
    return best_cache

def enhanced_cache_placement(requests, endpoints, video_sizes, C, X):
    """Optimized cache placement using multiple strategies"""
    cache_servers = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]
    video_stats = preprocess_requests(requests, endpoints, video_sizes)
    
    # Sort videos by priority (demand, latency potential, then size)
    sorted_videos = sorted(
        range(len(video_sizes)),
        key=lambda v: (
            -video_stats[v]['total_demand'],
            -video_stats[v]['latency_potential'],
            video_sizes[v]
        )
    )

    for vid in sorted_videos:
        best_cache = find_optimal_cache(
            vid, video_sizes[vid],
            endpoints, video_stats[vid],
            cache_servers
        )
        if best_cache is not None:
            cache_servers[best_cache]['videos'].add(vid)
            cache_servers[best_cache]['remaining_capacity'] -= video_sizes[vid]
    
    return cache_servers



def perturb_solution(solution, video_sizes, C, X, num_changes=3):
    """Randomly modify the solution to escape local optima"""
    new_solution = copy.deepcopy(solution)
    
    for _ in range(num_changes):
        # Randomly select a cache and a video to remove
        cache_id = random.randint(0, C-1)
        if not new_solution[cache_id]['videos']:
            continue
        
        vid = random.choice(list(new_solution[cache_id]['videos']))
        new_solution[cache_id]['videos'].remove(vid)
        new_solution[cache_id]['remaining_capacity'] += video_sizes[vid]
        
        # Try to place the video in another cache
        for new_cache_id in random.sample(range(C), C):
            if new_cache_id != cache_id and video_sizes[vid] <= new_solution[new_cache_id]['remaining_capacity']:
                new_solution[new_cache_id]['videos'].add(vid)
                new_solution[new_cache_id]['remaining_capacity'] -= video_sizes[vid]
                break
    
    return new_solution

def generate_neighbor(solution, video_sizes, C, X):
    """Generate a neighbor solution by swapping videos"""
    neighbor = copy.deepcopy(solution)
    
    # Randomly select two caches
    cache1, cache2 = random.sample(range(C), 2)
    if not neighbor[cache1]['videos'] or not neighbor[cache2]['videos']:
        return neighbor
    
    # Randomly select a video from each cache
    vid1 = random.choice(list(neighbor[cache1]['videos']))
    vid2 = random.choice(list(neighbor[cache2]['videos']))
    
    # Check if swap is feasible
    size_diff = video_sizes[vid1] - video_sizes[vid2]
    if (neighbor[cache1]['remaining_capacity'] + video_sizes[vid1] >= video_sizes[vid2] and
        neighbor[cache2]['remaining_capacity'] + video_sizes[vid2] >= video_sizes[vid1]):
        neighbor[cache1]['videos'].remove(vid1)
        neighbor[cache1]['videos'].add(vid2)
        neighbor[cache1]['remaining_capacity'] += size_diff
        
        neighbor[cache2]['videos'].remove(vid2)
        neighbor[cache2]['videos'].add(vid1)
        neighbor[cache2]['remaining_capacity'] -= size_diff
    
    return neighbor

def process_file(input_path, input_filename):
    """Process input file with enhanced caching"""
    print(f"\nProcessing {input_filename}...")
    
    with open(input_path, 'r') as f:
        V, E, R, C, X = map(int, f.readline().split())
        video_sizes = list(map(int, f.readline().split()))
        
        endpoints = []
        for _ in range(E):
            dc_latency, num_caches = map(int, f.readline().split())
            cache_latencies = {}
            for _ in range(num_caches):
                cache_id, latency = map(int, f.readline().split())
                cache_latencies[cache_id] = latency
            endpoints.append({
                'data_center_latency': dc_latency,
                'cache_latencies': cache_latencies
            })
        
        requests = []
        for _ in range(R):
            vid, endpoint_id, num_requests = map(int, f.readline().split())
            requests.append((vid, endpoint_id, num_requests))

    # Run basic algorithm for comparison
    basic_caches = basic_cache_placement(requests, endpoints, video_sizes, C, X)
    basic_score = calculate_score(requests, endpoints, basic_caches, video_sizes)
    
    # Run enhanced algorithm
    enhanced_caches = enhanced_cache_placement(requests, endpoints, video_sizes, C, X)
    enhanced_score = calculate_score(requests, endpoints, enhanced_caches, video_sizes)
    
    # Run ILS on enhanced solution
    optimized_caches = iterative_local_search(enhanced_caches, requests, endpoints, video_sizes, C, X)
    optimized_score = calculate_score(requests, endpoints, optimized_caches, video_sizes)
    
    # Operator: Largest video first strategy
    cache_servers2 = [{'videos': set(), 'remaining_capacity': X} for _ in range(C)]
    sorted_videos2 = sorted(range(V), key=lambda v: -video_sizes[v])
    for vid in sorted_videos2:
        for cache_id in range(C):
            if video_sizes[vid] <= cache_servers2[cache_id]['remaining_capacity']:
                cache_servers2[cache_id]['videos'].add(vid)
                cache_servers2[cache_id]['remaining_capacity'] -= video_sizes[vid]
                break

    # Generate output with optimized solution
    output_lines = []
    for cache_id, cache in enumerate(optimized_caches):
        if cache['videos']:
            output_lines.append(f"{cache_id} {' '.join(map(str, sorted(cache['videos'])))}")
    
    os.makedirs("output", exist_ok=True)
    output_filename = f"output/output_{os.path.splitext(input_filename)[0]}.txt"
    with open(output_filename, 'w') as f:
        f.write(f"{len(output_lines)}\n")
        f.write("\n".join(output_lines) + "\n")

    # Print comparison results
    print("\nAlgorithm Comparison:")
    print(f"  Basic Greedy Score:      {basic_score:>10,}")
    print(f"  Enhanced Cache Score:    {enhanced_score:>10,}")
    print(f"  Optimized (ILS) Score:   {optimized_score:>10,}")
    
    improvement_basic = optimized_score - basic_score
    improvement_pct_basic = (improvement_basic / basic_score * 100) if basic_score != 0 else float('inf')
    print(f"\nImprovement over Basic:    {improvement_basic:>+10,} ({improvement_pct_basic:+.2f}%)")
    
    improvement_enhanced = optimized_score - enhanced_score
    improvement_pct_enhanced = (improvement_enhanced / enhanced_score * 100) if enhanced_score != 0 else float('inf')
    print(f"Improvement over Enhanced: {improvement_enhanced:>+10,} ({improvement_pct_enhanced:+.2f}%)")
    
    print("--------------------------")
    score2 = calculate_score(requests, endpoints, cache_servers2, video_sizes)
    output_filename = f"output/output_largest_first_{os.path.splitext(input_filename)[0]}.txt"
    with open(output_filename, 'w') as f:
        f.write(f"{len(output_lines)}\n")
        f.write("\n".join(output_lines) + "\n")
    print(f"Score (largest first): {score2} | Output saved to: {output_filename}")

    # Validate optimized solution
    print("\nSolution Validation:")
    validate_solution(optimized_caches, video_sizes, X, V)
    print(f"\nOptimized output saved to: {output_filename}")

def main():
    """Main program entry point"""
    input_dir = "input"
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.in')]
    
    if not input_files:
        print("No input files found (*.in) in 'input' directory")
        return
    
    print(f"Found {len(input_files)} input files:")
    for i, f in enumerate(input_files, 1):
        print(f"  {i}. {f}")
    
    for filename in input_files:
        try:
            full_path = os.path.join(input_dir, filename)
            process_file(full_path, filename)
        except Exception as e:
            print(f"\nError processing {filename}: {str(e)}")

if __name__ == '__main__':
    main()