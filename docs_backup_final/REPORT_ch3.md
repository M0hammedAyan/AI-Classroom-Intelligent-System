# CHAPTER 3: SOFTWARE REQUIREMENT SPECIFICATION

## 3.1 Hardware Requirements
The VISTA system has been engineered to run efficiently on commodity, off-the-shelf hardware without requiring dedicated enterprise GPU clusters. Table 3.1 outlines the minimum operational requirements and the recommended hardware specifications for both development/evaluation environments and production on-premise classroom deployment.

**Table 3.1: Hardware Requirements Specification**

| Component | Minimum Specification | Recommended Specification (Evaluated System) | Production Institutional Server |
|---|---|---|---|
| **Processor (CPU)** | Intel Core i5 (8th Gen) or AMD Ryzen 5 (4 cores, 2.5 GHz) | Intel Core i7-13700H / AMD Ryzen 7 (10–16 cores, 3.5+ GHz) | Intel Xeon Silver or AMD EPYC (16+ cores, 2.8+ GHz) |
| **System Memory (RAM)** | 8 GB DDR4 | 16 GB DDR4/DDR5 | 32 GB ECC DDR4/DDR5 |
| **Storage** | 20 GB available SSD storage | 50 GB NVMe PCIe 4.0 SSD | 250 GB NVMe SSD (RAID 1 mirrored) |
| **Graphics Card (GPU)** | Not Required (CPU inference mode active) | NVIDIA GeForce RTX 3050 (4 GB VRAM) — optional | NVIDIA RTX A4000 / T4 (16 GB) — optional for batch re-training |
| **Camera Sensor** | 1080p USB Webcam (2.0 Megapixels) | 4K Ultra-HD USB/IP Camera (8.0 Megapixels, f/2.0 aperture) | 4K Wide-Angle Pan-Tilt-Zoom (PTZ) IP Camera (PoE enabled) |
| **Network Interface** | 100 Mbps Ethernet / Wi-Fi 5 | 1 Gbps Ethernet / Wi-Fi 6 (802.11ax) | 10 Gbps SFP+ Ethernet |

---

## 3.2 Software Requirements
The software ecosystem encompasses the runtime execution environments, compilers, programming frameworks, database engines, and pinned third-party library dependencies across all architectural tiers.

### 3.2.1 Operating System and Base Environments
- **Operating System:** Windows 10/11 64-bit, Ubuntu Linux 22.04 LTS, or Red Hat Enterprise Linux 9.
- **Python Runtime:** Python 3.11.x (tested on CPython 3.11.9 64-bit).
- **Node.js Environment:** Node.js v18.x LTS or v20.x LTS with npm package manager (v10.x).
- **Relational Database Engine:** PostgreSQL 15.x / 16.x (production) or SQLite 3.x (local development/unit testing).
- **In-Memory Cache & Broker:** Redis Server v7.0+.

### 3.2.2 Pinned Software Dependencies
The core software specifications with exact version constraints verified from `vista/requirements.txt` and `vista/frontend/package.json` are tabulated in Table 3.2.

**Table 3.2: Software Requirements Specification and Pinned Dependencies**

| Layer / Ecosystem | Software Package | Pinned Version Constraint | Functional Purpose |
|---|---|---|---|
| **Backend API** | FastAPI | `>=0.111.0` | Asynchronous REST API routing, Pydantic validation, dependency injection |
| **ASGI Server** | Uvicorn | `>=0.29.0` | High-throughput asynchronous web server worker |
| **Process Manager** | Gunicorn | `>=23.0.0` | Production WSGI/ASGI master process supervisor |
| **Database ORM** | SQLAlchemy | `>=2.0.0` | 24-table declarative mapping and connection pooling |
| **PostgreSQL Driver**| Psycopg2-binary | `>=2.9.9` | C-optimized PostgreSQL database adapter |
| **Authentication** | PyJWT | `>=2.8.0` | Cryptographic HS256 JSON Web Token generation and validation |
| **Cryptography** | Bcrypt | `>=4.1.0` | Adaptive salt generation and one-way password hashing |
| **Multi-Part Upload**| Python-multipart | `>=0.0.9` | Streaming multi-part form-data parsing for image uploads |
| **PDF Generation** | ReportLab | `>=5.0.0` | Programmatic canvas drawing for academic PDF transcripts |
| **Task Scheduling** | APScheduler | `>=3.10.0` | In-process cron scheduling for automated midnight risk recomputation |
| **Caching & Queue** | Redis | `>=5.0.0` | Token blacklist storage and fast query cache layer |
| **Distributed Queue**| Celery | `>=5.4.0` | Asynchronous background worker orchestration |
| **WebSockets** | WebSockets | `>=12.0` | Bi-directional streaming for live dashboard updates |
| **Computer Vision** | InsightFace | `>=1.0.0` | Model management for SCRFD detector and ArcFace recognition |
| **Neural Runtime** | ONNX Runtime | `>=1.27.0` | High-efficiency cross-platform execution of serialized ONNX graphs |
| **Image I/O** | OpenCV Python | `>=4.8.0` | Image matrix reading, affine transforms, and Laplacian variance computation |
| **Augmentation** | Albumentations | `>=1.4.0` | Offline data augmentation for personal face classifier training |
| **Deep Learning** | PyTorch | `>=2.0.0` | ResNet-50 personal face classifier architecture and gradient engine |
| **Vision Utilities** | Torchvision | `>=0.15.0` | Pretrained ResNet-50 weights and tensor transforms |
| **Tabular Data** | Pandas | `>=2.0.0` | Dataframe manipulation, CSV exports, and temporal rollups |
| **Vector Math** | NumPy | `>=2.0.0` | Array manipulation, L2 vector normalization, cosine dot-products |
| **Classical ML** | Scikit-learn | `>=1.9.0` | Metrics evaluation, train-test splitting, and baseline logistic regression |
| **Gradient Boosting**| XGBoost | `>=3.0.0` | Multi-class gradient boosted decision tree ensemble |
| **Explainable AI** | SHAP | `>=0.51.0` | TreeExplainer game-theoretic Shapley value decomposition |
| **Frontend Runtime** | React | `^18.3.1` | Declarative component UI engine |
| **DOM Renderer** | React DOM | `^18.3.1` | Web document object model reconciliation |
| **Client Routing** | React Router DOM | `^6.23.1` | Role-guarded single-page application route transitions |
| **Frontend Bundler** | Vite | `^5.4.0` | High-speed frontend development server and Rollup bundler |
| **CSS Framework** | Tailwind CSS | `^4.3.1` | Utility-first CSS engine with dark/light mode tokens |
| **Vite Integration** | @tailwindcss/vite | `^4.3.1` | First-party Vite compiler plugin for Tailwind CSS v4 |
| **UI Verification** | @reticlehq/react | `^2.2.0` | In-app verification harness for UI contract assertions |
