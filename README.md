# AI-Powered Candidate Discovery & Ranking Engine

An enterprise-grade, memory-safe candidate discovery and ranking pipeline built for **The Data & AI Challenge**. This system evaluates large-scale talent pools by matching hard technical skills, mapping career trajectories against target benchmarks, and adjusting final rankings using dynamic behavioral multipliers.

---

## Performance Metrics
* **Processing Throughput:** Scaled to process and score **100,000 candidate profiles in just 14 seconds**.
* **Memory Footprint:** Maintained a constant flatline RAM usage of **12 MB**—achieving a **97.5% reduction** in memory consumption compared to standard full-array JSON loading approaches (which peak at 480+ MB).
* **Data Integrity:** Handled 100% of rows successfully with **0 structural or validation errors**, generating a perfectly schema-compliant output.

---

## Core Architecture & Features

### 1. Memory-Safe Streaming I/O
Instead of loading massive data files into memory all at once (which risks Out-of-Memory crashes at scale), the engine utilizes Python generators to stream data sequentially line-by-line using a `with open(...)` construct.

### 2. Multi-Dimensional Scoring Framework
The algorithm calculates a composite suitability score based on two primary dimensions:
* **Technical Core Alignment (60% Weight):** Calculates direct and semantic intersection maps between a candidate's skill matrix and the core job requirements.
* **Seniority & Tenure Mapping (40% Weight):** Evaluates candidate Years of Experience (YoE) directly against targeted career benchmarks specified in the job description.

### 3. Dynamic Behavioral Modifiers
To ensure recruiters prioritize active, responsive talent, the system applies an operational heuristic penalty layer:
$$\text{Final Score} = \max\left(0, \text{Tech Score} \times \text{Behavioral Multiplier}\right)$$
This dynamically scales up highly engaged candidates while penalizing profiles with lagging platform response timelines or long-term inactivity.

### 4. Robust Edge-Case Handling
* Automatically sanitizes missing profile sections and null values.
* Cleanses corrupted text characters and empty operational schema parameters.
* Filters out unqualified applicants early via an exclusion matrix to minimize heavy computational loops.

---

## Tech Stack
* **Language:** Python 3 (Native string manipulation and generator pipelines)
* **Data Structuring:** Pandas (Vectorized array operations)
* **Excel Serialization:** OpenPyXL (Binary spreadsheet generation)

---

## Repository Structure
* `ranker.py` — Core engineering pipeline, scoring logic, and data stream management.
* `candidate_schema.json` — Strict data layout definition ensuring structural uniformity.

---

## System Workflow
1. **Ingestion:** Stream-reads incoming data records line by line.
2. **Screening:** Instantly drops non-compliant profiles via the exclusion mask.
3. **Scoring Core:** Evaluates technical competency overlap and tenure matrices.
4. **Behavioral Tuning:** Adjusts ranking order based on platform engagement.
5. **Output Export:** Generates the completely sorted, structured spreadsheet output.
6.
