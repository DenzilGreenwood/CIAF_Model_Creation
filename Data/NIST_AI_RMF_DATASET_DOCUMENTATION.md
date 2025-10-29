# NIST AI Risk Management Framework (AI RMF 1.0) - Dataset Documentation

## Primary Source Citation

**Formal Citation (APA-style):**
Tabassi, E. (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.100-1

## Dataset Information

- **Title**: AI RMF 1.0 (Artificial Intelligence Risk Management Framework)
- **Author**: Elham Tabassi
- **Publisher**: National Institute of Standards and Technology (NIST)
- **Publication Year**: 2023
- **Document Type**: Federal Standard
- **DOI**: 10.6028/NIST.AI.100-1
- **Canonical URL**: https://doi.org/10.6028/NIST.AI.100-1
- **PDF URL**: https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf

## Dataset Usage in Training

- **Local File**: `data/corpus/NIST.txt`
- **Training Split**: `data/train/nist_ai_rmf_train.txt` (85% - 124 sentences)
- **Evaluation Split**: `data/eval/nist_ai_rmf_eval.txt` (15% - 22 sentences)
- **Total Content**: 21,412 characters, 146 sentences
- **Domain**: AI Risk Management, Federal Standards, Technology Governance

## Content Summary

The NIST AI Risk Management Framework provides a comprehensive approach for organizations to:

1. **Govern AI Systems**: Establish governance structures and policies
2. **Map AI Risks**: Identify and categorize potential risks
3. **Measure AI Performance**: Implement metrics and monitoring
4. **Manage AI Lifecycle**: Control risks throughout development and deployment

## Key Concepts Covered

- AI Actor roles and responsibilities (Design, Development, Deployment, Operations)
- Test, Evaluation, Verification, and Validation (TEVV) processes
- Human Factors integration
- Domain Expert involvement
- AI Impact Assessment methodologies
- Procurement and acquisition guidelines
- Governance and oversight frameworks
- Cross-sectoral risk profiles

## Training Configuration

**Primary Config**: `configs/nist_ai_rmf_from_eu.yaml`
- Transfer learning from EU AI Act averaged checkpoint
- Optimized for regulatory/governance text domain
- Batch size: 2 (optimized for smaller dataset)
- Learning rate: 1.0e-4 (fine-tuning rate)
- Epochs: 3 (sufficient for transfer learning)

## Legal and Usage Notes

- **Public Domain**: NIST publications are in the public domain
- **No Copyright Restrictions**: Free to use for training and research
- **Attribution Required**: Proper citation should be maintained
- **Federal Standard**: Official U.S. government guidance document

## Model Training Provenance

```yaml
dataset:
  name: "NIST AI RMF 1.0"
  source: "National Institute of Standards and Technology"
  citation: "Tabassi, E. (2023). AI RMF 1.0. NIST. https://doi.org/10.6028/NIST.AI.100-1"
  doi: "10.6028/NIST.AI.100-1"
  date_accessed: "2025-10-27"
  local_path: "data/corpus/NIST.txt"
  preprocessing: "sentence-level splitting, 85/15 train/eval split"
  content_type: "federal_standard_regulatory_text"
```

## Training Objectives

1. **Domain Transfer**: Extend EU AI Act knowledge to NIST RMF framework
2. **Risk Management**: Enhance understanding of AI risk assessment methodologies
3. **Governance Integration**: Connect regulatory compliance with practical implementation
4. **Cross-Framework Knowledge**: Bridge EU and US AI governance approaches

---

*Documentation created: October 27, 2025*  
*Training Configuration: NIST AI RMF Transfer Learning from EU AI Act*