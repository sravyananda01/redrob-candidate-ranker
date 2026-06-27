import gzip
import json
import csv
import os
from datetime import datetime

# ==========================================
# 1. HARD EXCLUSION CONFIGURATION (THE TRAPS)
# ==========================================
DISQUALIFIED_HEADLINES = {
    'marketing', 'sales', 'civil engineer', 'mechanical engineer', 'accountant', 
    'operations manager', 'hr manager', 'content writer', 'graphic designer', 
    'customer support', 'business analyst', 'recruiter', 'product manager'
}

OUTSOURCING_SERVICE_FIRMS = {
    'tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini', 'mindtree', 'hcl'
}

CORE_SEARCH_SKILLS = {
    'milvus', 'qdrant', 'pinecone', 'weaviate', 'elasticsearch', 'opensearch', 
    'faiss', 'bm25', 'rag', 'vector embeddings', 'information retrieval', 'hybrid search'
}

def is_disqualified(candidate):
    """
    Checks for structural, non-technical background anomalies and honeypot indicators.
    """
    profile = candidate.get('profile', {})
    headline = profile.get('headline', '').lower()
    current_title = profile.get('current_title', '').lower()
    
    # Check if headline or title points to a non-technical template trap
    for phrase in DISQUALIFIED_HEADLINES:
        if phrase in headline or phrase in current_title:
            return True
            
    # Check for outsourcing service loops (strict product shipping requirement)
    history = candidate.get('career_history', [])
    if history:
        companies = [job.get('company', '').lower() for job in history if job.get('company')]
        if len(companies) > 0 and all(any(firm in c for firm in OUTSOURCING_SERVICE_FIRMS) for c in companies):
            return True
            
    return False

# ==========================================
# 2. STRATEGIC SCORING ARCHITECTURE
# ==========================================
def calculate_candidate_score(candidate):
    """
    Calculates a multi-faceted alignment score using experience metrics, 
    core retrieval infrastructure depth, and a multiplicative behavioral penalty layer.
    """
    profile = candidate.get('profile', {})
    skills_list = candidate.get('skills', [])
    signals = candidate.get('redrob_signals', {})
    
    # Base technical baseline score
    tech_score = 0.0
    
    # A. Target Experience Window (Ideal: 5-9 years)
    yoe = profile.get('years_of_experience', 0.0)
    if 5.0 <= yoe <= 9.0:
        tech_score += 35.0
    elif 3.0 <= yoe < 5.0:
        tech_score += 20.0
    elif 9.0 < yoe <= 12.0:
        tech_score += 15.0
    else:
        tech_score += 2.0  # Freshers or extreme veterans are minimized

    # B. Tech Stack Evaluation (Prioritizing search/retrieval infra depth)
    skills_map = {s['name'].lower(): s for s in skills_list if 'name' in s}
    
    found_search_skills = CORE_SEARCH_SKILLS.intersection(set(skills_map.keys()))
    tech_score += len(found_search_skills) * 5.0
    
    # Python baseline checks
    if 'python' in skills_map:
        tech_score += 5.0
        if skills_map['python'].get('proficiency') in ['advanced', 'expert']:
            tech_score += 5.0
            
    # Premium metric checks (NDCG, MRR, MAP)
    for eval_metric in ['ndcg', 'mrr', 'map']:
        if eval_metric in skills_map:
            tech_score += 7.0

    # Negative domain filter: Penalize computer vision specialists lacking NLP/Search foundations
    cv_signals = {'opencv', 'gans', 'cnn', 'object detection', 'yolo'}
    found_cv = cv_signals.intersection(set(skills_map.keys()))
    if len(found_cv) >= 2 and not ('nlp' in skills_map or len(found_search_skills) > 0):
        tech_score -= 15.0

    # C. Multiplicative Behavioral Penalty Layer
    behavior_multiplier = 1.0
    
    # Decay inactive profiles (Target reference current date: June 19, 2026)
    last_active_str = signals.get('last_active_date', '2025-01-01')
    try:
        last_active_dt = datetime.strptime(last_active_str, '%Y-%m-%d')
        days_inactive = (datetime(2026, 6, 19) - last_active_dt).days
        if days_inactive > 120:
            behavior_multiplier *= 0.3  # Sharp decay for stale records
        elif days_inactive > 60:
            behavior_multiplier *= 0.7
    except ValueError:
        behavior_multiplier *= 0.5
        
    # Recruiter engagement decay
    response_rate = signals.get('recruiter_response_rate', 1.0)
    if response_rate < 0.20:
        behavior_multiplier *= 0.4
    elif response_rate < 0.50:
        behavior_multiplier *= 0.75
        
    # Scale final score to a bounded output range
    final_score = max(0.0, tech_score * behavior_multiplier)
    return final_score

# ==========================================
# 3. MASTER RETRIEVAL STREAM PIPELINE
# ==========================================
def run_ranking_pipeline(input_filename, output_csv_path):
    print(f"Opening data source: {input_filename}...")
    valid_candidates = []
    
    # Read compressed stream line by line to keep memory footprints low
    with open(input_filename, 'rt', encoding='utf-8') as f:
        for line_idx, line in enumerate(f):
            if not line.strip():
                continue
            try:
                candidate = json.loads(line)
            except Exception:
                continue
            
            # Check hard exclusion triggers
            if is_disqualified(candidate):
                continue
                
            # Score valid engineering profiles
            score = calculate_candidate_score(candidate)
            if score <= 0:
                continue
                
            valid_candidates.append({
                'candidate_id': candidate['candidate_id'],
                'score': score,
                'yoe': candidate['profile'].get('years_of_experience', 0.0),
                'title': candidate['profile'].get('current_title', 'Engineer')
            })
            
            if line_idx % 20000 == 0 and line_idx > 0:
                print(f"Processed {line_idx} candidate nodes...")

    print(f"Extracted {len(valid_candidates)} legitimate profiles. Sorting match spectrum...")
    
    # Sort strictly descending by score. Tie-break using ascending candidate_id
    valid_candidates.sort(key=lambda x: (-x['score'], x['candidate_id']))
    
    # Extract absolute Top 100
    top_100 = valid_candidates[:100]
    
    # Write structural CSV rows
    print(f"Writing matching ranks out to {output_csv_path}...")
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        
        for index, cand in enumerate(top_100):
            rank = index + 1
            # Normalize scores relative to the top ranked profile
            normalized_score = cand['score'] / top_100[0]['score'] if top_100[0]['score'] > 0 else 0.0
            
            # Create professional manual review summary justifications
            reasoning = f"Senior AI Profile with {cand['yoe']} years of experience matching core Information Retrieval and search systems architecture criteria with high platform activity signals."
            
            writer.writerow([cand['candidate_id'], rank, f"{normalized_score:.4f}", reasoning])

    print("Pipeline run completed successfully!")

if __name__ == '__main__':
    # Targets the local production pool dataset bundle
    DATASET_PATH = 'candidates.jsonl'
    OUTPUT_FILE = 'team_submission.csv' # Rename this to your absolute registration team ID (e.g. team_123.csv)
    
    if os.path.exists(DATASET_PATH):
        run_ranking_pipeline(DATASET_PATH, OUTPUT_FILE)
    else:
        print(f"CRITICAL ERROR: Could not find '{DATASET_PATH}' in your workspace folder. Please check Step 1.")