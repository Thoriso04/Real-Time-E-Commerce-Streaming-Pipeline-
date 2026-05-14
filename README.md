Real-Time E-Commerce Observability Pipeline
This project demonstrates a high-velocity, cloud-native streaming architecture built to solve the "Batch-Processing Latency" problem in modern e-commerce. It utilizes a Lambda-lite pattern to ingest, process, and visualize customer behavior and system health in under 30 seconds.

Key Features
Real-Time Revenue Tracking: 5-minute tumbling windows for category-level sales analytics.

Automated Cart Recovery: Identification of high-value cart abandonments for immediate marketing intervention.

Operational Resilience: Implementation of a Dead Letter Queue (DLQ) and TRY_CAST logic to handle "poison messages" and malformed JSON.

Personalization Insights: Real-time joining of clickstream events with customer reference data to trigger behavioral alerts.

