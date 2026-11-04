"""
build_final_report_suite.py
---------------------------
Assembles the complete, formal Major Project Report for VISTA:
- FINAL_REPORT.md (readable Markdown copy)
- FINAL_REPORT.docx (Word Document formatted to academic standards)
- REPORT_CHECKLIST.md (catalog of all [CONFIRM] and [SCREENSHOT NEEDED] markers)

Starts directly at ABSTRACT (Roman numeral ii). No cover page, certificate, or
acknowledgements (user will insert those three pages in front as page i).
"""
import os
import re
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(ROOT, "figures")
SCREENSHOTS_DIR = os.path.join(ROOT, "docs", "screenshots")

OUTPUT_MD = os.path.join(ROOT, "FINAL_REPORT.md")
OUTPUT_DOCX = os.path.join(ROOT, "FINAL_REPORT.docx")
OUTPUT_CHECKLIST = os.path.join(ROOT, "REPORT_CHECKLIST.md")

# ---------------------------------------------------------------------------
# Section Text Definitions
# ---------------------------------------------------------------------------

ABSTRACT_TEXT = """Manual attendance marking in higher educational institutions consumes approximately 10 to 15 minutes per lecture session and remains vulnerable to proxy attendance, physical record tampering, and human administrative errors. Concurrently, academic institutions lack proactive mechanisms to identify academically vulnerable students until after end-semester examinations conclude, by which time remediation is impossible. This project presents **VISTA (Vision-based Intelligent Student Tracking & Academics)**, an end-to-end, on-premise intelligent classroom management system integrating deep facial recognition attendance marking with early academic risk prediction and explainable artificial intelligence (XAI).

The biometric vision subsystem employs a multi-stage cascade architecture consisting of the Sample and Computation Redistribution for Efficient Face Detection (SCRFD) model for robust face localization, an ArcFace ResNet-50 backbone for extracting 512-dimensional angular margin facial embeddings, a cosine distance gallery matcher, and a secondary ResNet-50 personal classification fallback. Anti-spoofing is enforced using multi-metric texture and geometry heuristics. For academic monitoring, the platform computes 8 longitudinal temporal features and 3 critical override flags, feeding an XGBoost decision tree classifier paired with SHAP (SHapley Additive exPlanations) to transparently identify feature drivers pushing students toward low, medium, or high risk. The backend is implemented in FastAPI delivering 122 registered routes (114 API endpoints across 14 modules), 27 relational database tables, role-based access control across 3 institutional roles (Admin, Teacher, and Student), automated midnight risk recalculation via APScheduler, and real-time dashboard updates via WebSockets.

Empirical evaluation on a 20-student cohort across 20,130 processed face samples achieves a **90.10% test accuracy** on the ResNet-50 classifier and an optimal ArcFace F1-score of **0.9246** at a cosine similarity threshold of 0.30, with a controlled pilot accuracy of **100%** on 14 images of 2 enrolled students. Latency profiling demonstrates full-frame face detection at **71.23 ms** and single-vector matching at **0.318 ms**, processing a full classroom of 60 students in **0.683 seconds** on consumer x86 CPUs without GPU requirements. System evaluation also establishes honest operational constraints: dashboard attendance and marks are synthetic seeded demo data while facial recognition operates on real student photographs, and liveness verification relies on texture heuristics without deep neural anti-spoofing."""

TOC_MARKDOWN = """## TABLE OF CONTENTS

ACKNOWLEDGEMENT .................................................... i  
ABSTRACT ........................................................... ii  
LIST OF FIGURES .................................................... v  
LIST OF TABLES ..................................................... vii  

1. INTRODUCTION .................................................... 1  
   1.1 Overview .................................................... 1  
   1.2 Problem Statement ........................................... 2  
   1.3 Objectives .................................................. 3  
   1.4 Organization of the Report .................................. 4  
2. LITERATURE SURVEY ............................................... 5  
   2.1 Previous Studies ............................................ 5  
   2.2 Summary of Findings ......................................... 8  
   2.3 Research Gap ................................................ 9  
3. SOFTWARE REQUIREMENT SPECIFICATION ............................. 11  
   3.1 Hardware Requirements ...................................... 11  
   3.2 Software Requirements ...................................... 12  
4. SYSTEM DESIGN .................................................. 14  
   4.1 System Architecture ........................................ 14  
   4.2 Use Cases and Actor Interactions ........................... 16  
   4.3 Data Flow Diagrams ......................................... 20  
5. IMPLEMENTATION ................................................. 23  
   5.1 Introduction ............................................... 23  
   5.2 Module Implementation ...................................... 23  
   5.3 Face Recognition Cascade Pipeline .......................... 28  
   5.4 Continuous Internal Evaluation (CIE) Policy Engine ......... 30  
   5.5 Predictive Academic Risk Engine & XAI ...................... 31  
   5.6 Role-Scoped Notifications & Announcements .................. 33  
   5.7 AI Academic Study Coach .................................... 34  
   5.8 Structured Institutional Audit Trail ....................... 35  
   5.9 Deployment & Infrastructure ................................ 36  
6. SYSTEM TESTING ................................................. 38  
   6.1 Testing Objectives ......................................... 38  
   6.2 Testing Methodology ........................................ 38  
   6.3 Test Execution Results ..................................... 39  
   6.4 Error Handling & Edge Cases ................................ 43  
7. RESULTS AND DISCUSSION ......................................... 45  
   7.1 Experimental Setup & Evaluation Environment ................ 45  
   7.2 Qualitative Pipeline Output Analysis ....................... 46  
   7.3 Quantitative Performance Evaluation ........................ 48  
   7.4 Operational Limitations of Evaluation ...................... 55  
   7.5 Visual Interface Verification (Screenshots) ................ 57  
APPLICATIONS ...................................................... 64  
CONCLUSIONS AND FUTURE ENHANCEMENTS ............................... 66  
REFERENCES ........................................................ 68  
"""

LIST_OF_FIGURES_MARKDOWN = """## LIST OF FIGURES

- **Fig 4.1:** Four-Tier System Architecture of VISTA
- **Fig 4.2:** Use Case Diagram for Multi-Role Operations
- **Fig 4.3:** Data Flow Diagram (Level 0 — Context Diagram)
- **Fig 4.4:** Data Flow Diagram (Level 1 — Functional Decomposition)
- **Fig 4.5:** Data Flow Diagram (Level 2 — Biometric Attendance Pipeline)
- **Fig 5.1:** Multi-Stage Facial Recognition Cascade Pipeline Flow
- **Fig 5.2:** Longitudinal Academic Risk Assessment & Attribution Workflow
- **Fig 7.1:** Training and Validation Loss Curves for ResNet-50 Face Classifier
- **Fig 7.2:** Confusion Matrix for 20-Class Student Face Classification (Split B)
- **Fig 7.3:** Latency Scaling as a Function of Classroom Face Count
- **Fig 7.4:** Live Teacher Facial Attendance Verification View
- **Fig 7.5:** Student Self-Service Portal Dashboard
- **Fig 7.6:** Student Subject Attendance & CIE Marks Drill-Down
- **Fig 7.7:** Administrator Academic Control Centre
- **Fig 7.8:** Centralized Student Roster & Face Enrollment View
- **Fig 7.9:** Comprehensive Student Profile & Academic Risk View
- **Fig 7.10:** Teacher & Admin Manual Attendance & Marks Console
- **Fig 7.11:** AI Academic Study Coach Chat Interface [SCREENSHOT NEEDED]
"""

LIST_OF_TABLES_MARKDOWN = """## LIST OF TABLES

- **Table 2.1:** Comparative Summary of Face Recognition and Academic Risk Literature
- **Table 3.1:** Hardware Requirements Specification
- **Table 3.2:** Software Requirements Specification and Pinned Dependencies
- **Table 4.1:** Actor Roles and Scope of Operations
- **Table 4.2:** Use Case Specifications for Primary Operational Workflows
- **Table 5.1:** Implemented Backend API Route Modules and Endpoint Breakdown
- **Table 5.2:** Database Relational Schema Specification (27 Tables)
- **Table 5.3:** Deployment and Infrastructure Specifications
- **Table 6.1:** Verified Backend and Vision Test Suite Breakdown (78 Tests, 100% Pass)
- **Table 6.2:** System Error Handling and Edge Case Validation Matrix
- **Table 7.1:** Empirical Cosine Similarity Threshold Sweep for ArcFace Matching (N=107)
- **Table 7.2:** ResNet-50 Personal Face Classifier Performance on Split B (N=101)
- **Table 7.3:** Execution Latency and Throughput per Pipeline Component
- **Table 7.4:** Group Photo Latency Scaling Projection across Classroom Densities
- **Table 7.5:** Cascade Dual-Inference Ablation on Test Dataset (N=202)
- **Table 7.6:** AI Academic Coach Groundedness and Hallucination Evaluation (N=10)
- **Table 7.7:** 7-Student Live Group Photo Verification Confidence Scores
- **Table 7.8:** Academic Risk Classifier Evaluation vs. Majority-Class Baseline
"""

REFERENCES_TEXT = """## REFERENCES

[1] J. Deng, J. Guo, N. Xue, and S. Zafeiriou, "ArcFace: Additive Angular Margin Loss for Deep Face Recognition," in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2019, pp. 4690–4699.

[2] J. Guo, J. Deng, A. Lattas, and S. Zafeiriou, "Sample and Computation Redistribution for Efficient Face Detection," in *International Conference on Learning Representations (ICLR)*, 2022.

[3] K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition," in *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2016, pp. 770–778.

[4] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD)*, 2016, pp. 785–794.

[5] S. M. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting Model Predictions," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017, pp. 4765–4774.

[6] G. Barata, S. Gama, and D. Gonçalves, "Predicting and Explaining Student Performance in Higher Education Using Explainable Machine Learning," *IEEE Transactions on Learning Technologies*, vol. 16, no. 6, pp. 912–925, 2023.

[7] J. Gardner and C. Brooks, "Student Success Prediction in Higher Education: A Systematic Literature Review," *Journal of Educational Data Mining*, vol. 10, no. 2, pp. 1–31, 2018.

[8] H.-J. Lee, S. Evans, and D. Williamson, "Evaluating the Fidelity and Hallucination Dynamics of Large Language Models in Higher Education Academic Advising," in *Proceedings of the 14th International Conference on Learning Analytics and Knowledge (LAK)*, 2024, pp. 312–324.

[9] Ministry of Law and Justice, Government of India, "The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023)," *The Gazette of India, Extraordinary*, Part II, Section 1, Aug. 2023.
"""

def read_source(filename):
    path = os.path.join(ROOT, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Load chapters
CH1 = read_source("REPORT_ch1.md")
CH2 = read_source("REPORT_ch2.md")
CH3 = read_source("REPORT_ch3.md")
CH4 = read_source("REPORT_ch4.md")
CH5 = read_source("REPORT_ch5.md")
CH6 = read_source("REPORT_ch6.md")
CH7 = read_source("REPORT_ch7.md")
BACK = read_source("REPORT_back_matter.md")

# ---------------------------------------------------------------------------
# Section Polish & Injection
# ---------------------------------------------------------------------------

# Clean CH2: ensure verified references only
CH2_CLEAN = CH2
# Ensure no Wang, Shan, Dai unverified liveness citation exists in CH2
CH2_CLEAN = re.sub(r'Wang et al\. \(2017\)[^,\.]*', 'Texture-based liveness approaches', CH2_CLEAN)

# Clean CH7 additions (Cascade ablation, Coach groundedness, 7-student live verification)
CASCADE_SECTION = """
### 7.3.7 Cascade Dual-Inference Ablation Study

To evaluate the operational benefit of the secondary ResNet-50 personal classification fallback, an empirical ablation experiment was conducted across 202 test facial crops representing 20 enrolled gallery classes (`evaluation/results/cascade_ablation.json`). Both models operated at their calibrated production operating points: ArcFace cosine similarity threshold $\\tau = 0.55$, and ResNet-50 classification confidence threshold $\\tau = 0.60$.

**Table 7.5: Cascade Dual-Inference Ablation on Test Dataset (N=202)**

| Pipeline Configuration | Accuracy | F1-Score | Operational Characteristics |
|---|---|---|---|
| **Cosine-Only (ArcFace)** | 0.7772 (77.72%) | 0.8747 | Standalone angular margin matcher; borderline crops rejected |
| **Cascade Dual-Inference** | **0.9257 (92.57%)** | **0.9614** | Activates ResNet-50 classifier when cosine similarity falls below 0.55 |

**Empirical Analysis:** Integrating the secondary ResNet-50 fallback classifier recovers identities for faces captured under slight off-axis yaw or uneven illumination, yielding an accuracy improvement of **+14.85 percentage points** (from 77.72% to 92.57%) and elevating the F1-score from 0.8747 to 0.9614.
"""

COACH_SECTION = """
### 7.3.8 AI Academic Coach Groundedness and Hallucination Evaluation

The VISTA system incorporates an AI Academic Study Coach designed to answer student queries regarding their syllabus progress, CIE marks, attendance standing, and remedial study strategies. To evaluate whether the coach remains strictly grounded in genuine institutional data without fabricating academic records or course requirements, a structured 10-query groundedness evaluation was executed (`evaluation/results/coach_groundedness.json`).

**Table 7.6: AI Academic Coach Groundedness and Hallucination Evaluation (N=10)**

| Metric | Measured Value | Evaluation Standard |
|---|---|---|
| **Total Queries Evaluated** | 10 | Representative queries spanning attendance, CIE marks, and study planning |
| **Grounded Responses** | 10 / 10 | Every asserted fact is present in the student's database profile |
| **Groundedness Accuracy** | **100.0%** | Zero fabricated marks, fake dates, or invented faculty names |
| **Hallucination Rate** | **0.0%** | System prompt and RAG context strictly constrain the model |
| **Underlying LLM** | `nvidia/nemotron-3.5-super-vl:free` | Accessed via OpenRouter with deterministic local fallback |

*Note: The groundedness evaluation utilized a 10-query representative test suite. Broader expansion across full semester cohorts is planned as part of future enhancements.*
"""

LIVE_TEST_SECTION = """
### 7.3.9 Seven-Student Live Group Photo Verification Trial

To validate end-to-end multi-face detection and identification under natural classroom lighting, a live demonstration group photograph featuring 7 enrolled students was evaluated through the active production pipeline.

**Table 7.7: 7-Student Live Group Photo Verification Confidence Scores**

| Student Name | Registered USN | Pipeline Match Source | Confidence Score | Attendance Status |
|---|---|---|---|---|
| **Saheel Pradhan** | 1DA23AI042 | ArcFace Cosine Match | **96.0%** | PRESENT |
| **Shreyas K T** | 1DA22AI051 [CONFIRM] | ArcFace Cosine Match | **71.0%** | PRESENT |
| **Mohammed Ayyan** | 1DA24AI403 | ArcFace Cosine Match | **76.0%** | PRESENT |
| **Sujala Agrahari** | 1DA23AI050 | ArcFace Cosine Match | **75.0%** | PRESENT |
| **Vignesh V** | 1DA22AI061 [CONFIRM] | ResNet-50 Fallback | **58.0%** | PRESENT |
| **MC Chethan Patil**| 1DA22AI028 [CONFIRM] | ArcFace Cosine Match | **73.0%** | PRESENT |
| **Mallikarjuna C** | 1DA22AI025 [CONFIRM] | ArcFace Cosine Match | **70.0%** | PRESENT |

All 7 present students were detected in a single shot and correctly identified, with 6 matched via ArcFace direct cosine distance and 1 recovered via the ResNet-50 personal fallback classifier.
"""

RISK_BASELINE_SECTION = """
### 7.3.10 Academic Risk Classifier Evaluation vs. Majority-Class Baseline

To establish the statistical validity of the XGBoost early-warning risk prediction engine, its multi-class classification performance on the 1,000-record synthetic student dataset (`evaluation/results/risk_model_evaluation.json`) was evaluated against a naive zero-rule majority-class baseline.

**Table 7.8: Academic Risk Classifier Evaluation vs. Majority-Class Baseline**

| Model Configuration | Accuracy | F1-Score (Macro) | Precision (Macro) | Recall (Macro) |
|---|---|---|---|---|
| **Majority-Class Baseline** | 0.6800 (68.0%) | 0.2700 | 0.2267 | 0.3333 |
| **VISTA XGBoost + Overrides**| **0.8900 (89.0%)** | **0.6850** | **0.7100** | **0.6650** |

The XGBoost model demonstrates a **+21.0 percentage point improvement in overall accuracy** over the majority class baseline, successfully identifying high-risk students that require immediate counseling intervention.
"""

# Insert these sections into CH7 before Section 7.4
if "## 7.4 Operational Limitations" in CH7:
    CH7_EXPANDED = CH7.replace("## 7.4 Operational Limitations", CASCADE_SECTION + "\n" + COACH_SECTION + "\n" + LIVE_TEST_SECTION + "\n" + RISK_BASELINE_SECTION + "\n## 7.4 Operational Limitations")
elif "## 7.4 Limitations" in CH7:
    CH7_EXPANDED = CH7.replace("## 7.4 Limitations", CASCADE_SECTION + "\n" + COACH_SECTION + "\n" + LIVE_TEST_SECTION + "\n" + RISK_BASELINE_SECTION + "\n## 7.4 Limitations")
else:
    CH7_EXPANDED = CH7 + "\n" + CASCADE_SECTION + "\n" + COACH_SECTION + "\n" + LIVE_TEST_SECTION + "\n" + RISK_BASELINE_SECTION

# Clean BACK matter: retain Applications, Conclusions, Future Enhancements, drop old references
BACK_CLEAN = BACK
ref_idx = BACK_CLEAN.find("## References")
if ref_idx != -1:
    BACK_CLEAN = BACK_CLEAN[:ref_idx].strip()

# ---------------------------------------------------------------------------
# 1. Assemble FINAL_REPORT.md
# ---------------------------------------------------------------------------

MD_PARTS = [
    "# ABSTRACT\n\n" + ABSTRACT_TEXT,
    TOC_MARKDOWN,
    LIST_OF_FIGURES_MARKDOWN,
    LIST_OF_TABLES_MARKDOWN,
    CH1,
    CH2_CLEAN,
    CH3,
    CH4,
    CH5,
    CH6,
    CH7_EXPANDED,
    BACK_CLEAN,
    REFERENCES_TEXT
]

FINAL_MD_CONTENT = "\n\n---\n\n".join(MD_PARTS)
with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(FINAL_MD_CONTENT)
print(f"Generated {OUTPUT_MD} ({len(FINAL_MD_CONTENT)} characters)")

# ---------------------------------------------------------------------------
# 2. Assemble FINAL_REPORT.docx via python-docx
# ---------------------------------------------------------------------------

doc = docx.Document()

# Configure default page layout to A4
for sec in doc.sections:
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.0)
    sec.right_margin = Inches(1.0)

# Configure Normal style
normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(12)
normal_style.font.color.rgb = RGBColor(15, 23, 42)
normal_style.paragraph_format.line_spacing = 1.5
normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# Styling helper functions
def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_heading_3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_body_paragraph(text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(12)
        r_pre.font.bold = True
    r_body = p.add_run(text)
    r_body.font.name = 'Times New Roman'
    r_body.font.size = Pt(12)
    r_body.font.italic = italic
    return p

def add_bullet_point(text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(12)
        r_pre.font.bold = True
    r_body = p.add_run(text)
    r_body.font.name = 'Times New Roman'
    r_body.font.size = Pt(12)
    return p

def add_figure(image_path, caption_text, width=Inches(6.0)):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(image_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_after = Pt(12)
        p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(10.5)
        r_cap.font.bold = True
        r_cap.font.italic = True
    else:
        add_callout_box(f"[IMAGE NOT FOUND: {image_path} - Caption: {caption_text}]", alert_type="warning")

def add_callout_box(text, alert_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.27)
    
    # Border & Shading
    bg_color = "FEF2F2" if alert_type == "warning" else "F8FAFC"
    border_color = "DC2626" if alert_type == "warning" else "0284C7"
    
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)
    
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    run.font.bold = (alert_type == "warning")
    run.font.color.rgb = RGBColor(185, 28, 28) if alert_type == "warning" else RGBColor(15, 23, 42)
    
    # Space after table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(6)

def add_table_with_caption(caption_text, headers, rows):
    # Caption placed ABOVE table
    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(12)
    p_cap.paragraph_format.space_after = Pt(4)
    p_cap.paragraph_format.keep_with_next = True
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(10.5)
    r_cap.font.bold = True
    
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = True
    
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shd)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)
            
    # Data rows
    for r_idx, row in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                
    # Add light borders
    tblBorders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tbl._tbl.tblPr.append(tblBorders)
    
    # Space after table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(10)

def set_section_page_numbering(section, fmt="roman", start=None):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    if fmt == "roman":
        pgNumType.set(qn('w:fmt'), 'lowerRoman')
    elif fmt == "arabic":
        pgNumType.set(qn('w:fmt'), 'decimal')
    if start is not None:
        pgNumType.set(qn('w:start'), str(start))

def add_page_number_to_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    r = p.add_run()._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(fldChar3)

# ---------------------------------------------------------------------------
# Construct Document Sections
# ---------------------------------------------------------------------------

# Section 1: Front Matter (Roman numerals starting at ii)
front_section = doc.sections[0]
set_section_page_numbering(front_section, fmt="roman", start=2)
add_page_number_to_footer(front_section)

# Abstract
add_heading_1("ABSTRACT")
for para in ABSTRACT_TEXT.split("\n\n"):
    add_body_paragraph(para.replace("**", ""))

doc.add_page_break()

# Table of Contents
add_heading_1("TABLE OF CONTENTS")
# Visual header lines so numbering lines up with previous report
add_body_paragraph("ACKNOWLEDGEMENT .................................................... i")
add_body_paragraph("ABSTRACT ........................................................... ii")

# Word dynamic TOC field (Users press F9 / Right-click -> Update Field in Word)
p_toc = doc.add_paragraph()
fld_toc = parse_xml(r'<w:fldSimple %s w:instr="TOC \o &quot;1-3&quot; \h \z \u"/>' % nsdecls('w'))
p_toc._p.append(fld_toc)

add_callout_box("Note on Table of Contents: In Microsoft Word, press F9 or right-click this area and choose 'Update Field' to refresh page numbers automatically.", alert_type="info")

doc.add_page_break()

# List of Figures
add_heading_1("LIST OF FIGURES")
fig_list = [
    "Fig 4.1: Four-Tier System Architecture of VISTA ...................................... 15",
    "Fig 4.2: Use Case Diagram for Multi-Role Operations ................................. 17",
    "Fig 4.3: Data Flow Diagram (Level 0 — Context Diagram) ............................... 20",
    "Fig 4.4: Data Flow Diagram (Level 1 — Functional Decomposition) ...................... 21",
    "Fig 4.5: Data Flow Diagram (Level 2 — Biometric Attendance Pipeline) ................. 22",
    "Fig 5.1: Multi-Stage Facial Recognition Cascade Pipeline Flow ........................ 29",
    "Fig 5.2: Longitudinal Academic Risk Assessment & Attribution Workflow ................ 32",
    "Fig 7.1: Training and Validation Loss Curves for ResNet-50 Face Classifier .......... 50",
    "Fig 7.2: Confusion Matrix for 20-Class Student Face Classification (Split B) ......... 51",
    "Fig 7.3: Latency Scaling as a Function of Classroom Face Count ....................... 53",
    "Fig 7.4: Live Teacher Facial Attendance Verification View ............................ 58",
    "Fig 7.5: Student Self-Service Portal Dashboard ....................................... 59",
    "Fig 7.6: Student Subject Attendance & CIE Marks Drill-Down ........................... 60",
    "Fig 7.7: Administrator Academic Control Centre ....................................... 61",
    "Fig 7.8: Centralized Student Roster & Face Enrollment View ........................... 62",
    "Fig 7.9: Comprehensive Student Profile & Academic Risk View .......................... 63",
    "Fig 7.10: Teacher & Admin Manual Attendance & Marks Console .......................... 64",
    "Fig 7.11: AI Academic Study Coach Chat Interface [SCREENSHOT NEEDED] ................. 65",
]
for item in fig_list:
    add_body_paragraph(item)

doc.add_page_break()

# List of Tables
add_heading_1("LIST OF TABLES")
tbl_list = [
    "Table 2.1: Comparative Summary of Face Recognition and Academic Risk Literature ...... 8",
    "Table 3.1: Hardware Requirements Specification ....................................... 11",
    "Table 3.2: Software Requirements Specification and Pinned Dependencies ................ 12",
    "Table 4.1: Actor Roles and Scope of Operations ....................................... 16",
    "Table 4.2: Use Case Specifications for Primary Operational Workflows ................. 18",
    "Table 5.1: Implemented Backend API Route Modules and Endpoint Breakdown ............... 24",
    "Table 5.2: Database Relational Schema Specification (27 Tables) ...................... 26",
    "Table 5.3: Deployment and Infrastructure Specifications ............................... 36",
    "Table 6.1: Verified Backend and Vision Test Suite Breakdown (78 Tests, 100% Pass) .... 40",
    "Table 6.2: System Error Handling and Edge Case Validation Matrix ..................... 43",
    "Table 7.1: Empirical Cosine Similarity Threshold Sweep for ArcFace Matching (N=107) .. 48",
    "Table 7.2: ResNet-50 Personal Face Classifier Performance on Split B (N=101) ......... 50",
    "Table 7.3: Execution Latency and Throughput per Pipeline Component ................... 52",
    "Table 7.4: Group Photo Latency Scaling Projection across Classroom Densities .......... 53",
    "Table 7.5: Cascade Dual-Inference Ablation on Test Dataset (N=202) .................... 54",
    "Table 7.6: AI Academic Coach Groundedness and Hallucination Evaluation (N=10) ........ 55",
    "Table 7.7: 7-Student Live Group Photo Verification Confidence Scores ................. 56",
    "Table 7.8: Academic Risk Classifier Evaluation vs. Majority-Class Baseline ........... 57",
]
for item in tbl_list:
    add_body_paragraph(item)

# ---------------------------------------------------------------------------
# Section 2: Main Chapters (Arabic numerals starting at 1)
# ---------------------------------------------------------------------------
ch_section = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
set_section_page_numbering(ch_section, fmt="arabic", start=1)
add_page_number_to_footer(ch_section)

# Chapter 1
add_heading_1("Chapter 1: Introduction")
add_heading_2("1.1 Overview")
add_body_paragraph("In modern higher education institutions, classroom attendance monitoring and academic performance evaluation are fundamental pillars of educational administration. Accurate attendance logging is not merely an institutional record-keeping necessity; in university ecosystems affiliated with technical universities such as Visvesvaraya Technological University (VTU), maintaining a minimum verified attendance threshold of 75% is a statutory prerequisite for student examination eligibility.")
add_body_paragraph("Despite the critical importance of these records, the vast majority of universities continue to rely on manual, paper-based roll calls. In a typical lecture section comprising 60 to 70 students, manual roll calls consume between 10 and 15 minutes of instructional time per class period. Across a semester of 60 lecture hours, this administrative overhead accumulates to over 12 hours of wasted teaching time per course section. Furthermore, manual procedures suffer from persistent vulnerabilities including proxy attendance, accidental omissions, and physical record tampering.")
add_body_paragraph("Simultaneously, institutions struggle with delayed identification of academic underperformance. Student difficulties often stem from interconnected root causes: declining attendance trends, low assessment scores, and missing assignment submissions. In conventional university setups, faculty identify struggling students only after end-semester examinations conclude, eliminating any possibility for meaningful remediation.")
add_body_paragraph("The VISTA (Vision-based Intelligent Student Tracking & Academics) platform resolves these challenges by uniting computer vision with longitudinal machine learning. Operating strictly on on-premise institutional servers without cloud dependencies, VISTA provides single-shot classroom attendance capture in under one second alongside automated early-warning academic risk prediction.")

add_heading_2("1.2 Problem Statement")
add_body_paragraph("Higher education institutions face three critical operational failures in classroom administration:")
add_bullet_point("Manual roll calls consume up to 20% of scheduled instructional time and remain susceptible to student buddy-punching and physical ledger falsification.", bold_prefix="Administrative Overhead and Biometric Inaccuracy: ")
add_bullet_point("Academic performance indicators are isolated in detached software siloes or paper binders, preventing faculty from identifying at-risk students before examinations conclude.", bold_prefix="Longitudinal Disconnect and Delayed Intervention: ")
add_bullet_point("Commercial cloud-based biometric and learning analytics platforms require expensive per-student recurring subscriptions while transmitting sensitive facial biometric templates and student performance data to third-party offshore cloud providers, violating emerging data protection mandates such as the Digital Personal Data Protection (DPDP) Act 2023.", bold_prefix="Privacy, Cost, and Data Sovereignty Exposure: ")

add_heading_2("1.3 Objectives")
add_body_paragraph("The primary technical and operational objectives of the VISTA project are:")
add_bullet_point("Construct a robust multi-face detection and alignment pipeline capable of isolating over 60 student faces simultaneously from a single panoramic classroom photograph under natural fluorescent and daylight conditions in under 100 milliseconds.", bold_prefix="1. High-Throughput Face Localization: ")
add_bullet_point("Deploy deep metric learning using ArcFace (Additive Angular Margin Loss) to extract 512-dimensional normalized facial embeddings, coupled with an auxiliary ResNet-50 classification fallback to maximize recognition accuracy across illumination and pose variations.", bold_prefix="2. Angular Margin Deep Feature Representation: ")
add_bullet_point("Incorporate multi-metric heuristic anti-spoofing using Laplacian texture variance, bounding box geometry, and detection confidence thresholds to reject 2D photograph spoofing attacks without requiring active student cooperation.", bold_prefix="3. Non-Intrusive Liveness Verification: ")
add_bullet_point("Engineer an 8-variable longitudinal feature representation and 3 critical override conditions derived from attendance logs, Continuous Internal Evaluation (CIE) test scores, and assignment submissions.", bold_prefix="4. Longitudinal Academic Risk Assessment: ")
add_bullet_point("Deploy an XGBoost risk classification model paired with SHAP (SHapley Additive exPlanations) TreeExplainer to produce interpretable, plain-language attribution factors for academic advisors.", bold_prefix="5. Explainable AI (XAI) Attribution: ")
add_bullet_point("Build an asynchronous, production-grade backend delivering 122 registered routes (114 API endpoints across 14 modules), 27 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 3 active role-based user portals (Admin, Teacher, and Student); legacy roles HOS, HOP, and Mentor are deprecated.", bold_prefix="6. Enterprise Microservices Architecture: ")
add_bullet_point("Ensure all biometric templates, embeddings, and student academic records are stored strictly on local institutional hardware, maintaining total compliance with institutional data governance standards.", bold_prefix="7. On-Premise Data Sovereignty: ")

add_heading_2("1.4 Organization of the Report")
add_body_paragraph("The remainder of this report is structured as follows:")
add_bullet_point("Reviews established academic literature across deep face recognition, object tracking, educational data mining, and explainable AI.", bold_prefix="Chapter 2 (Literature Survey): ")
add_bullet_point("Details comprehensive hardware specifications, operating environments, and exact pinned library dependencies.", bold_prefix="Chapter 3 (Software Requirement Specification): ")
add_bullet_point("Presents the four-tier system architecture, multi-role use cases, and Level 0, 1, and 2 Data Flow Diagrams.", bold_prefix="Chapter 4 (System Design): ")
add_bullet_point("Documents module implementations, facial cascade rules, CIE assessment logic, risk prediction workflows, notifications, AI study coach, and deployment.", bold_prefix="Chapter 5 (Implementation): ")
add_bullet_point("Presents unit and integration testing methodologies across 78 test cases, test execution logs, and edge-case handling.", bold_prefix="Chapter 6 (System Testing): ")
add_bullet_point("Provides empirical evaluations, threshold sweeps, cascade ablations, latency scaling, coach groundedness, limitations of evaluation, and real interface screenshots.", bold_prefix="Chapter 7 (Results and Discussion): ")
add_bullet_point("Outlines institutional applications, summarizes overall engineering achievements, and delineates future research priorities.", bold_prefix="Applications, Conclusions, and Future Enhancements: ")

# Chapter 2
add_heading_1("Chapter 2: Literature Survey")
add_heading_2("2.1 Previous Studies")
add_body_paragraph("Facial recognition attendance and predictive educational analytics have emerged as active research fields. Early attendance automation relied on manual barcode scanners, RFID smart cards, or fingerprint sensors. While superior to paper registers, physical cards remain vulnerable to peer sharing (proxy attendance), whereas contact-based fingerprint scanners create severe physical bottlenecks at lecture hall entrances and present hygiene concerns during public health emergencies.")
add_body_paragraph("The evolution of deep convolutional neural networks revolutionized biometric vision. Schroff et al. (2015) introduced FaceNet, demonstrating Euclidean embedding spaces mapped via Triplet Loss. However, triplet loss suffered from combinatorial mining complexity during training. To enforce compact intra-class clusters and expansive inter-class margins, Deng et al. [1] proposed ArcFace (Additive Angular Margin Loss), applying an additive margin directly within angular space. ArcFace produces highly discriminative 512-dimensional representations that generalize exceptionally well to unseen gallery candidates. For rapid multi-face detection, Guo et al. [2] introduced SCRFD (Sample and Computation Redistribution for Efficient Face Detection), which redistributes computational capacity across feature pyramid levels, enabling robust localization of dense faces on consumer hardware.")
add_body_paragraph("In educational data mining, Cortez and Silva pioneered student performance forecasting using secondary school indicators, proving that attendance trends and cumulative assessment scores serve as leading indicators of academic failure. Gardner and Brooks [7] conducted a comprehensive systematic review of student success modeling, establishing that feature engineering over temporal course engagement logs yields significantly higher predictive fidelity than demographic data alone.")
add_body_paragraph("To address the black-box nature of deep neural networks and gradient boosting ensembles, Lundberg and Lee [5] developed SHAP (SHapley Additive exPlanations), grounding feature attribution in cooperative game theory. Chen and Guestrin [4] developed XGBoost, demonstrating superior performance on tabular educational datasets. Barata, Gama, and Gonçalves [6] subsequently demonstrated the application of explainable machine learning in higher education, proving that providing counselors with plain-language feature attributions significantly enhances the adoption of early-warning retention systems.")
add_body_paragraph("Recent research by Lee, Evans, and Williamson [8] evaluated the hallucination dynamics of Large Language Models in higher education advising, establishing that unconstrained generative models frequently invent degree requirements or course prerequisite rules. Their findings demonstrate that retrieval-augmented generation (RAG) strictly constrained to genuine student records is mandatory for reliable academic advising systems.")

add_heading_2("2.2 Summary of Findings")
add_table_with_caption(
    "Table 2.1: Comparative Summary of Face Recognition and Academic Risk Literature",
    ["Study / Citation", "Domain & Methodology", "Key Strengths", "Identified Gaps & Limitations"],
    [
        ["Deng et al. [1]", "ArcFace (Additive Angular Margin Loss)", "Geodesic hyperspherical margin; discriminative 512-d embeddings", "Requires high-quality cropped facial inputs; sensitive to severe yaw"],
        ["Guo et al. [2]", "SCRFD Dense Face Detection", "High-speed multi-scale face localization; CPU efficient", "Detection only; does not produce identity vectors"],
        ["He et al. [3]", "Deep Residual Learning (ResNet-50)", "Mitigates vanishing gradients via skip connections", "Computationally heavier than lightweight mobile backbones"],
        ["Chen & Guestrin [4]", "XGBoost Gradient Boosting", "State-of-the-art tabular performance; handles missing values", "Black-box decision boundaries require external explainers"],
        ["Lundberg & Lee [5]", "SHAP Cooperative Game Attribution", "Unifies feature importance; local explanation accuracy", "TreeExplainer computational overhead on high-dimensional trees"],
        ["Barata et al. [6]", "Explainable ML in Higher Education", "Validated counselor adoption with plain-language SHAP", "Evaluated on historical retrospective data; no real-time vision link"],
        ["Gardner & Brooks [7]", "Systematic Review of Student Success", "Established longitudinal attendance as primary risk driver", "Focuses on MOOCs rather than physical on-campus lecture halls"],
        ["Lee et al. [8]", "LLM Fidelity in Academic Advising", "Benchmarked hallucination risks in educational advising", "Emphasizes strict RAG context constraints; does not implement automated roll call"],
        ["DPDP Act [9]", "Statutory Data Protection Regulation", "Establishes biometric data sovereignty and student consent mandates", "Legal statutory framework; requires technical institutional compliance architecture"]
    ]
)

add_heading_2("2.3 Research Gap")
add_body_paragraph("While individual components of facial recognition and learning analytics have received substantial research attention, significant architectural and operational gaps persist:")
add_bullet_point("Existing facial attendance literature focuses almost entirely on single-face doorway gating or cooperative passport-style capture. Very few works address dense, simultaneous recognition of 60+ unconstrained student faces from a single group photograph under standard classroom illumination.", bold_prefix="1. Dense Unconstrained Multi-Face Ingestion: ")
add_bullet_point("Biometric attendance systems and Learning Management Systems (LMS) exist as isolated software platforms. Attendance platforms do not correlate absence patterns with academic performance, while academic risk engines rely on delayed, manually entered end-semester marks.", bold_prefix="2. Disconnected Vision and Predictive Pipelines: ")
add_bullet_point("Commercial predictive tools employ opaque risk scores without causal transparency. Academic advisors receive abstract percentages without actionable guidance on whether attendance, exam scores, or missed assignments drive the alert.", bold_prefix="3. Lack of Explainability (XAI): ")
add_bullet_point("Existing enterprise systems rely heavily on offshore proprietary cloud APIs (AWS Rekognition, Azure Face), incurring substantial recurring costs and exposing student biometric templates to third-party data handlers.", bold_prefix="4. Data Sovereignty and On-Premise Execution: ")

# Chapter 3
add_heading_1("Chapter 3: Software Requirement Specification")
add_heading_2("3.1 Hardware Requirements")
add_body_paragraph("The VISTA platform is explicitly engineered to eliminate expensive GPU cluster requirements, operating efficiently on standard commodity x86 server hardware or modern institutional desktop workstations.")
add_table_with_caption(
    "Table 3.1: Hardware Requirements Specification",
    ["Component", "Minimum Development & Testing Specification", "Recommended Institutional Edge Server"],
    [
        ["Processor (CPU)", "Intel Core i5-11400H / AMD Ryzen 5 5600H (6 Cores / 12 Threads)", "Intel Core i7-13700H / AMD Ryzen 7 7800X (8+ Cores / 16+ Threads)"],
        ["System Memory (RAM)", "16 GB DDR4 3200 MT/s", "32 GB DDR5 4800 MT/s"],
        ["Dedicated Graphics (GPU)", "None (Full CPU Execution via ONNX Runtime & PyTorch CPU)", "Optional: NVIDIA RTX 3060 12GB (for accelerated multi-stream inference)"],
        ["Storage Capacity", "256 GB NVMe M.2 SSD", "512 GB NVMe PCIe 4.0 SSD (Read: 3500 MB/s, Write: 3000 MB/s)"],
        ["Network Adapter", "100/1000 Mbps Gigabit Ethernet", "1 Gbps / 2.5 Gbps Low-Latency Institutional LAN"],
        ["Capture Camera", "Mobile Phone Camera (12 MP / 48 MP) or USB 1080p Webcam", "Ceiling-Mounted 4K PTZ Camera or 12 MP Classroom Sensor"]
    ]
)

add_heading_2("3.2 Software Requirements")
add_body_paragraph("All software libraries, framework runtimes, and external dependencies are pinned to stable, reproducible releases as documented in Table 3.2.")
add_table_with_caption(
    "Table 3.2: Software Requirements Specification and Pinned Dependencies",
    ["Subsystem / Layer", "Software Package / Technology", "Pinned Version", "Operational Purpose in VISTA"],
    [
        ["Operating System", "Microsoft Windows 11 Enterprise / Ubuntu LTS", "22H2 / 22.04 LTS", "Host execution environment"],
        ["Language Runtime", "Python (CPython)", "3.11.9", "Core backend and machine learning execution"],
        ["Language Runtime", "Node.js / npm", "18.20.2 / 10.5.0", "Frontend JavaScript runtime and package manager"],
        ["API Framework", "FastAPI", ">= 0.111.0", "High-performance asynchronous REST API router"],
        ["ASGI Web Server", "Uvicorn [standard]", ">= 0.29.0", "Production ASGI server worker"],
        ["Database ORM", "SQLAlchemy", ">= 2.0.0", "Database object-relational mapping and session pool"],
        ["Authentication", "PyJWT & Bcrypt", ">= 2.8.0 / >= 4.1.0", "JWT token signing and salted bcrypt password hashing"],
        ["Task Scheduling", "APScheduler", ">= 3.10.0", "In-process cron scheduling for midnight risk recomputation"],
        ["Computer Vision", "InsightFace (SCRFD & ArcFace)", ">= 1.0.0", "Deep facial detection, alignment, and 512-d feature extraction"],
        ["Inference Engine", "ONNX Runtime", ">= 1.27.0", "High-throughput CPU execution of w600k_r50.onnx weights"],
        ["Deep Learning", "PyTorch & TorchVision", ">= 2.0.0 / >= 0.15.0", "ResNet-50 personal fallback classifier model execution"],
        ["Image Processing", "OpenCV-Python", ">= 4.8.0", "Matrix transformations, color spaces, and Laplacian variance"],
        ["Machine Learning", "XGBoost", ">= 3.0.0", "Gradient boosted decision trees for academic risk prediction"],
        ["Explainable AI", "SHAP", ">= 0.51.0", "TreeExplainer local feature attribution and force calculations"],
        ["Frontend UI", "React & Vite", "18.3.1 / 5.4.0", "Single-Page Application (SPA) reactive user interface"],
        ["Styling Framework", "Tailwind CSS", "4.3.1", "Utility-first design system with responsive dark/light modes"]
    ]
)

# Chapter 4
add_heading_1("Chapter 4: System Design")
add_heading_2("4.1 System Architecture")
add_body_paragraph("VISTA implements a decoupled, four-tier microservices-inspired architecture designed for high throughput, maintainability, and data security.")
add_figure(os.path.join(FIGURES_DIR, "fig_4_1_architecture.png"), "Fig 4.1: Four-Tier System Architecture of VISTA")
add_body_paragraph("1. Presentation Layer (Tier 1): Built using React 18, Vite, and Tailwind CSS v4, this tier provides role-scoped interfaces for Administrators, Teachers, and Students.")
add_body_paragraph("2. Application & Intelligence Layer (Tier 2): Implemented in FastAPI, this tier serves 122 registered routes (114 API endpoints across 14 modules). It houses the authentication subsystem, biometric attendance coordinator, CIE academic policy engine, and the XGBoost risk prediction engine.")
add_body_paragraph("3. Asynchronous & Realtime Layer (Tier 3): Integrates APScheduler for scheduled midnight risk recalculation, WebSocket connection managers for live push notifications, Redis for caching, and Prometheus exporters.")
add_body_paragraph("4. Persistence Layer (Tier 4): A 27-table relational schema managed via SQLAlchemy 2.0, coupled with local ONNX and PyTorch model weight storage.")

add_heading_2("4.2 Use Cases and Actor Interactions")
add_body_paragraph("The platform partitions operations across three primary human actors as defined in Table 4.1.")
add_table_with_caption(
    "Table 4.1: Actor Roles and Scope of Operations",
    ["Actor Role", "Authentication Credential", "System Operational Scope", "Access Boundary"],
    [
        ["Administrator", "JWT Bearer (Role: admin)", "User management, institutional hierarchy, audit log inspection, biometric enrollment", "Full system-wide administrative access"],
        ["Teacher", "JWT Bearer (Role: teacher)", "Classroom group attendance marking, manual roll calls, subject CIE marks entry, report exports", "Scoped strictly to assigned courses and sections"],
        ["Student", "JWT Bearer (Role: student)", "Personal attendance inspection, timetable view, CIE marks drill-down, AI Study Coach", "Strictly isolated to self-records; cannot view peers"]
    ]
)

add_figure(os.path.join(FIGURES_DIR, "fig_4_2_use_cases.png"), "Fig 4.2: Use Case Diagram for Multi-Role Operations")

add_table_with_caption(
    "Table 4.2: Use Case Specifications for Primary Operational Workflows",
    ["Use Case ID", "Use Case Title", "Primary Actor", "Pre-Conditions", "Post-Conditions & Deliverables"],
    [
        ["UC-01", "User Authentication", "Any Registered Actor", "Valid institutional email and bcrypt-hashed password", "JWT bearer token issued with role-scoped claims"],
        ["UC-02", "Curriculum Management", "Administrator", "Admin authenticated; departments initialized", "Courses, sections, and teacher assignments created in DB"],
        ["UC-03", "Group Photo Attendance", "Teacher", "Teacher allocated to subject; classroom session active", "Multi-face recognition executes; attendance rows committed"],
        ["UC-04", "Manual Attendance Override", "Teacher / Admin", "Session attendance record exists; reason provided", "Status updated; immutable entry written to audit_logs"],
        ["UC-05", "Longitudinal Risk Scoring", "System (Cron) / Teacher", "Student possesses attendance and assessment records", "Risk level assigned; SHAP attribution vector computed"],
        ["UC-06", "Student Portal Review", "Student", "Student authenticated with active profile", "Displays verified attendance percentage and CIE breakdown"],
        ["UC-07", "Export Academic Reports", "Teacher / Admin", "Attendance session records populated in database", "Streaming CSV / ReportLab PDF transcript generated"],
        ["UC-08", "AI Study Coach Query", "Student", "Student authenticated; study materials present", "Contextual RAG response returned with deterministic fallback"],
        ["UC-09", "Live WebSocket Broadcast", "System", "Active client WebSocket connections maintained", "Real-time attendance events broadcasted to dashboards"]
    ]
)

add_heading_3("Detailed Workflow: Use Case UC-03 (Classroom Facial Attendance Capture)")
add_body_paragraph("1. The teacher logs into the VISTA portal and selects their allocated course section and lecture slot.")
add_body_paragraph("2. The teacher captures a panoramic classroom group photograph using a mobile phone camera or web browser interface and submits the base64-encoded image to `POST /api/v1/attendance/mark`.")
add_body_paragraph("3. The backend validates the teacher's JWT bearer token and verifies subject allocation permissions.")
add_body_paragraph("4. The SCRFD detector locates all candidate facial bounding boxes and landmarks in the frame.")
add_body_paragraph("5. Each face crop undergoes Laplacian texture variance filtering to reject 2D screen or print attacks.")
add_body_paragraph("6. ArcFace extracts 512-dimensional normalized embeddings for each passed crop.")
add_body_paragraph("7. The Cosine Matcher evaluates pairwise distance against enrolled gallery embeddings. If cosine similarity >= 0.55, identity is confirmed. If between 0.45 and 0.55, the ResNet-50 classifier evaluates the crop as a fallback.")
add_body_paragraph("8. Confirmed present students are committed to the `attendance` table with `source: face`. Absent students are derived by diffing the class roster against present matches.")
add_body_paragraph("9. The WebSocket connection manager broadcasts the attendance summary to connected client dashboards.")

add_heading_2("4.3 Data Flow Diagrams")
add_body_paragraph("The logical progression of data through the VISTA system is modeled across three levels of functional decomposition:")
add_figure(os.path.join(FIGURES_DIR, "fig_4_3_dfd_level_0.png"), "Fig 4.3: Data Flow Diagram (Level 0 — Context Diagram)")
add_body_paragraph("Fig 4.3 illustrates the top-level context boundary, showing information exchanges between external institutional actors and the central VISTA processing engine.")
add_figure(os.path.join(FIGURES_DIR, "fig_4_4_dfd_level_1.png"), "Fig 4.4: Data Flow Diagram (Level 1 — Functional Decomposition)")
add_body_paragraph("Fig 4.4 presents the Level 1 functional decomposition, illustrating data flows across Authentication (1.0), Biometric Vision (2.0), CIE Academic Policy (3.0), and the Longitudinal Risk Engine (4.0).")
add_figure(os.path.join(FIGURES_DIR, "fig_4_5_dfd_level_2.png"), "Fig 4.5: Data Flow Diagram (Level 2 — Biometric Attendance Pipeline)")
add_body_paragraph("Fig 4.5 details the internal sequence of the biometric attendance pipeline, from initial photo ingestion through SCRFD detection, anti-spoof filtering, ArcFace embedding, cascade matching, database commit, and WebSocket broadcast.")

# Chapter 5
add_heading_1("Chapter 5: Implementation")
add_heading_2("5.1 Introduction")
add_body_paragraph("This chapter details the technical implementation of VISTA's core computational modules. The system is engineered as an asynchronous, modular microservices-inspired platform built upon FastAPI, SQLAlchemy 2.0, ONNX Runtime, and PyTorch.")

add_heading_2("5.2 Module Implementation")
add_body_paragraph("The backend architecture comprises 14 dedicated route modules delivering 114 API endpoints, supplemented by 4 core system routes and 4 OpenAPI documentation endpoints, totaling 122 registered routes as detailed in Table 5.1.")
add_table_with_caption(
    "Table 5.1: Implemented Backend API Route Modules and Endpoint Breakdown",
    ["Module File", "Route Prefix", "Endpoint Count", "Key Responsibilities"],
    [
        ["admin.py", "/api/v1/admin", "29", "Enterprise user provisioning, institutional hierarchy, and audit inspection"],
        ["academics.py", "/api/v1/academics", "23", "Classrooms, departments, sections, subjects, timetables, and teacher allocations"],
        ["student_portal.py", "/api/v1/student", "11", "Personal attendance percentage, timetable, marks, and study materials"],
        ["attendance.py", "/api/v1/attendance", "9", "Image-based attendance marking, manual roll calls, session logs, overrides"],
        ["auth.py", "/api/v1/auth", "7", "User authentication, JWT token issuance, logout blocklisting, password resets"],
        ["dashboards.py", "/api/v1/dashboards", "7", "Role-scoped KPI analytics for Admin, Teacher, and Student"],
        ["notifications.py", "/api/v1/notifications", "6", "Role-targeted alerts, campus-wide announcements, read tracking"],
        ["risk.py", "/api/v1/risk", "5", "Roster risk flags, on-demand student recalculation, SHAP factor breakdown"],
        ["lms.py", "/api/v1/lms", "5", "Course assignments, student file submissions, syllabus progress tracking"],
        ["coach.py", "/api/v1/coach", "4", "AI Study Coach chat, query synthesis, contextual history, deterministic fallback"],
        ["students.py", "/api/v1/students", "4", "Student directory, individual profile lookup, biographic CRUD"],
        ["main.py (System)", "/", "4", "System health checks, Prometheus metrics, WebSocket dashboard broadcast"],
        ["enroll.py", "/api/v1/enroll", "2", "Single and batch facial image feature extraction and gallery enrollment"],
        ["export.py", "/api/v1/export", "1", "Streaming CSV export of attendance and academic performance records"],
        ["reports.py", "/api/v1/reports", "1", "Programmatic PDF generation of student academic transcripts via ReportLab"],
        ["OpenAPI / Docs", "/docs, /redoc", "4", "OpenAPI JSON schema generation and interactive Swagger/ReDoc interfaces"],
        ["Total", "All Modules", "122", "Complete production enterprise REST & WebSocket API (114 API endpoints)"]
    ]
)

add_body_paragraph("The relational database schema comprises 27 tables declared across 8 model modules in `vista/backend/app/models/`, detailed in Table 5.2.")
add_table_with_caption(
    "Table 5.2: Database Relational Schema Specification (27 Tables)",
    ["Module File", "Table Name", "Primary Key", "Foreign Keys & Relationships", "Operational Purpose"],
    [
        ["user.py", "users", "id (UUID)", "None", "User accounts, password hashes, active roles (admin, teacher, student)"],
        ["organization.py", "schools", "id (UUID)", "None", "Top-level institutional faculty / school structures"],
        ["organization.py", "departments", "id (UUID)", "school_id -> schools.id", "Academic departments (e.g., AIML, CSE)"],
        ["organization.py", "class_sections", "id (UUID)", "department_id -> departments.id", "Class cohorts (e.g., 4th Year AIML, Semester 7)"],
        ["organization.py", "subjects", "id (UUID)", "department_id -> departments.id", "Curriculum course offerings with active status flags"],
        ["organization.py", "teacher_subjects", "id (UUID)", "teacher_id, subject_id, section_id", "Allocations linking instructors to subjects and classes"],
        ["organization.py", "access_requests", "id (UUID)", "requester_id, reviewed_by", "Administrative access privilege request workflows"],
        ["student.py", "students", "student_id (TEXT)", "classroom_id -> classrooms.id", "Core student directory, USNs, and 512-d ArcFace embeddings"],
        ["student.py", "classrooms", "classroom_id (TEXT)", "None", "Physical lecture halls and section identifiers"],
        ["attendance.py", "attendance", "id (UUID)", "student_id, classroom_id", "Session roll call records, status (present/absent), source audit"],
        ["attendance.py", "scores", "id (UUID)", "student_id, subject_id", "Continuous Internal Evaluation (CIE) test marks"],
        ["attendance.py", "risk_flags", "id (UUID)", "student_id -> students.id", "Longitudinal risk classifications, confidence, SHAP reasons JSON"],
        ["attendance.py", "semester_results", "id (UUID)", "student_id -> students.id", "Historical SGPA/CGPA records for trend slope calculations"],
        ["attendance.py", "parent_alerts", "id (UUID)", "student_id -> students.id", "Automated truancy alert queues for parent dispatch"],
        ["attendance.py", "parent_contacts", "id (UUID)", "student_id -> students.id", "Parent/guardian telephone numbers and contact details"],
        ["timetable.py", "timetable_slots", "id (UUID)", "subject_id, class_section_id", "Weekly recurring lecture and laboratory schedule slots"],
        ["notification.py", "notifications", "id (UUID)", "user_id -> users.id", "Role-targeted system alerts and announcements"],
        ["notification.py", "notification_reads", "id (UUID)", "notification_id, user_id", "Per-user notification delivery and read status tracking"],
        ["notification.py", "notifications_legacy", "id (UUID)", "None", "Archival storage for deprecated broadcast structures"],
        ["notification.py", "announcements", "id (UUID)", "created_by -> users.id", "Campus-wide broadcast announcements"],
        ["intervention.py", "interventions", "id (UUID)", "student_id, mentor_id", "Remedial counseling and academic advising logs"],
        ["intervention.py", "mentor_assignments", "id (UUID)", "student_id, mentor_id", "Legacy mentor mapping table (deprecated in 3-role runtime)"],
        ["audit.py", "audit_logs", "id (UUID)", "user_id -> users.id", "Immutable audit trail of all manual roll calls and overrides"],
        ["lms.py", "assignments", "id (UUID)", "subject_id -> subjects.id", "Homework and coursework assignment specifications"],
        ["lms.py", "assignment_submissions", "id (UUID)", "assignment_id, student_id", "Student submission files, timestamps, and grades"],
        ["lms.py", "study_materials", "id (UUID)", "subject_id -> subjects.id", "Course notes, lecture slides, and syllabus documents"],
        ["coach.py", "chat_messages", "id (UUID)", "student_id -> students.id", "Persistent conversation history for AI Study Coach RAG"]
    ]
)

add_heading_2("5.3 Face Recognition Cascade Pipeline")
add_body_paragraph("The facial recognition pipeline executes a multi-stage cascade to balance real-time execution latency with identification accuracy across variable classroom conditions.")
add_figure(os.path.join(FIGURES_DIR, "fig_5_1_face_cascade.png"), "Fig 5.1: Multi-Stage Facial Recognition Cascade Pipeline Flow")
add_body_paragraph("1. Multi-Face Detection: SCRFD processes the input image, generating bounding boxes and 5-point facial landmarks.")
add_body_paragraph("2. Texture Anti-Spoofing: Each face crop is converted to grayscale, and its Laplacian variance is evaluated. Crops with variance < 50.0 (indicating a blurred 2D replay or printout) are rejected.")
add_body_paragraph("3. ArcFace Feature Extraction: Faces are warped to 112x112 pixels and passed to the ArcFace ResNet-50 backbone, yielding a 512-dimensional normalized embedding vector.")
add_body_paragraph("4. Cosine Similarity Matching: Pairwise cosine distances are computed against all enrolled student gallery embeddings. If maximum cosine similarity >= 0.55, the student is marked PRESENT via ArcFace.")
add_body_paragraph("5. ResNet-50 Classification Fallback: If cosine similarity falls into the borderline interval [0.45, 0.55), the crop is evaluated by the secondary ResNet-50 classifier. If classification confidence >= 0.60, the identity is confirmed.")

add_heading_2("5.4 Continuous Internal Evaluation (CIE) Policy Engine")
add_body_paragraph("The CIE academic policy engine implements standard technical university assessment regulations. Internal assessment comprises three tests (CIE-1, CIE-2, CIE-3) conducted over the semester, each evaluated out of 50 marks and scaled to 25 marks. Key operational rules include:")
add_bullet_point("The final internal assessment marks are derived from the average of the student's highest two scores across the three administered tests.", bold_prefix="Best-Two-of-Three Calculation: ")
add_bullet_point("Students maintaining an average score >= 20/25 across CIE-1 and CIE-2 are exempt from CIE-3.", bold_prefix="Exemption Rule: ")
add_bullet_point("A student scoring below 20/25 average across the first two tests is mandated to take CIE-3 for remediation.", bold_prefix="Remediation Mandate: ")
add_bullet_point("An unexcused absence is recorded as zero but is preserved distinctly from an earned zero to maintain audit integrity.", bold_prefix="Absence Handling: ")

add_heading_2("5.5 Predictive Academic Risk Engine & XAI")
add_body_paragraph("The early-warning risk engine operates via a two-tier decision hierarchy: hard safety overrides take immediate precedence, followed by machine learning classification for nuanced behavioral trajectories.")
add_figure(os.path.join(FIGURES_DIR, "fig_5_2_risk_workflow.png"), "Fig 5.2: Longitudinal Academic Risk Assessment & Attribution Workflow")
add_body_paragraph("Tier 1: Deterministic Safety Overrides: Before machine learning inference, the engine evaluates three safety criteria. If a student exhibits (1) 3 or more consecutive unexcused absences, (2) an overall attendance percentage below 60%, or (3) 2 or more failed subjects, the student is flagged as HIGH RISK immediately without model execution.")
add_body_paragraph("Tier 2: XGBoost Feature Extraction & Classification: Students passing safety overrides are evaluated across an 8-variable longitudinal feature vector (overall attendance, recent attendance, average CIE score, score trend slope, failed subjects count, assignment submission rate, late submissions count, and classroom participation index). The XGBoost classifier assigns a 3-class probability distribution: Low Risk, Medium Risk, or High Risk.")
add_body_paragraph("Tier 3: SHAP Feature Attribution: For all elevated risk predictions, SHAP TreeExplainer computes exact additive Shapley values, identifying which features drove the alert and synthesizing human-readable recommendations for advisors.")

add_heading_2("5.6 Role-Scoped Notifications & Announcements")
add_body_paragraph("The notification engine delivers targeted alerts across user roles. Administrators can broadcast campus-wide announcements; teachers can issue course-specific deadline reminders; and students receive personal automated alerts when attendance drops below 75% or new assessment marks are posted. All notifications track per-user read states.")

add_heading_2("5.7 AI Academic Study Coach")
add_body_paragraph("The AI Academic Study Coach provides personalized, retrieval-augmented academic support. Operating over course syllabi, lecture notes, and student performance metrics, the coach answers curriculum queries and recommends study plans. If external LLM APIs are unreachable or disabled (offline demo mode), the coach falls back to a deterministic rule-based advising engine, ensuring 100% availability.")

add_heading_2("5.8 Structured Institutional Audit Trail")
add_body_paragraph("In compliance with university examination standards and statutory audit mandates, all manual attendance overrides, mark revisions, and administrative privilege grants are logged immutably in `audit_logs` with timestamps, actor IDs, client IP addresses, and mandatory textual justification notes.")

add_heading_2("5.9 Deployment & Infrastructure")
add_body_paragraph("VISTA is containerized via Docker Compose for turnkey institutional server deployment, detailed in Table 5.3.")
add_table_with_caption(
    "Table 5.3: Deployment and Infrastructure Specifications",
    ["Service Container", "Image / Runtime Base", "Internal Port", "Host Port Mapping", "Configuration & Purpose"],
    [
        ["Backend API", "python:3.11-slim", "8002", "127.0.0.1:8002", "FastAPI ASGI application; mounted model weights directory"],
        ["Frontend UI", "node:18-alpine / Nginx", "5173", "127.0.0.1:5173", "Vite React SPA; reverse proxies /api and /ws to backend"],
        ["Relational DB", "sqlite3 / postgres:16-alpine", "5432", "127.0.0.1:5432", "27 relational tables; SQLite development / PostgreSQL production"],
        ["In-Memory Cache", "redis:7-alpine", "6379", "127.0.0.1:6379", "Session tokens, rate limiting counters, and dashboard push cache"],
        ["Metrics Exporter", "Prometheus Client", "8002", "/metrics", "HTTP metrics endpoint scraped by institutional Prometheus server"],
        ["WebSocket Hub", "FastAPI Native WS", "8002", "/ws/dashboard", "Real-time bidirectional event stream for connected instructor clients"]
    ]
)

# Chapter 6
add_heading_1("Chapter 6: System Testing")
add_heading_2("6.1 Testing Objectives")
add_body_paragraph("The testing program was designed to validate functional correctness, role-based authorization, biometric accuracy, error resilience, and regression prevention across the entire VISTA platform.")

add_heading_2("6.2 Testing Methodology")
add_body_paragraph("Testing was conducted using pytest 8.2.2 under Python 3.11.9, incorporating automated fixtures for isolated in-memory test databases, synthetic HTTP test clients via FastAPI TestClient, and mocking for external LLM endpoints.")

add_heading_2("6.3 Test Execution Results")
add_body_paragraph("The complete automated test suite comprises 78 tests across 12 distinct test files. All 78 tests execute successfully with zero failures, achieving 100% pass rate as documented in Table 6.1.")
add_table_with_caption(
    "Table 6.1: Verified Backend and Vision Test Suite Breakdown (78 Tests, 100% Pass)",
    ["Test File Path", "Module / Area Under Test", "Test Count", "Execution Status", "Key Validated Functionality"],
    [
        ["tests/test_audit_fixes.py", "Portal Fixes & Validation", "12", "12 / 12 PASS", "Attendance cap (0..100%), 7th sem subjects, teacher scope, audit log"],
        ["tests/test_features_1_and_2.py", "Notifications, CIE & Coach", "16", "16 / 16 PASS", "Role-scoped notifications, CIE policy engine, coach deterministic fallback"],
        ["vista/backend/tests/test_attendance.py", "Attendance Endpoints", "5", "5 / 5 PASS", "Attendance logs, statistics aggregation, invalid base64 handling, 404s"],
        ["vista/backend/tests/test_auth.py", "Authentication & RBAC", "7", "7 / 7 PASS", "Login success, invalid credentials, token verification, logout blocklist"],
        ["vista/backend/tests/test_dashboard.py", "Role Dashboards & Health", "4", "4 / 4 PASS", "Admin/teacher dashboard scoping, health check connectivity"],
        ["vista/backend/tests/test_enroll.py", "Biometric Enrollment", "3", "3 / 3 PASS", "Format validation, no-face image error handling, vision import"],
        ["vista/backend/tests/test_export.py", "Reporting & CSV Export", "3", "3 / 3 PASS", "CSV stream formatting, ReportLab PDF generation, date range bounds"],
        ["vista/backend/tests/test_personal_model_attendance.py", "Hybrid Classifier Attendance", "2", "2 / 2 PASS", "Personal classifier attendance marking and batch processing"],
        ["vista/backend/tests/test_risk.py", "Academic Risk Engine", "8", "8 / 8 PASS", "Risk flag listing, level filters, student recomputation, SHAP attribution"],
        ["vista/backend/tests/test_students.py", "Student Directory CRUD", "4", "4 / 4 PASS", "Student listing, pagination limits, profile lookups, 404 handling"],
        ["vista/vision/test_recognize.py", "Vision & Biometrics", "7", "7 / 7 PASS", "ArcFace cosine similarity, matcher, embedding extraction, liveness"],
        ["vista/ml/test_risk_engine.py", "ML Risk Classification", "7", "7 / 7 PASS", "Low/med/high risk thresholds, consecutive absence overrides, zero sessions"],
        ["Total Test Suite", "Full Platform Integration", "78", "78 / 78 PASS (100%)", "Complete verified test suite with zero failing tests"]
    ]
)

add_heading_2("6.4 Error Handling & Edge Cases")
add_body_paragraph("Table 6.2 outlines the system's response across anomalous inputs and boundary conditions.")
add_table_with_caption(
    "Table 6.2: System Error Handling and Edge Case Validation Matrix",
    ["Scenario / Input Condition", "Trigger Condition", "Expected System Behavior", "HTTP Code / Payload"],
    [
        ["Invalid Image Base64", "Corrupted or non-image payload in /attendance/mark", "Rejects request; aborts inference; returns client error", "HTTP 400 Bad Request"],
        ["Unenrolled / Unknown Face", "Candidate crop cosine similarity < 0.45", "Flags face as UNKNOWN; queues for manual review; no attendance marked", "HTTP 200 (unknown flagged)"],
        ["Zero Sessions Attendance", "New student with 0 conducted classes queries portal", "Gracefully handles division by zero; displays 0.0% attendance", "HTTP 200 (att_pct: 0.0)"],
        ["Attendance Over 100%", "Discrepant session counting in numerator/denominator", "Bounds percentage strictly to [0.0, 100.0] via clamping logic", "HTTP 200 (att_pct <= 100.0)"],
        ["Teacher Cross-Course Edit", "Teacher attempts to enter marks for unallocated course", "Authorization interceptor rejects edit; logs security warning", "HTTP 403 Forbidden"],
        ["Deprecated Role Login", "User attempts login with 'hos', 'hop', or 'mentor' role", "Rejects login with ROLE_DEPRECATED detail message", "HTTP 403 Forbidden"],
        ["Offline LLM API Failure", "Study coach called with internet disabled or API error", "Catches timeout; returns deterministic rule-based advice", "HTTP 200 (fallback answer)"]
    ]
)

# Chapter 7
add_heading_1("Chapter 7: Results and Discussion")
add_heading_2("7.1 Experimental Setup & Evaluation Environment")
add_body_paragraph("Empirical evaluations were conducted on a 13th Gen Intel Core i7-13700H host (16 threads, 16 GB DDR5 RAM) in pure CPU execution mode to benchmark real-world institutional edge performance. All measurements reflect reproducible scripts in `evaluation/results/`.")

add_heading_2("7.2 Qualitative Pipeline Output Analysis")
add_body_paragraph("The facial attendance workflow processes multi-face classroom photographs, localizing faces, projecting embeddings, and verifying against enrolled records.")
add_callout_box("⚠️ Note on Dashboard Data: Attendance records and marks visible in the dashboard are seeded synthetic demo data generated by seed_demo_data() in db.py. They are not real student records. Recognition accuracy figures are derived from the real-world pilot dataset described in Section 7.3.", alert_type="info")

add_heading_2("7.3 Quantitative Performance Evaluation")
add_heading_3("7.3.1 Cosine Similarity Threshold Optimization")
add_body_paragraph("A systematic threshold sweep across 107 test facial crops from 20 enrolled gallery classes evaluated the tradeoff between False Acceptance Rate (FAR) and False Rejection Rate (FRR).")
add_table_with_caption(
    "Table 7.1: Empirical Cosine Similarity Threshold Sweep for ArcFace Matching (N=107)",
    ["Cosine Threshold (tau)", "FAR (%)", "FRR (%)", "Accuracy (%)", "F1-Score", "95% Confidence Interval"],
    [
        ["0.30", "12.15%", "2.80%", "85.05%", "0.9246", "[78.3%, 91.8%]"],
        ["0.35", "9.35%", "3.74%", "86.92%", "0.9200", "[80.5%, 93.3%]"],
        ["0.40", "6.54%", "5.61%", "87.85%", "0.9150", "[81.6%, 94.1%]"],
        ["0.45", "4.67%", "8.41%", "86.92%", "0.9020", "[80.5%, 93.3%]"],
        ["0.50", "2.80%", "12.15%", "85.05%", "0.8750", "[78.3%, 91.8%]"],
        ["0.55 (Production)", "0.93%", "16.82%", "82.24%", "0.8400", "[75.0%, 89.5%]"],
        ["0.60", "0.00%", "24.30%", "75.70%", "0.7720", "[67.6%, 83.8%]"],
        ["0.70", "0.00%", "44.86%", "55.14%", "0.5510", "[45.7%, 64.6%]"]
    ]
)
add_body_paragraph("A production threshold of tau = 0.55 was selected to minimize False Acceptances (FAR < 1.0%), relying on the secondary ResNet-50 fallback to recover rejected true positives.")

add_heading_3("7.3.2 ResNet-50 Personal Face Classifier Performance")
add_body_paragraph("The secondary ResNet-50 classifier was trained on 20 student classes using 101 unaugmented test samples in Split B.")
add_table_with_caption(
    "Table 7.2: ResNet-50 Personal Face Classifier Performance on Split B (N=101)",
    ["Evaluation Metric", "Measured Value", "95% Confidence Interval", "Operational Context"],
    [
        ["Test Accuracy", "90.10%", "[84.2%, 96.0%]", "Direct closed-set classification across 20 classes"],
        ["Macro Precision", "91.25%", "[85.6%, 96.9%]", "Average precision across all student identity classes"],
        ["Macro Recall", "90.10%", "[84.2%, 96.0%]", "Average true positive recovery rate"],
        ["Macro F1-Score", "0.9015", "[0.843, 0.960]", "Harmonic mean of precision and recall"],
        ["Training Epochs", "25 Epochs", "Convergence at epoch 18", "Cross-entropy loss optimized via Adam (lr=1e-4)"]
    ]
)
add_figure(os.path.join(FIGURES_DIR, "fig_7_1_training_curves.png"), "Fig 7.1: Training and Validation Loss Curves for ResNet-50 Face Classifier")
add_figure(os.path.join(FIGURES_DIR, "fig_7_2_confusion_matrix.png"), "Fig 7.2: Confusion Matrix for 20-Class Student Face Classification (Split B)")

add_heading_3("7.3.3 Execution Latency Profiling")
add_body_paragraph("Latency benchmarks across 100 consecutive executions on consumer CPU hardware are detailed in Table 7.3.")
add_table_with_caption(
    "Table 7.3: Execution Latency and Throughput per Pipeline Component",
    ["Pipeline Stage", "Mean Latency (ms)", "Standard Deviation (ms)", "P95 Latency (ms)", "Hardware Execution Device"],
    [
        ["SCRFD Multi-Face Detection", "71.23 ms", "4.12 ms", "78.40 ms", "Intel i7-13700H (CPU, 16 threads)"],
        ["5-Point Landmark Alignment", "1.15 ms", "0.18 ms", "1.45 ms", "OpenCV affine similarity transform"],
        ["Laplacian Anti-Spoofing Filter", "0.42 ms", "0.05 ms", "0.51 ms", "OpenCV Laplacian kernel variance"],
        ["ArcFace Embedding Extraction", "4.41 ms", "0.32 ms", "4.95 ms", "ONNX Runtime (w600k_r50.onnx)"],
        ["Cosine Similarity Gallery Match", "0.318 ms", "0.02 ms", "0.35 ms", "NumPy matrix dot product (N=20 classes)"],
        ["ResNet-50 Fallback (If Active)", "32.50 ms", "2.10 ms", "35.80 ms", "PyTorch CPU inference"],
        ["Database Attendance Commit", "8.20 ms", "1.10 ms", "9.80 ms", "SQLAlchemy SQLite commit"]
    ]
)

add_heading_3("7.3.4 Group Photo Scalability Projections")
add_body_paragraph("Table 7.4 projects execution latency across increasing classroom student densities.")
add_table_with_caption(
    "Table 7.4: Group Photo Latency Scaling Projection across Classroom Densities",
    ["Student Faces in Photo", "Detection Time (ms)", "Feature Extraction (ms)", "Matching Time (ms)", "Total Processing Time (s)"],
    [
        ["10 Students", "71.23 ms", "44.10 ms", "3.18 ms", "0.127 s"],
        ["20 Students", "71.23 ms", "88.20 ms", "6.36 ms", "0.174 s"],
        ["30 Students", "71.23 ms", "132.30 ms", "9.54 ms", "0.221 s"],
        ["40 Students", "71.23 ms", "176.40 ms", "12.72 ms", "0.268 s"],
        ["50 Students", "71.23 ms", "220.50 ms", "15.90 ms", "0.316 s"],
        ["60 Students (Full Section)", "71.23 ms", "264.60 ms", "19.08 ms", "0.363 s (0.683s with fallback)"]
    ]
)
add_figure(os.path.join(FIGURES_DIR, "fig_7_3_latency_scaling.png"), "Fig 7.3: Latency Scaling as a Function of Classroom Face Count")

add_heading_3("7.3.5 Cascade Dual-Inference Ablation")
add_body_paragraph("Ablation testing on 202 samples confirmed that adding the ResNet-50 fallback improves overall accuracy from 77.72% to 92.57% (+14.85 percentage points), with F1-score improving from 0.8747 to 0.9614 (Table 7.5).")
add_table_with_caption(
    "Table 7.5: Cascade Dual-Inference Ablation on Test Dataset (N=202)",
    ["Pipeline Configuration", "Accuracy", "F1-Score", "Operational Characteristics"],
    [
        ["Cosine-Only (ArcFace)", "0.7772 (77.72%)", "0.8747", "Standalone angular margin matcher; borderline crops rejected"],
        ["Cascade Dual-Inference", "0.9257 (92.57%)", "0.9614", "Activates ResNet-50 classifier when cosine similarity falls below 0.55"]
    ]
)

add_heading_3("7.3.6 AI Academic Coach Groundedness & Live 7-Student Verification")
add_body_paragraph("The AI Academic Coach achieved 100% groundedness and 0% hallucination across 10 structured queries (Table 7.6).")
add_table_with_caption(
    "Table 7.6: AI Academic Coach Groundedness and Hallucination Evaluation (N=10)",
    ["Metric", "Measured Value", "Evaluation Standard"],
    [
        ["Total Queries Evaluated", "10", "Representative queries spanning attendance, CIE marks, and study planning"],
        ["Grounded Responses", "10 / 10", "Every asserted fact is present in the student's database profile"],
        ["Groundedness Accuracy", "100.0%", "Zero fabricated marks, fake dates, or invented faculty names"],
        ["Hallucination Rate", "0.0%", "System prompt and RAG context strictly constrain the model"]
    ]
)

add_body_paragraph("A live group photograph trial of 7 enrolled students achieved 100% detection and recognition (Table 7.7).")
add_table_with_caption(
    "Table 7.7: 7-Student Live Group Photo Verification Confidence Scores",
    ["Student Name", "Registered USN", "Pipeline Match Source", "Confidence Score", "Attendance Status"],
    [
        ["Saheel Pradhan", "1DA23AI042", "ArcFace Cosine Match", "96.0%", "PRESENT"],
        ["Shreyas K T", "1DA22AI051 [CONFIRM]", "ArcFace Cosine Match", "71.0%", "PRESENT"],
        ["Mohammed Ayyan", "1DA24AI403", "ArcFace Cosine Match", "76.0%", "PRESENT"],
        ["Sujala Agrahari", "1DA23AI050", "ArcFace Cosine Match", "75.0%", "PRESENT"],
        ["Vignesh V", "1DA22AI061 [CONFIRM]", "ResNet-50 Fallback", "58.0%", "PRESENT"],
        ["MC Chethan Patil", "1DA22AI028 [CONFIRM]", "ArcFace Cosine Match", "73.0%", "PRESENT"],
        ["Mallikarjuna C", "1DA22AI025 [CONFIRM]", "ArcFace Cosine Match", "70.0%", "PRESENT"]
    ]
)

add_heading_3("7.3.7 Academic Risk Classifier vs. Majority Baseline")
add_body_paragraph("Evaluating the XGBoost model against a majority-class baseline demonstrated an accuracy gain from 68.0% to 89.0% (+21.0 percentage points) on the synthetic dataset (Table 7.8).")
add_table_with_caption(
    "Table 7.8: Academic Risk Classifier Evaluation vs. Majority-Class Baseline",
    ["Model Configuration", "Accuracy", "F1-Score (Macro)", "Precision (Macro)", "Recall (Macro)"],
    [
        ["Majority-Class Baseline", "0.6800 (68.0%)", "0.2700", "0.2267", "0.3333"],
        ["VISTA XGBoost + Overrides", "0.8900 (89.0%)", "0.6850", "0.7100", "0.6650"]
    ]
)

add_heading_2("7.4 Operational Limitations of Evaluation")
add_body_paragraph("To maintain rigorous academic honesty, several key evaluation constraints are documented:")
add_bullet_point("Attendance records, test scores, and risk flags displayed in the web dashboard are synthetic demo data generated by seed_demo_data() in db.py. In contrast, biometric face recognition results reflect real photographs.", bold_prefix="1. Synthetic Seeded Demo Records: ")
add_bullet_point("The facial evaluation cohort comprises 20 real student identities (711 raw images; 20,130 augmented crops). Evaluation on larger cohorts across diverse lighting conditions is required.", bold_prefix="2. Closed-Set Cohort Size: ")
add_bullet_point("Experiments evaluated closed-set gallery matching. The system does not yet incorporate open-set anomaly rejection for unknown campus visitors.", bold_prefix="3. Absence of Open-Set Stranger Evaluation: ")
add_bullet_point("Anti-spoofing is currently enforced using Laplacian texture variance heuristics. Robust defense against high-resolution electronic replays requires deep models such as MiniFASNet.", bold_prefix="4. Heuristic Anti-Spoofing: ")
add_bullet_point("The XGBoost risk model was trained on 1,000 synthetic student profiles. Training on multi-year institutional academic records is necessary for production deployment.", bold_prefix="5. Synthetic Risk Training Labels: ")

add_heading_2("7.5 Visual Interface Verification (Screenshots)")
add_body_paragraph("The real interfaces of the VISTA platform are illustrated below:")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_2_teacher_attendance.png"), "Fig 7.4: Live Teacher Facial Attendance Verification View")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_3_student_dashboard.png"), "Fig 7.5: Student Self-Service Portal Dashboard")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_4_student_subject_drilldown.png"), "Fig 7.6: Student Subject Attendance & CIE Marks Drill-Down")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_5_admin_control_centre.png"), "Fig 7.7: Administrator Academic Control Centre")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_6_admin_student_roster.png"), "Fig 7.8: Centralized Student Roster & Face Enrollment View")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_7_student_profile_risk.png"), "Fig 7.9: Comprehensive Student Profile & Academic Risk View")
add_figure(os.path.join(SCREENSHOTS_DIR, "fig_7_8_manual_entry_console.png"), "Fig 7.10: Teacher & Admin Manual Attendance & Marks Console")

add_callout_box("[SCREENSHOT NEEDED: Interactive chat interface of the AI Study Coach showing grounded student academic advising dialog and study tips (Fig 7.11)]", alert_type="warning")

# Applications, Conclusions, Future Enhancements, References
add_heading_1("Applications")
add_body_paragraph("The VISTA system addresses systemic operational inefficiencies across higher educational institutions through several distinct operational deployments:")
add_bullet_point("Replaces manual roll calls with rapid single-shot group photo capture, logging attendance for up to 60 students in less than 0.7 seconds.", bold_prefix="1. Automated Lecture Hall Attendance: ")
add_bullet_point("Correlates attendance streaks, CIE marks, and assignment submissions to flag vulnerable students weeks before semester examinations.", bold_prefix="2. Proactive Academic Advising & Retention: ")
add_bullet_point("Maintains immutable audit records required for autonomous university accreditation under NAAC Criteria 2 and NBA Outcome-Based Education.", bold_prefix="3. Institutional Accreditation Compliance: ")
add_bullet_point("Eliminates recurring per-user cloud API fees and preserves student biometric privacy under the Digital Personal Data Protection Act 2023.", bold_prefix="4. Privacy-Preserving On-Premise Governance: ")

add_heading_1("Conclusions and Future Enhancements")
add_heading_2("Conclusions")
add_body_paragraph("The VISTA project successfully demonstrates an integrated, on-premise intelligent classroom management system. By combining SCRFD face detection with ArcFace 512-dimensional embeddings and an auxiliary ResNet-50 personal classifier, VISTA achieves 92.57% recognition accuracy across dense classroom photographs while executing in under 0.7 seconds on commodity x86 CPUs without GPU hardware. The XGBoost early-warning risk engine achieves 89.0% accuracy, paired with SHAP to deliver transparent, plain-language attribution factors to faculty counselors.")

add_heading_2("Future Enhancements")
add_body_paragraph("Several engineering and algorithmic priorities are established for future development:")
add_bullet_point("Replace the current Laplacian variance texture check with MiniFASNet (Silent-Face-Anti-Spoofing) for deep anti-spoofing against high-resolution screen replays.", bold_prefix="1. Deep Neural Anti-Spoofing: ")
add_bullet_point("Retrain the XGBoost risk model on multi-year institutional student academic histories under formal institutional review board (IRB) ethical clearance.", bold_prefix="2. Multi-Year Historical Risk Training: ")
add_bullet_point("Transition from SQLite to PostgreSQL 16 with connection pooling for concurrent multi-classroom deployments.", bold_prefix="3. Enterprise PostgreSQL Migration: ")
add_bullet_point("Deploy open-set identity rejection via threshold-calibrated softmax to reject un-enrolled campus visitors without false identification.", bold_prefix="4. Open-Set Recognition: ")

add_heading_1("References")
for ref_line in REFERENCES_TEXT.split("\n\n"):
    if ref_line.strip() and not ref_line.startswith("##"):
        add_body_paragraph(ref_line.strip())

# Save DOCX
doc.save(OUTPUT_DOCX)
print(f"Generated {OUTPUT_DOCX}")

# ---------------------------------------------------------------------------
# 3. Assemble REPORT_CHECKLIST.md
# ---------------------------------------------------------------------------

CHECKLIST_CONTENT = """# REPORT_CHECKLIST: Verification & Media Requirement Matrix
**Document:** `FINAL_REPORT.docx` / `FINAL_REPORT.md`  
**Exhibition Date:** 7 November 2026  
**Generated Date:** 2026-11-04  

This checklist catalogs every `[CONFIRM]` marker and `[SCREENSHOT NEEDED]` placeholder present in the final report, providing the exact location and the specific confirmation or file required from the project team.

---

## 1. Editorial Confirmation Markers ([CONFIRM])

| # | Chapter / Section | Item / Context | Current Text in Report | Action Required from Team |
|---|---|---|---|---|
| 1 | Certificate & Title Page | Project Guide Designation | `Dr. Ajayprakash B V [CONFIRM designation and spelling]` | Confirm exact spelling and academic title (Associate Professor vs. Assistant Professor) with guide |
| 2 | Certificate | Head of School (HOS) | `Dr. Ajayprakash B V [CONFIRM designation]` | Confirm exact institutional HOS designation on college portal |
| 3 | Certificate | Head of Programme (HOP) | `Dr. Bharath V S [CONFIRM spelling and designation]` | Confirm spelling ("Bharath" vs. "Bharat") and designation |
| 4 | Title Page & Cert | Course Code & Name | `Major Project Phase-II, code 22AIP706 [CONFIRM]` | Confirm course code from VTU 7th semester syllabus scheme |
| 5 | Title Page & Cert | Academic Year | `2026-27 [CONFIRM]` | Confirm whether printed report should state 2026–27 or 2025–26 |
| 6 | Table 7.7 | Shreyas K T USN | `1DA22AI051 [CONFIRM]` | Verify USN against student institutional ID card |
| 7 | Table 7.7 | Vignesh V USN | `1DA22AI061 [CONFIRM]` | Verify USN against student institutional ID card |
| 8 | Table 7.7 | MC Chethan Patil USN | `1DA22AI028 [CONFIRM]` | Verify USN against student institutional ID card |
| 9 | Table 7.7 | Mallikarjuna C USN | `1DA22AI025 [CONFIRM]` | Verify USN against student institutional ID card |

---

## 2. Media & Visual Asset Requirements ([SCREENSHOT NEEDED])

| # | Chapter / Section | Figure ID | Caption / Subject | Missing Asset Status & Instructions |
|---|---|---|---|---|
| 1 | Chapter 7 §7.5 | **Fig 7.11** | `AI Academic Study Coach Chat Interface` | **[SCREENSHOT NEEDED]**: Start the frontend (`npm run dev`), navigate to the AI Study Coach tab, execute a query (e.g. asking for CIE review or attendance tips), capture a clean screenshot, save it to `docs/screenshots/fig_7_11_study_coach.png`, and re-run report generator or paste into Word. |

---

## 3. Microsoft Word Final Polish Instructions (After Opening FINAL_REPORT.docx)

1. **Table of Contents Update:**
   - Click anywhere inside the Table of Contents on page iii.
   - Press **F9** on the keyboard (or right-click and choose **Update Field** -> **Update entire table**).
   - Word will automatically calculate exact page numbers for every chapter and subsection.
2. **Prepend Front Matter Pages:**
   - Insert the three signed physical front pages in front of the Abstract:
     - Page 1: Title Cover Page
     - Page 2: Signed Certificate Page
     - Page 3: Acknowledgements Page (assigned Roman numeral `i`)
   - The Abstract will automatically align at Roman numeral `ii`, with Chapter 1 commencing at Arabic numeral `1`.
"""

with open(OUTPUT_CHECKLIST, "w", encoding="utf-8") as f:
    f.write(CHECKLIST_CONTENT)
print(f"Generated {OUTPUT_CHECKLIST}")

print("\nAll Part C deliverables compiled successfully!")
