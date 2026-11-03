# CHAPTER 2: LITERATURE SURVEY

## 2.1 Previous Studies
The convergence of deep convolutional neural networks, computer vision, and educational data mining has inspired extensive research over the past decade. This section reviews seminal and peer-reviewed studies foundational to biometric attendance systems and academic performance forecasting.

### 2.1.1 Face Detection Architectures
Robust face localization in unconstrained group environments is the critical precursor to facial recognition. Early approaches relied heavily on the Viola-Jones cascade classifier utilizing Haar-like wavelets and AdaBoost. While computationally efficient, Viola-Jones suffers from unacceptable false-negative rates under non-uniform illumination, head rotation, and slight occlusion common in university lecture halls.

Zhang et al. (2016) proposed **Multi-task Cascaded Convolutional Networks (MTCNN)**, which revolutionized face detection by cascading three deep subnetworks: the Proposal Network (P-Net), Refine Network (R-Net), and Output Network (O-Net). MTCNN simultaneously predicts bounding boxes and regresses five facial landmark coordinates. However, MTCNN suffers from high computational latency when processing high-resolution images containing dozens of small faces due to its dense sliding-window proposal step.

Deng et al. (2020) introduced **RetinaFace**, a single-stage pixel-level face localization framework utilizing multi-task learning to predict bounding boxes, 2D facial landmarks, and 3D face shape vertices. Building upon these principles, Guo et al. (2021) introduced **Sample and Computation Redistribution for Efficient Face Detection (SCRFD)**. SCRFD re-evaluates computation allocations across network backbones and feature pyramids, training lightweight networks that achieve exceptional localization accuracy on tiny and partially occluded faces with remarkably low FLOP counts. SCRFD is particularly suited for CPU-based classroom inference where dozens of faces must be detected within milliseconds.

### 2.1.2 Deep Feature Representation and Angular Loss Functions
The paradigm of facial verification shifted from handcrafted local binary patterns (LBP) and Gabor filters to deep metric learning with Schroff et al. (2015) in **FaceNet**. FaceNet maps facial images directly into a compact Euclidean space using deep convolutional networks optimized via Triplet Loss. The triplet objective minimizes the anchor-positive distance while maximizing the anchor-negative distance:
$$\mathcal{L}_{\text{triplet}} = \sum_{i}^{N} \left[ \left\| f(x_i^a) - f(x_i^p) \right\|_2^2 - \left\| f(x_i^a) - f(x_i^n) \right\|_2^2 + \alpha \right]_+$$
While highly influential, triplet loss suffers from combinatorial explosion during mining of semi-hard negative triplets, resulting in slow convergence and training instability on large cohorts.

To overcome these constraints, angular margin loss formulations were developed. Wang et al. (2018) introduced **CosFace** (Large Margin Cosine Loss), which incorporates an additive cosine margin directly into the softmax formulation. Deng et al. (2019) subsequently presented **ArcFace (Additive Angular Margin Loss)**. ArcFace incorporates an additive angular margin $m$ directly within the cosine angle space:
$$\mathcal{L}_{\text{arc}} = -\frac{1}{N} \sum_{i=1}^N \log \frac{e^{s(\cos(\theta_{y_i} + m))}}{e^{s(\cos(\theta_{y_i} + m))} + \sum_{j \neq y_i}^N e^{s \cos \theta_j}}$$
Because the angular margin corresponds exactly to geodesic distance on the hyperspherical manifold, ArcFace produces embeddings with maximum intra-class compactness and inter-class discrepancy. Pretrained on large-scale datasets such as WebFace600K, ArcFace 512-dimensional embeddings provide state-of-the-art transferability without requiring fine-tuning for each newly enrolled student.

### 2.1.3 Multi-Object Tracking in Educational Environments
Tracking student identities across continuous video feeds or sequential photographic bursts requires robust data association. Bewley et al. (2016) proposed **Simple Online and Realtime Tracking (SORT)**, which combines Kalman filtering for motion estimation with the Hungarian algorithm for spatial bounding box association based on Intersection over Union (IoU). Wojke et al. (2017) extended SORT into **DeepSORT** by integrating deep appearance descriptor vectors into the association cost matrix, allowing tracks to persist through visual occlusions.

Zhang et al. (2022) developed **ByteTrack**, proposing the BYTE data association algorithm. Rather than discarding low-confidence detection boxes (as done in SORT and DeepSORT), ByteTrack retains all bounding boxes and associates both high-score and low-score detections sequentially, preserving true object tracks during severe occlusions. However, in fixed-camera classroom settings capturing static periodic snapshots rather than high-frame-rate video feeds, heavy Kalman motion propagation is often unnecessary; a direct greedy IoU association mechanism provides equivalent continuity with zero matrix inversion overhead.

### 2.1.4 Educational Data Mining & Academic Risk Prediction
Educational Data Mining (EDM) explores historical student indicators to forecast academic failure or dropouts. Cortez and Silva (2008) pioneered student performance prediction using secondary school data (the UCI Student Performance Dataset), demonstrating that past assessment trends combined with absence counts serve as primary determinants of end-semester marks. Subsequent studies by Romero et al. and subsurface learning analytics researchers established that attendance percentage serves as the single strongest leading indicator of student retention.

Chen and Guestrin (2016) introduced **XGBoost (eXtreme Gradient Boosting)**, a scalable tree boosting system utilizing second-order Taylor expansions of the loss function, weighted quantile sketches, and sparsity-aware split finding. XGBoost consistently outperforms standard feedforward neural networks and linear regressors on tabular academic data. To address the black-box nature of ensemble tree models, Lundberg and Lee (2017) formulated **SHAP (SHapley Additive exPlanations)** based on game-theoretic Shapley values, calculating exact, additive feature attributions:
$$g(z') = \phi_0 + \sum_{j=1}^M \phi_j z_j'$$
Applying SHAP to student risk modeling enables educational platforms to output transparent, actionable diagnostic reasons alongside numerical risk scores.

---

## 2.2 Summary of Findings
A systematic comparative analysis of existing literature across face recognition and academic performance forecasting is summarized in Table 2.1.

**Table 2.1: Comparative Summary of Face Recognition and Academic Risk Literature**

| Author & Year | Methodology / Model | Core Objective | Strengths | Limitations |
|---|---|---|---|---|
| **Schroff et al. (2015)** | FaceNet (Triplet Loss on CNN) | Face verification & clustering | Direct Euclidean mapping; compact vector representations | Combinatorial mining complexity; unstable gradient convergence |
| **Zhang et al. (2016)** | MTCNN (Cascaded CNNs) | Multi-task detection and landmark regression | Simultaneous bounding box and 5-point landmark estimation | Slow inference on high-resolution group photographs with small faces |
| **Deng et al. (2019)** | ArcFace (Additive Angular Margin Loss) | Hyperspherical feature representation | Geodesic metric separation; state-of-the-art open-set discriminative power | High sensitivity to alignment errors on extreme out-of-plane poses |
| **Guo et al. (2021)** | SCRFD (Sample/Computation Redistribution) | High-efficiency face detection | Superior recall on tiny and occluded faces; optimized for low-compute CPUs | Focused strictly on detection; requires separate recognition backbone |
| **Wojke et al. (2017)** | DeepSORT (Kalman + Deep Embedding) | Multi-object tracking under occlusion | Recovers tracks across visual occlusions using appearance features | Computational overhead; redundant for static single-frame classroom capture |
| **Cortez & Silva (2008)**| Decision Trees & Regression on UCI Dataset | Secondary student academic failure forecasting | Verified attendance and early test scores as dominant predictors | Evaluated on static snapshot data; lacks real-time classroom telemetry |
| **Chen & Guestrin (2016)**| XGBoost (Gradient Tree Boosting) | Tabular prediction across diverse domains | Handles missing values, non-linear feature interactions, prevents overfitting | Complex multi-tree ensembles lack native interpretability without XAI |
| **Lundberg & Lee (2017)**| SHAP (TreeExplainer) | Model-agnostic and tree-specific explanations | Mathematically consistent local feature attributions | Computationally demanding on deep ensembles with wide feature sets |

---

## 2.3 Research Gap
Despite significant advances across individual disciplines, a critical gap persists at the intersection of automated computer vision attendance monitoring and early academic risk intervention:

1. **Isolation of Attendance and Predictive Academics:** Existing commercial and open-source attendance applications treat attendance marking strictly as an isolated logging mechanism. They fail to channel daily presence and absence telemetry into automated predictive pipelines that forecast academic distress.
2. **Lack of Dual-Inference Recognition Resilience:** Contemporary open-set biometric systems rely solely on single-threshold cosine similarity against enrollment galleries. When subtle variations in classroom illumination, camera perspective, or facial expressions cause the similarity score to drop marginally below threshold, the system fails silently. Integrating a localized discriminative classifier as a secondary fallback remains unexplored in attendance architectures.
3. **Absence of Explainable Risk Diagnostics:** The few learning management platforms that incorporate machine learning risk prediction output binary flags ("At Risk" vs. "Normal") without transparent causal reasoning. Academic counselors and faculty mentors require explainable factor decompositions (e.g., distinguishing between a sharp attendance collapse versus chronic low marks) to formulate targeted student interventions.
4. **Cloud Vulnerability and Biometric Exposure:** Most modern commercial products rely on cloud computer vision APIs (e.g., AWS Rekognition, Microsoft Azure Face), introducing ongoing API costs, network latency dependencies, and severe student biometric privacy risks.

The VISTA system addresses these gaps by unifying SCRFD face detection, ArcFace angular embeddings, a secondary ResNet-50 fallback, heuristic anti-spoofing, and longitudinal XGBoost risk prediction with SHAP explanations into a unified, on-premise educational intelligence framework.
