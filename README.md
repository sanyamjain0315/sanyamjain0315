<h1 align="center">Sanyam Jain</h1>

<p align="center">
  <strong>Applied AI &amp; backend engineering</strong><br>
  M.S. Computer Science candidate · Boston University
</p>

<p align="center">
  <a href="#selected-work">Selected work</a> ·
  <a href="#current-work">Current work</a> ·
  <a href="https://www.linkedin.com/in/sanyamsuniljain/">LinkedIn</a>
</p>

## Selected work

### NoDust

**Real-time air-quality monitoring** · `Kafka` `Spark` `PostgreSQL`

I built a streaming pipeline that reads simulated sensor data from Kafka, stores hourly averages in PostgreSQL, and publishes anomaly alerts back to Kafka.

[![NoDust architecture showing simulated sensors, Kafka, Spark, and PostgreSQL](https://raw.githubusercontent.com/sanyamjain0315/NoDust/main/material/nodust-architecture.png)](https://github.com/sanyamjain0315/NoDust/blob/main/material/nodust-architecture.png)

[Source code](https://github.com/sanyamjain0315/NoDust) · [Run with Docker Compose](https://github.com/sanyamjain0315/NoDust#quick-start)

### CUDA wildfire simulation

**Monte Carlo simulation** · `C++` `CUDA`

I wrote the CPU baseline and implemented dynamic parallelism in the GPU version. In our benchmark, kernel time was `~1.2 ms` with dynamic parallelism and `~40 ms` with one CUDA stream per simulation.

[Source code](https://github.com/sanyamjain0315/cuda-wildfirespread-simulation) · [Benchmark report](https://github.com/sanyamjain0315/cuda-wildfirespread-simulation/blob/main/writeup/CUDA%20project%20report.pdf)

- **Go stream-processing research** — I evaluated cache bypassing, async prefetching, and cross-batch caching across read-heavy and write-heavy workloads.
- **[YT Gatekeeper](https://github.com/sanyamjain0315/yt-gatekeeper)** — I published a Chrome extension that shows your daily YouTube time and adds a short pause before you keep watching. [Chrome Web Store](https://chromewebstore.google.com/detail/yt-gatekeeper/paggklmpeoleddkmffideelfdcgmcbjm)

## Current work

- **BU Spark! · Phone-tree navigation** — I’m building an agent for a healthcare administration client. I wrote a simulator to test how quickly and reliably local models decide when to dial, wait, or hand off.
- **Talks.ai · Sign language recognition** — I’ve trained models for continuous American Sign Language recognition and benchmarked seven video recognition architectures.
