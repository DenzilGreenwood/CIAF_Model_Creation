# AI Governance Landscape: A Comprehensive Regulatory and Standards Framework

**Document Version:** 1.0  
**Date:** October 18, 2025  
**Classification:** Professional Reference Document  

---

## Executive Summary

This document provides a comprehensive overview of the current artificial intelligence (AI) governance landscape, encompassing binding laws, international frameworks, technical standards, and implementation procedures. It serves as a strategic reference for organizations seeking to develop compliant-by-design AI systems across multiple jurisdictions.

The landscape analysis covers regulatory requirements from major jurisdictions including the European Union, United States, United Kingdom, Singapore, China, and Brazil, alongside international standards and frameworks from ISO/IEC, NIST, OECD, and other authoritative bodies.

---

## Table of Contents

1. [Regulatory Landscape Overview](#regulatory-landscape-overview)
2. [Binding Laws and Treaties](#binding-laws-and-treaties)
3. [Government Frameworks and Guidance](#government-frameworks-and-guidance)
4. [International Principles and Standards](#international-principles-and-standards)
5. [Privacy Laws with AI Implications](#privacy-laws-with-ai-implications)
6. [Implementation Requirements](#implementation-requirements)
7. [Repository Structure and Implementation Strategy](#repository-structure-and-implementation-strategy)
8. [Timeline and Compliance Roadmap](#timeline-and-compliance-roadmap)
9. [Recommendations](#recommendations)

---

## Regulatory Landscape Overview

The AI governance ecosystem has rapidly evolved, with 2024-2025 marking a critical inflection point where theoretical frameworks have crystallized into enforceable regulations. Organizations must now navigate a complex matrix of overlapping jurisdictional requirements, each with distinct compliance timelines and obligations.

### Key Regulatory Themes

- **Risk-based approach**: Most regulations adopt tiered risk classifications
- **Lifecycle governance**: Requirements span development, deployment, and monitoring phases  
- **Human oversight**: Mandatory human-in-the-loop or human-on-the-loop mechanisms
- **Transparency and explainability**: Public disclosure and algorithmic accountability
- **Technical documentation**: Comprehensive system documentation and audit trails
- **Quality management**: Formal QMS requirements for high-risk applications

---

## Binding Laws and Treaties

### European Union

#### EU Artificial Intelligence Act (Regulation (EU) 2024/1689)

**Status:** In force August 1, 2024  
**Scope:** Providers, deployers, importers, distributors in EU market

**Key Implementation Timeline:**
- **February 2, 2025:** Prohibited uses and AI literacy requirements
- **August 2, 2025:** General-Purpose AI (GPAI) transparency obligations
- **August 2, 2026-2027:** High-risk system obligations

**Core Requirements:**
- Risk classification system (prohibited, high-risk, limited risk, minimal risk)
- Provider Quality Management System (QMS) requirements
- Technical documentation and CE marking for high-risk systems
- Logging and traceability across system lifecycle
- Fundamental Rights Impact Assessments (FRIA) for public sector deployers
- Conformity assessment procedures

**Key Articles:**
- Article 9: Risk management systems
- Article 10: Data governance requirements
- Article 12: Logging and record-keeping
- Article 14: Human oversight obligations
- Article 16: Provider obligations
- Article 43: Conformity assessment procedures

#### Additional Resource: [The AI Act - artificialintelligenceact.eu](https://artificialintelligenceact.eu/the-act/)
Comprehensive unofficial resource providing article-by-article analysis and implementation guidance for the EU AI Act.

### United States

#### Colorado AI Act (SB24-205)
**Status:** Effective February 1, 2026  
**Scope:** Developers and deployers of high-risk AI systems

**Core Requirements:**
- "Reasonable care" standard in development and deployment
- Risk management frameworks
- Algorithmic impact assessments
- Consumer notice and disclosure obligations
- Incident reporting for algorithmic discrimination

#### Additional Resource: [Colorado AI Act - Official Text](https://leg.colorado.gov/bills/sb24-205)
Complete text of the Colorado AI Act for reference.


#### New York City Local Law 144 (AEDT)
**Status:** Enforcement ongoing since 2023  
**Scope:** Employers and agencies using Automated Employment Decision Tools for NYC positions

**Core Requirements:**
- Annual independent bias audit by qualified third parties
- Public posting of audit summaries
- Selection rate and impact ratio metrics disclosure
- Candidate notification requirements
- Data collection opt-out mechanisms

#### Additional Resource: [NYC Local Law 144 - Official Text](https://rules.cityofnewyork.us/rule/automated-employment-decision-tools-updated/)

#### California ADMT Regulations (CPPA)
**Status:** Effective January 1, 2026  
**Scope:** Businesses covered under CCPA/CPRA

**Core Requirements:**
- Consumer rights and opt-out for Automated Decision-Making Technology (ADMT)
- Risk assessment obligations
- Annual cybersecurity audits
- Enhanced transparency requirements

#### Additional Resource: [California ADMT Regulations - Official Text](https://cppa.ca.gov/announcements/2025/20250923.html)

### Other Major Jurisdictions

#### [Council of Europe Framework Convention on AI](https://www.coe.int/en/web/artificial-intelligence/the-framework-convention-on-artificial-intelligence)
**Status:** Opened for signature September 5, 2024  
**Scope:** Signatory states (binding upon ratification)

Establishes human rights-anchored AI governance requirements for participating nations.

#### [Brazil LGPD Article 20](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais/lgpd-en-lei-no-13-709-capa.pdf)
**Status:** In force  
**Scope:** Controllers processing Brazilian residents' data

Grants individuals rights to explanation and human review of automated decisions.

#### [China Interim Measures for Generative AI](https://www.chinalawtranslate.com/en/generative-ai-interim/)
**Status:** Effective August 15, 2023  
**Scope:** Providers of generative AI services to public in mainland China

**Core Requirements:**
- Safety and security protocols
- Content labeling and truthfulness standards
- Data governance obligations
- Regulatory filings for public services

---

## Government Frameworks and Guidance

### United States Federal Guidance

#### NIST AI Risk Management Framework (AI RMF 1.0)
**Status:** Published January 2023  
**Scope:** Cross-sector voluntary framework

**Core Functions:**
- **Govern:** Establish organizational AI governance
- **Map:** Contextualize AI risks and opportunities  
- **Measure:** Analyze and track AI risks
- **Manage:** Allocate resources to manage AI risks

#### [NIST Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
**Status:** Published 2024  
Provides sector-agnostic guidance for managing generative AI risks across the AI lifecycle.

#### [OMB M-24-10](https://www.whitehouse.gov/wp-content/uploads/2024/03/M-24-10-Advancing-Governance-Innovation-and-Risk-Management-for-Agency-Use-of-Artificial-Intelligence.pdf)
**Status:** March 28, 2024  
**Scope:** US Federal agencies

Mandates AI inventories, risk assessments, and safety guardrails for rights and safety-impacting AI uses.

#### Sectoral Guidance
- **[FDA](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence):** Final guidance on Predetermined Change Control Plans (PCCP) for AI-enabled medical devices
- **[FTC](https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes):** Enforcement actions targeting deceptive AI claims and unfair data practices
- **[EEOC](https://www.eeoc.gov/2023-annual-performance-report):** Technical assistance on AI compliance with Title VII employment discrimination laws

### United Kingdom

#### Pro-Innovation Regulatory Approach
The UK maintains a regulator-led framework without omnibus AI legislation. The [AI Safety Institute](https://www.gov.uk/government/publications/ai-safety-institute-approach-to-evaluations) publishes evaluation approaches for advanced AI models.

### Singapore

#### [Model AI Governance Framework](https://www.pdpc.gov.sg/help-and-resources/2020/01/second-edition-of-model-artificial-intelligence-governance-framework)
**Original Version:** January 21, 2020  
**Generative AI Update:** May 30, 2024

**Core Dimensions:**
- Internal governance structures
- Human involvement requirements
- Operations management
- Stakeholder communications
- Data governance
- Testing and assurance
- Content provenance
- Incident reporting

**Sector-Specific:** [MAS FEAT Principles](https://www.mas.gov.sg/publications/monographs-or-information-paper/2018/feat) for financial institutions (Fairness, Ethics, Accountability, Transparency)

---

## International Principles and Standards

### ISO/IEC Standards Suite

#### ISO/IEC 42001:2023 - AI Management System (AIMS)
**Status:** Published December 2023  
**Type:** Certifiable management system standard

Establishes requirements for AI governance using Plan-Do-Check-Act (PDCA) methodology.

#### [ISO/IEC 42006:2025 - AIMS Certification Bodies](https://www.iso.org/standard/42006)
**Status:** Published July 2025  
Defines requirements for bodies auditing and certifying against ISO/IEC 42001.

#### [ISO/IEC 23894:2023 - AI Risk Management](https://www.iso.org/standard/77304.html)  
**Status:** Published 2023  
Provides processes to identify, assess, treat, and monitor AI risks, mapping to ISO 31000.

#### [ISO/IEC TS 6254:2025 - Explainability & Interpretability](https://www.iso.org/standard/82148.html)
**Status:** Published September 2025  
Defines objectives and approaches for AI explainability across the system lifecycle.

#### [ISO/IEC 38507:2022 - Board-Level AI Governance](https://www.iso.org/standard/56641.html)
**Status:** Published 2022  
Provides governance guidance for executive leadership and governing bodies.

### International Principles

#### [OECD AI Principles](https://oecd.ai/en/ai-principles) (Updated 2024)
- Human-centered values and fairness
- Transparency and explainability  
- Robustness, security, and safety
- Accountability

#### [G7 Hiroshima Process](https://www.mofa.go.jp/files/100573471.pdf)
- Guiding Principles for AI development
- Code of Conduct for advanced AI systems

#### UNESCO Recommendation on AI Ethics (2021)
Comprehensive framework emphasizing human rights, human oversight, transparency, and fairness.

---

## Privacy Laws with AI Implications

### [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) and UK GDPR
**Key Provisions:**
- [Article 22](https://gdpr-info.eu/art-22-gdpr/): Rights regarding automated decision-making
- [Article 35](https://gdpr-info.eu/art-35-gdpr/): Data Protection Impact Assessment (DPIA) requirements for high-risk processing

### California Privacy Laws (CCPA/CPRA)
Enhanced ADMT regulations requiring consumer rights, opt-out mechanisms, and risk assessments.

### Brazil LGPD Article 20
Grants rights to explanation and human review of automated decisions affecting data subjects.

---

## Implementation Requirements

Organizations must implement the following core processes to achieve regulatory compliance:

### 1. Risk Management (Lifecycle)
- Continuous risk identification, assessment, treatment, and monitoring
- Pre-deployment testing and validation
- Periodic re-assessment protocols
- **Regulatory References:** EU AI Act Article 9, ISO/IEC 23894, NIST AI RMF

### 2. Data Governance
- Dataset lineage and provenance tracking
- Representativeness and relevance validation
- Data minimization principles
- Bias and quality assessment protocols
- Source documentation and collection purpose records
- **Regulatory References:** EU AI Act Article 10

### 3. Human Oversight Design
- Intervention and override capabilities
- Confidence threshold mechanisms
- Fallback procedures
- Operator training requirements
- Misuse scenario planning
- **Regulatory References:** EU AI Act Article 14

### 4. Technical Documentation
- System description and intended purpose
- Architecture documentation
- Training and evaluation methodologies
- Performance metrics and limitations
- Hazard analysis and residual risk assessment
- User instructions and operational guidelines
- **Regulatory References:** EU AI Act provider obligations, conformity assessment requirements

### 5. Logging and Traceability
- Immutable decision and event logs
- Input/output tracking
- Version control and change management
- Human intervention recording
- **Regulatory References:** EU AI Act Article 12

### 6. Quality Management System (QMS)
- Policy framework and procedures
- Role definition and competence management
- Supplier and vendor controls
- Corrective action procedures
- Internal audit programs
- **Regulatory References:** EU AI Act provider obligations, ISO/IEC 42001

### 7. Conformity Assessment and CE Marking (EU)
- Risk classification determination
- Assessment route selection (internal control vs. notified body)
- Technical file compilation
- CE marking affixment for high-risk systems
- **Regulatory References:** EU AI Act Article 43

### 8. Impact Assessments
- Fundamental Rights Impact Assessment (FRIA) for EU public sector deployments
- Data Protection Impact Assessment (DPIA) under GDPR
- Algorithmic impact assessments under various jurisdictions
- **Regulatory References:** EU AI Act, GDPR Article 35, California ADMT regulations

### 9. Bias Auditing (Jurisdiction-Specific)
- Annual third-party bias audits (NYC requirement)
- Selection rate and impact ratio metrics
- Public disclosure of audit summaries
- **Regulatory References:** NYC Local Law 144

### 10. Post-Market Monitoring and Incident Reporting
- Performance degradation triggers
- Severity classification systems
- Regulatory notification timelines
- Model change control procedures
- **Regulatory References:** FDA PCCP guidance, various jurisdictional requirements

### 11. Security by Design
- Model provenance and supply chain security
- Software Bill of Materials (SBOM) for AI systems
- Secrets management protocols
- Red team and adversarial testing
- **Regulatory References:** [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final), [NIST SP 800-218A](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218A.pdf)

### 12. Governance and Accountability
- Board-level oversight mechanisms
- Role and responsibility matrices (RACI)
- Competence and training programs
- Vendor risk management
- **Regulatory References:** ISO/IEC 42001, ISO/IEC 38507

### 13. Transparency and User Disclosure
- AI interaction notifications
- Capability and limitation disclosures
- Data usage transparency
- Appeal and redress mechanisms
- **Regulatory References:** OECD Principles, G7 Code of Conduct, multiple jurisdictional laws

---

## Repository Structure and Implementation Strategy

### Recommended Directory Structure

```
ai-governance-landscape/
├── README.md
├── laws/
│   ├── eu-ai-act/
│   │   ├── articles/
│   │   ├── timelines/
│   │   ├── templates/
│   │   │   ├── FRIA.md
│   │   │   └── CA-checklist.md
│   ├── us-colorado-sb24-205/
│   ├── us-nyc-ll144/
│   ├── cn-genai-measures/
│   └── privacy/
│       ├── GDPR-Art22.md
│       ├── DPIA.md
│       ├── CPRA-ADMT.md
│       └── LGPD-Art20.md
├── frameworks/
│   ├── nist-ai-rmf/
│   │   └── GENAI-Profile.md
│   ├── uk-aisi/
│   │   └── eval-approach.md
│   └── sg-model-framework/
│       ├── 2019-framework/
│       ├── 2020-updates/
│       └── 2024-genai/
├── standards/
│   ├── iso-42001/
│   ├── iso-42006/
│   ├── iso-23894/
│   ├── iso-38507/
│   ├── iso-ts-6254/
│   ├── isms-27001/
│   ├── pims-27701/
│   └── nist-ssdf-800-218/
├── procedures/
│   ├── risk-management.md
│   ├── data-governance.md
│   ├── model-card.md
│   ├── system-card.md
│   ├── human-oversight-playbook.md
│   ├── logging-traceability.md
│   ├── bias-audit-nyc.md
│   ├── conformity-assessment-eu.md
│   ├── postmarket-monitoring.md
│   ├── incident-reporting.md
│   ├── change-control-pccp-pattern.md
│   └── security-ssdf-checklist.md
├── checklists/
│   ├── high-risk-readiness.xlsx
│   ├── dpia-template.docx
│   ├── fria-template.md
│   └── vendor-due-diligence.md
└── data/
    └── ai_governance_landscape_baseline.csv
```

### Implementation Strategy: Fastest Path to Compliant-by-Design

#### 1. Control Spine Selection
**Recommended Approach:** Adopt ISO/IEC 42001 (AIMS) as the management backbone and map controls to NIST AI RMF tasks. Utilize ISO/IEC 23894 to formalize the risk management loop.

**Benefits:**
- Provides certification pathway
- Aligns with US-friendly framework language
- Establishes internationally recognized governance structure

#### 2. Jurisdictional Overlay Strategy
**EU AI Act Compliance:**
- Implement risk tiering classification
- Establish QMS specifics for high-risk systems
- Develop FRIA procedures for public sector deployments
- Prepare conformity assessment documentation

**US Jurisdictional Requirements:**
- NYC bias audit procedures (hiring tools only)
- Colorado SB24-205 programmatic safeguards (high-risk systems)
- Federal sector compliance (OMB M-24-10 for government contractors)

#### 3. Privacy Integration
- Ensure DPIA triggers are properly configured
- Implement automated decision rights workflows
- Establish California ADMT notice and opt-out mechanisms
- Design privacy-by-design data processing flows

#### 4. Secure Development Integration
- Adopt NIST Secure Software Development Framework (SSDF)
- Implement NIST SP 800-218A for AI-specific development security
- Establish adversarial testing protocols
- Define model provenance and evaluation procedures

#### 5. Assurance and Certification
- Plan for ISO/IEC 42001 certification using ISO/IEC 42006 audit guidelines
- Establish internal audit capabilities
- Design continuous compliance monitoring systems

---

## Timeline and Compliance Roadmap

### Critical Upcoming Deadlines

#### 2025
- **February 2, 2025:** EU AI Act prohibited uses and AI literacy requirements
- **August 2, 2025:** EU AI Act GPAI transparency and systemic risk model duties

#### 2026
- **January 1, 2026:** California ADMT regulations effective
- **February 1, 2026:** Colorado AI Act effective
- **August 2, 2026:** EU AI Act high-risk system obligations begin phased implementation

#### 2027
- **2026-2027:** Full EU AI Act high-risk system compliance required
- **Ongoing:** Conformity assessments and CE marking requirements

### Regulatory Monitoring Points

#### European Union
- Monitor European Commission guidance on AI Act implementation
- Track notified body designation for conformity assessments
- Follow harmonized standards development for technical compliance

#### United States
- Watch for federal AI legislation development
- Monitor state-level AI regulation expansion
- Track sectoral regulator guidance updates (FDA, FTC, EEOC, CFPB)

#### United Kingdom
- Follow AI Safety Institute evaluation methodology releases
- Monitor sectoral regulator approach evolution
- Track potential future omnibus AI legislation

#### International
- Monitor ISO/IEC AI standards development pipeline
- Track OECD AI Principles implementation guidance
- Follow G7 and multilateral AI governance initiatives

---

## Recommendations

### Immediate Actions (0-3 months)

1. **Regulatory Mapping Exercise**
   - Conduct comprehensive analysis of applicable jurisdictions
   - Map current AI systems to regulatory risk categories
   - Identify compliance gaps and resource requirements

2. **Governance Foundation**
   - Establish AI governance committee with board-level oversight
   - Implement ISO/IEC 42001 management system framework
   - Define roles, responsibilities, and accountability structures

3. **Risk Assessment Framework**
   - Implement NIST AI RMF methodology
   - Establish continuous risk monitoring capabilities
   - Define risk appetite and tolerance statements

### Medium-Term Implementation (3-12 months)

1. **Process Development**
   - Develop comprehensive AI lifecycle procedures
   - Implement quality management system requirements
   - Establish technical documentation standards

2. **Technical Capabilities**
   - Deploy logging and traceability infrastructure
   - Implement bias detection and mitigation tools
   - Establish model versioning and change control systems

3. **Compliance Integration**
   - Integrate privacy and AI compliance workflows
   - Develop impact assessment templates and procedures
   - Establish vendor due diligence frameworks

### Long-Term Maturity (12+ months)

1. **Certification and Assurance**
   - Pursue ISO/IEC 42001 certification
   - Establish internal audit capabilities
   - Implement continuous compliance monitoring

2. **Advanced Capabilities**
   - Deploy automated compliance monitoring tools
   - Establish AI ethics review boards
   - Implement advanced explainability and transparency features

3. **Ecosystem Integration**
   - Participate in industry standards development
   - Engage with regulatory sandboxes and pilot programs
   - Contribute to AI governance best practice development

---

## Conclusion

The AI governance landscape has reached a critical maturity point where regulatory compliance is no longer optional but essential for sustainable AI deployment. Organizations must adopt a proactive, multi-jurisdictional approach that integrates governance, technical, and operational requirements from the outset of AI system development.

Success requires a comprehensive strategy that balances regulatory compliance with innovation objectives, utilizing established frameworks like ISO/IEC 42001 and NIST AI RMF as foundational elements while layering jurisdiction-specific requirements as needed.

The window for reactive compliance approaches is rapidly closing. Organizations that establish robust AI governance frameworks now will be best positioned to adapt to the evolving regulatory landscape while maintaining competitive advantage in the AI-driven economy.

---

**Document Control:**
- **Document Owner:** Cognitive Insight AI Framework (CIAF) Team
- **Next Review Date:** January 18, 2026
- **Distribution:** Internal governance and compliance teams
- **Version History:** v1.0 - Initial release (October 18, 2025)

**References:**
- Complete source citations and regulatory links available in accompanying CSV dataset
- Official regulatory texts and standards documents
- Industry best practice guidelines and frameworks

---

## Sources (authoritative)
- EU Artificial Intelligence Act (Regulation (EU) 2024/1689): https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
- Council of Europe Framework Convention on AI: https://www.coe.int/en/web/artificial-intelligence/the-framework-convention-on-artificial-intelligence
- Colorado AI Act (SB24-205): https://leg.colorado.gov/bills/sb24-205
- New York City Local Law 144 (AEDT): https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page
- California ADMT Regulations (CPPA): https://cppa.ca.gov/announcements/2025/20250923.html
- Brazil LGPD Article 20: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais/lgpd-en-lei-no-13-709-capa.pdf
- China Interim Measures for Generative AI: https://www.chinalawtranslate.com/en/generative-ai-interim/
- NIST AI Risk Management Framework (AI RMF 1.0): https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
- NIST Generative AI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- OMB M-24-10: https://www.whitehouse.gov/wp-content/uploads/2024/03/M-24-10-Advancing-Governance-Innovation-and-Risk-Management-for-Agency-Use-of-Artificial-Intelligence.pdf
- FDA: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence
- FTC: https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes
- EEOC: https://www.eeoc.gov/2023-annual-performance-report
- AI Safety Institute: https://www.gov.uk/government/publications/ai-safety-institute-approach-to-evaluations
- Model AI Governance Framework: https://www.pdpc.gov.sg/help-and-resources/2020/01/second-edition-of-model-artificial-intelligence-governance-framework
- Model Framework for Generative AI: https://aiverifyfoundation.sg/wp-content/uploads/2024/05/Model-AI-Governance-Framework-for-Generative-AI-May-2024-1-1.pdf
- MAS FEAT Principles: https://www.mas.gov.sg/publications/monographs-or-information-paper/2018/feat
- ISO/IEC 42001:2023 - AI Management System (AIMS): https://www.iso.org/standard/42001
- ISO/IEC 42006:2025 - AIMS Certification Bodies: https://www.iso.org/standard/42006
- ISO/IEC 23894:2023 - AI Risk Management: https://www.iso.org/standard/77304.html
- ISO/IEC TS 6254:2025 - Explainability & Interpretability: https://www.iso.org/standard/82148.html
- ISO/IEC 38507:2022 - Board-Level AI Governance: https://www.iso.org/standard/56641.html
- OECD AI Principles: https://oecd.ai/en/ai-principles
- G7 Hiroshima Process: https://www.mofa.go.jp/files/100573471.pdf
- UNESCO Recommendation on AI Ethics (2021): https://www.unesco.org/en/artificial-intelligence/recommendation-ethics
- GDPR: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- Article 22: https://gdpr-info.eu/art-22-gdpr/
- Article 35: https://gdpr-info.eu/art-35-gdpr/
- California Privacy Laws (CCPA/CPRA): https://cppa.ca.gov/regulations/ccpa_updates.html
- SR 11-7: https://www.federalreserve.gov/supervisionreg/srletters/sr1107a1.pdf
- OCC 2011-12: https://www.occ.treas.gov/news-issuances/bulletins/2011/bulletin-2011-12a.pdf
- FDIC FIL-22-2017: https://www.fdic.gov/news/financial-institution-letters/2017/fil17022.html
- NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- NIST SP 800-218A: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218A.pdf