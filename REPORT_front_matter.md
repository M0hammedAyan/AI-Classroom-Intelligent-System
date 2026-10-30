# PROJECT REPORT

## VISTA: AI-BASED CLASSROOM ATTENDANCE MONITORING AND ACADEMIC RISK PREDICTION SYSTEM

**A Major Project Report submitted in partial fulfillment of the requirements for the award of the degree of**

### BACHELOR OF ENGINEERING
**in**
### ARTIFICIAL INTELLIGENCE & MACHINE LEARNING

---

### Submitted By:
- **Mohammed Ayan** (1DA22AI031)
- **Saheel Pradhan** (1DA22AI044)
- **Sujal Agrahari** (1DA22AI055)
- **Aryan Raj Singh** (1DA22AI010)

### Under the Guidance of:
**[Faculty Advisor Name]**  
Assistant Professor, Department of Artificial Intelligence & Machine Learning  

---

### DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING
**DR. AMBEDKAR INSTITUTE OF TECHNOLOGY / DSATM**  
*(An Autonomous Institution Affiliated to Visvesvaraya Technological University, Belagavi)*  
Bengaluru – 560056, Karnataka, India  
**Academic Year: 2026–2027**

---

<div style="page-break-after: always;"></div>

## CERTIFICATE

Certified that the project work entitled **"VISTA: AI-Based Classroom Attendance Monitoring and Academic Risk Prediction System"** is a bona fide work carried out by **Mohammed Ayan (1DA22AI031)**, **Saheel Pradhan (1DA22AI044)**, **Sujal Agrahari (1DA22AI055)**, and **Aryan Raj Singh (1DA22AI010)** in partial fulfillment for the award of the degree of **Bachelor of Engineering in Artificial Intelligence & Machine Learning** of the Visvesvaraya Technological University, Belagavi during the academic year 2026–2027. It is certified that all corrections/suggestions indicated for internal assessment have been incorporated in the report deposited in the departmental library. The project report has been approved as it satisfies the academic requirements in respect of project work prescribed for the said degree.

<br><br>

----------------------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -----------------------------------  
**[Guide Name]** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Head of Department**  
Project Guide &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Dept. of AI & ML  
Dept. of AI & ML  

<br><br>
**External Examiners:**

Name of the Examiner &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Signature with Date  
1. _____________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; _____________________________  
2. _____________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; _____________________________  

---

<div style="page-break-after: always;"></div>

## ACKNOWLEDGEMENTS

The satisfaction that accompanies the successful completion of any task would be incomplete without the mention of people whose ceaseless cooperation made it possible, whose constant guidance and encouragement served as a beacon of light and crowned our efforts with success.

We express our profound gratitude to our institution and management for providing the infrastructure and technical environment to carry out this project.

We convey our heartfelt gratitude to our Head of the Department, **Department of Artificial Intelligence & Machine Learning**, for continuous support and valuable advice throughout the tenure of the course.

We express our sincere and heartfelt thanks to our guide, **[Guide Name]**, Assistant Professor, Department of Artificial Intelligence & Machine Learning, for invaluable guidance, constructive suggestions, and keen interest shown throughout the course of this work.

Finally, we express our gratitude to our family members and friends who helped us directly or indirectly in completing this project successfully.

<br>
**Mohammed Ayan**  
**Saheel Pradhan**  
**Sujal Agrahari**  
**Aryan Raj Singh**

---

<div style="page-break-after: always;"></div>

## ABSTRACT

Manual attendance marking in higher educational institutions consumes approximately 10 to 15 minutes per lecture session and remains vulnerable to proxy attendance, physical record tampering, and human administrative errors. Concurrently, academic institutions lack proactive mechanisms to identify academically vulnerable students until after end-semester examinations conclude, by which time remediation is impossible. This project presents **VISTA (Vision-based Intelligent Student Tracking & Academics)**, an end-to-end, on-premise intelligent classroom management system integrating deep facial recognition attendance marking with early academic risk prediction and explainable artificial intelligence (XAI).

The biometric vision subsystem employs a multi-stage architecture consisting of the Sample and Computation Redistribution for Efficient Face Detection (SCRFD) model for robust face localization, an ArcFace ResNet-50 backbone for extracting 512-dimensional angular margin facial embeddings, a cosine distance gallery matcher, and a secondary ResNet-50 personal classification fallback trained on local institutional datasets. Anti-spoofing is enforced using multi-metric texture and geometry heuristics. For academic monitoring, the platform computes 8 longitudinal temporal features and 3 critical override flags, feeding an XGBoost decision tree classifier paired with SHAP (SHapley Additive exPlanations) to transparently identify feature drivers pushing students toward low, medium, or high risk. The backend is implemented in FastAPI providing 114 RESTful endpoints, 24 relational database tables, role-based access control across 6 institutional roles (Admin, Head of School, Head of Program, Mentor, Teacher, and Student), automated midnight risk recalculation via APScheduler, and real-time dashboard updates via WebSockets.

Empirical evaluation on a 20-student cohort across 20,130 processed face samples achieves a **90.10% test accuracy** (Split B) on the ResNet-50 classifier and an optimal ArcFace F1-score of **0.9246** at a cosine similarity threshold of 0.30, with a controlled pilot accuracy of **100%** on 14 images of 2 enrolled students. Latency profiling demonstrates full-frame face detection at **71.23 ms** and single-vector matching at **0.318 ms**, processing a full classroom of 60 students in **0.683 seconds** on standard x86 consumer CPUs without GPU requirements. The entire system operates strictly on-premise, preserving data sovereignty and providing higher education institutions with a scalable, privacy-preserving automated intelligence solution.

---

<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS

- **Certificate**
- **Acknowledgements**
- **Abstract**
- **List of Figures**
- **List of Tables**
- **Chapter 1: Introduction**
  - 1.1 Overview
  - 1.2 Problem Statement
  - 1.3 Objectives
  - 1.4 Organization of the Report
- **Chapter 2: Literature Survey**
  - 2.1 Previous Studies
  - 2.2 Summary of Findings
  - 2.3 Research Gap
- **Chapter 3: Software Requirement Specification**
  - 3.1 Hardware Requirements
  - 3.2 Software Requirements
- **Chapter 4: System Design**
  - 4.1 System Architecture
  - 4.2 Use Cases and Actor Interactions
  - 4.3 Data Flow Diagrams (DFD Level 0, 1, and 2)
- **Chapter 5: Implementation**
  - 5.1 Introduction
  - 5.2 Module Implementation
  - 5.3 Model Development
  - 5.4 Deployment Details
  - 5.5 Summary
- **Chapter 6: System Testing**
  - 6.1 Testing Objectives
  - 6.2 Testing Methodology
  - 6.3 Test Cases and Results
  - 6.4 Error Handling and Edge Cases
  - 6.5 Summary
- **Chapter 7: Results and Discussion**
  - 7.1 Experimental Setup
  - 7.2 Output Analysis
  - 7.3 Performance Metrics and Threshold Sweeps
  - 7.4 Limitations of Evaluation
  - 7.5 List of Required Interface Screenshots
  - 7.6 Summary
- **Applications**
- **Conclusions and Future Enhancements**
- **References**

---

<div style="page-break-after: always;"></div>

## LIST OF FIGURES

- **Fig 4.1:** High-Level Four-Tier System Architecture of VISTA
- **Fig 4.2:** Use Case Diagram for Multi-Role Operations
- **Fig 4.3:** Data Flow Diagram (Level 0 — Context Diagram)
- **Fig 4.4:** Data Flow Diagram (Level 1 — Functional Decomposition)
- **Fig 4.5:** Data Flow Diagram (Level 2 — Facial Recognition & Attendance Process)
- **Fig 5.1:** Multi-Stage Facial Recognition and Dual-Inference Pipeline Flow
- **Fig 5.2:** Academic Risk Feature Vector Extraction and Classification Workflow
- **Fig 7.1:** Training and Validation Loss Curves for ResNet-50 Face Classifier
- **Fig 7.2:** Confusion Matrix for 20-Class Student Face Classification (Split B)
- **Fig 7.3:** Latency Scaling as a Function of Classroom Face Count

---

## LIST OF TABLES

- **Table 2.1:** Comparative Summary of Face Recognition and Academic Risk Literature
- **Table 3.1:** Hardware Requirements Specification
- **Table 3.2:** Software Requirements Specification and Pinned Dependencies
- **Table 4.1:** Actor Roles and Scope of Operations
- **Table 4.2:** Use Case Specifications for Primary Operational Workflows
- **Table 5.1:** Implemented Backend API Route Modules and Endpoint Breakdown
- **Table 5.2:** Database Relational Schema Specification (24 Tables)
- **Table 5.3:** Deployment and Infrastructure Specifications
- **Table 6.1:** Vision Module Integration Test Cases and Execution Results
- **Table 6.2:** Machine Learning Risk Engine Unit Test Cases and Execution Results
- **Table 7.1:** Empirical Cosine Similarity Threshold Sweep for ArcFace Matching
- **Table 7.2:** ResNet-50 Personal Face Classifier Performance on Split B
- **Table 7.3:** Execution Latency and Throughput per Pipeline Component
- **Table 7.4:** Group Photo Latency Scaling Projection across Classroom Densities
- **Table 7.5:** Academic Risk Classifier Evaluation on Synthetic Dataset
- **Table 7.6:** Hardware Resource Utilization Profile
