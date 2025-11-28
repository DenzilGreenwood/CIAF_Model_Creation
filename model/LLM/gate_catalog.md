# CIAF LLM Gate Catalog

Complete reference of all gate types for governed LLM systems.

---

## 1. Data-Level Gates

### 1.1 DatasetLicenseGate

**Purpose**: Validate dataset license compatibility with intended use

**Inputs**:
- `DatasetAnchor` with license information
- `IntendedUseCase` (commercial, research, internal)
- `PolicyBundle` with acceptable licenses

**Evaluation Logic**:
```python
def evaluate(dataset_anchor, use_case, policy_bundle):
    license_spdx = dataset_anchor.license_spdx
    
    # Check if license is in allowed list
    if license_spdx not in policy_bundle.allowed_licenses[use_case]:
        return Decision.DENY(
            reason=f"License {license_spdx} not compatible with {use_case}",
            required_action="Select different dataset or change use case"
        )
    
    # Check for attribution requirements
    if requires_attribution(license_spdx):
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="License requires attribution",
            constraints=["Add attribution to documentation", "Track in model card"]
        )
    
    return Decision.ALLOW(reason="License compatible")
```

**Outcomes**:
- `ALLOW` - License fully compatible
- `ALLOW_WITH_CONSTRAINTS` - Compatible but requires attribution/notices
- `DENY` - License incompatible with use case

**Receipt Generated**: License validation proof with policy references

---

### 1.2 DatasetSafetyScanGate

**Purpose**: Detect harmful content in dataset

**Inputs**:
- `DatasetAnchor`
- Sample percentage (default 10%)
- Toxicity thresholds
- Content policy

**Evaluation Logic**:
```python
def evaluate(dataset_anchor, sample_pct=10, policy):
    samples = dataset_anchor.get_samples(sample_pct)
    
    results = {
        'toxicity': scan_toxicity(samples),
        'hate_speech': scan_hate_speech(samples),
        'violence': scan_violence(samples),
        'self_harm': scan_self_harm(samples),
        'sexual_content': scan_sexual_content(samples)
    }
    
    violations = []
    for category, scores in results.items():
        violation_rate = scores.above_threshold(policy.thresholds[category])
        if violation_rate > policy.max_violation_rates[category]:
            violations.append({
                'category': category,
                'rate': violation_rate,
                'threshold': policy.max_violation_rates[category]
            })
    
    if len(violations) > 0:
        if any(v['rate'] > policy.critical_threshold for v in violations):
            return Decision.DENY(
                reason="Critical safety violations detected",
                violations=violations
            )
        else:
            return Decision.REQUIRE_HUMAN_REVIEW(
                reason="Safety violations require review",
                violations=violations,
                suggested_action="Manual review or apply content filters"
            )
    
    return Decision.ALLOW(reason="No significant safety violations")
```

**Outcomes**:
- `ALLOW` - Content within acceptable limits
- `REQUIRE_HUMAN_REVIEW` - Moderate violations need human judgment
- `DENY` - Critical safety violations

**Receipt Generated**: Safety scan report with violation details

---

### 1.3 PIIRemovalGate

**Purpose**: Detect and handle Personal Identifiable Information

**Inputs**:
- `DatasetAnchor`
- PII detection config
- Redaction policy

**Evaluation Logic**:
```python
def evaluate(dataset_anchor, pii_config, policy):
    pii_scan = detect_pii(dataset_anchor, pii_config)
    
    findings = {
        'names': pii_scan.count('PERSON'),
        'emails': pii_scan.count('EMAIL'),
        'phone_numbers': pii_scan.count('PHONE'),
        'addresses': pii_scan.count('ADDRESS'),
        'ssn': pii_scan.count('SSN'),
        'medical_ids': pii_scan.count('MEDICAL_ID')
    }
    
    if policy.zero_pii_policy:
        if sum(findings.values()) > 0:
            if policy.auto_redact:
                return Decision.ALLOW_WITH_CONSTRAINTS(
                    reason="PII detected - auto-redaction required",
                    constraints=[
                        "Apply PII redaction pipeline",
                        "Create CuratedDatasetAnchor with redacted version"
                    ],
                    findings=findings
                )
            else:
                return Decision.DENY(
                    reason="PII detected - zero-PII policy enforced",
                    findings=findings
                )
    
    # Risk-based thresholds
    if findings['ssn'] > 0 or findings['medical_ids'] > 0:
        return Decision.REQUIRE_HUMAN_REVIEW(
            reason="Sensitive PII detected",
            findings=findings
        )
    
    return Decision.ALLOW(reason="No PII or acceptable levels")
```

**Outcomes**:
- `ALLOW` - No PII or within acceptable limits
- `ALLOW_WITH_CONSTRAINTS` - PII found, auto-redaction required
- `REQUIRE_HUMAN_REVIEW` - Sensitive PII needs review
- `DENY` - PII policy violation

**Receipt Generated**: PII detection report with counts and locations

---

### 1.4 DomainRelevanceGate

**Purpose**: Validate dataset relevance to intended domain

**Inputs**:
- `DatasetAnchor`
- `IntendedDomain` (e.g., "medical", "legal", "customer_service")
- Relevance classifier

**Evaluation Logic**:
```python
def evaluate(dataset_anchor, intended_domain, classifier):
    samples = dataset_anchor.get_samples(5)  # 5% sample
    
    relevance_scores = []
    for sample in samples:
        score = classifier.predict_relevance(sample, intended_domain)
        relevance_scores.append(score)
    
    avg_relevance = np.mean(relevance_scores)
    min_threshold = 0.7
    
    if avg_relevance < min_threshold:
        return Decision.DENY(
            reason=f"Dataset not relevant to {intended_domain}",
            avg_relevance=avg_relevance,
            threshold=min_threshold,
            suggestion="Select dataset with higher domain relevance"
        )
    
    if avg_relevance < 0.85:
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="Moderate relevance - consider filtering",
            avg_relevance=avg_relevance,
            constraints=["Apply domain-specific filtering", "Monitor performance"]
        )
    
    return Decision.ALLOW(
        reason=f"High relevance to {intended_domain}",
        avg_relevance=avg_relevance
    )
```

**Outcomes**:
- `ALLOW` - High domain relevance (>= 0.85)
- `ALLOW_WITH_CONSTRAINTS` - Moderate relevance (0.7-0.85)
- `DENY` - Low relevance (< 0.7)

**Receipt Generated**: Relevance analysis with sample scores

---

## 2. Model-Level Gates

### 2.1 BaseModelLicenseGate

**Purpose**: Validate base model license for intended use

**Inputs**:
- `ModelAnchor` with license info
- `IntendedUseCase`
- `PolicyBundle`

**Evaluation Logic**:
```python
def evaluate(model_anchor, use_case, policy_bundle):
    license = model_anchor.license
    
    # Check license type
    license_info = parse_license(license)
    
    # Llama, Mistral, Qwen, etc. have specific terms
    if "commercial" in use_case.lower():
        if not license_info.allows_commercial:
            return Decision.DENY(
                reason=f"Model license does not allow commercial use",
                license=license
            )
    
    # Check use case restrictions
    restricted_domains = license_info.restricted_domains or []
    if use_case.domain in restricted_domains:
        return Decision.DENY(
            reason=f"License restricts use in {use_case.domain}",
            restricted_domains=restricted_domains
        )
    
    # Check attribution requirements
    constraints = []
    if license_info.requires_attribution:
        constraints.append("Add model attribution to documentation")
    if license_info.requires_share_alike:
        constraints.append("Finetuned model must use compatible license")
    
    if constraints:
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="License compatible with conditions",
            constraints=constraints
        )
    
    return Decision.ALLOW(reason="License fully compatible")
```

**Outcomes**:
- `ALLOW` - License fully compatible
- `ALLOW_WITH_CONSTRAINTS` - Compatible with attribution/sharing requirements
- `DENY` - License incompatible

**Receipt Generated**: License validation with use case compatibility

---

### 2.2 CapabilityRiskGate

**Purpose**: Assess model capabilities against risk profile

**Inputs**:
- `ModelAnchor`
- `RiskProfile` (allowed/disallowed capabilities)
- Model card metadata

**Evaluation Logic**:
```python
def evaluate(model_anchor, risk_profile):
    capabilities = extract_capabilities(model_anchor.model_card)
    
    # Check for disallowed capabilities
    violations = []
    for capability in capabilities:
        if capability in risk_profile.disallowed_capabilities:
            violations.append({
                'capability': capability,
                'reason': risk_profile.disallow_reasons[capability]
            })
    
    if violations:
        return Decision.DENY(
            reason="Model has disallowed capabilities",
            violations=violations
        )
    
    # Check for high-risk capabilities requiring controls
    high_risk_caps = [
        cap for cap in capabilities 
        if cap in risk_profile.high_risk_capabilities
    ]
    
    if high_risk_caps:
        required_controls = []
        for cap in high_risk_caps:
            required_controls.extend(risk_profile.required_controls[cap])
        
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="High-risk capabilities require controls",
            high_risk_capabilities=high_risk_caps,
            constraints=required_controls
        )
    
    return Decision.ALLOW(reason="Capabilities aligned with risk profile")
```

**Outcomes**:
- `ALLOW` - Capabilities fully aligned
- `ALLOW_WITH_CONSTRAINTS` - High-risk capabilities need controls
- `DENY` - Disallowed capabilities present

**Receipt Generated**: Capability assessment with risk analysis

---

### 2.3 TrainingPlanGate

**Purpose**: Validate training configuration before execution

**Inputs**:
- `TrainingConfig`
- `DatasetAnchor`
- `ModelAnchor`
- `PolicyBundle`

**Evaluation Logic**:
```python
def evaluate(training_config, dataset_anchor, model_anchor, policy_bundle):
    checks = []
    
    # 1. Verify dataset and model are approved
    if not dataset_anchor.is_approved():
        return Decision.DENY(
            reason="Dataset not approved through gates",
            dataset_status=dataset_anchor.gate_status
        )
    
    if not model_anchor.is_approved():
        return Decision.DENY(
            reason="Base model not approved through gates",
            model_status=model_anchor.gate_status
        )
    
    # 2. Check hyperparameters against policy
    hp_violations = []
    
    if training_config.max_steps > policy_bundle.max_training_steps:
        hp_violations.append({
            'param': 'max_steps',
            'value': training_config.max_steps,
            'limit': policy_bundle.max_training_steps
        })
    
    if training_config.learning_rate > policy_bundle.max_learning_rate:
        hp_violations.append({
            'param': 'learning_rate',
            'value': training_config.learning_rate,
            'limit': policy_bundle.max_learning_rate
        })
    
    if hp_violations:
        return Decision.DENY(
            reason="Hyperparameters exceed policy limits",
            violations=hp_violations
        )
    
    # 3. Verify evaluation plan exists
    if not training_config.has_evaluation_plan():
        return Decision.DENY(
            reason="No evaluation plan defined",
            required_action="Define evaluation suite and metrics"
        )
    
    # 4. Check for required privacy features (if applicable)
    if policy_bundle.requires_differential_privacy:
        if not training_config.differential_privacy_enabled:
            return Decision.DENY(
                reason="Differential privacy required but not enabled",
                policy_ref=policy_bundle.dp_policy
            )
    
    # 5. Verify reproducibility requirements
    if not training_config.has_random_seed():
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="No random seed set - affects reproducibility",
            constraints=["Set random seed for reproducibility"]
        )
    
    return Decision.ALLOW(reason="Training plan validated")
```

**Outcomes**:
- `ALLOW` - Training plan approved
- `ALLOW_WITH_CONSTRAINTS` - Approved with reproducibility notes
- `DENY` - Policy violations or missing requirements

**Receipt Generated**: Training plan validation with checks performed

---

### 2.4 ReproducibilityGate

**Purpose**: Verify training reproducibility at completion

**Inputs**:
- `TrainingRunAnchor`
- Training artifacts
- Policy requirements

**Evaluation Logic**:
```python
def evaluate(training_run_anchor, artifacts, policy):
    missing_elements = []
    
    # 1. Check for complete config capture
    required_config = [
        'random_seed', 'learning_rate', 'batch_size', 
        'optimizer', 'scheduler', 'gradient_clip_norm',
        'dataset_version', 'model_version'
    ]
    
    for config_item in required_config:
        if config_item not in training_run_anchor.config:
            missing_elements.append(config_item)
    
    # 2. Verify checkpoint hashes
    if not artifacts.has_final_checkpoint_hash():
        missing_elements.append('final_checkpoint_hash')
    
    # 3. Check for training logs
    if not artifacts.has_training_logs():
        missing_elements.append('training_logs')
    
    # 4. Verify dataset and model anchors referenced
    if not training_run_anchor.dataset_anchor_id:
        missing_elements.append('dataset_anchor_id')
    
    if not training_run_anchor.base_model_anchor_id:
        missing_elements.append('base_model_anchor_id')
    
    if missing_elements:
        return Decision.DENY(
            reason="Incomplete reproducibility information",
            missing_elements=missing_elements,
            required_action="Capture missing elements before proceeding"
        )
    
    # 5. Generate reproducibility score
    score = calculate_reproducibility_score(training_run_anchor, artifacts)
    
    if score < policy.min_reproducibility_score:
        return Decision.REQUIRE_HUMAN_REVIEW(
            reason="Low reproducibility score",
            score=score,
            threshold=policy.min_reproducibility_score
        )
    
    return Decision.ALLOW(
        reason="Training run is fully reproducible",
        reproducibility_score=score
    )
```

**Outcomes**:
- `ALLOW` - Fully reproducible
- `REQUIRE_HUMAN_REVIEW` - Borderline reproducibility
- `DENY` - Missing critical reproducibility elements

**Receipt Generated**: Reproducibility validation report

---

## 3. Evaluation-Level Gates

### 3.1 BenchmarkThresholdGate

**Purpose**: Enforce minimum performance requirements

**Inputs**:
- `EvaluationRunReceipt`
- Benchmark results
- Performance thresholds

**Evaluation Logic**:
```python
def evaluate(eval_results, thresholds):
    failures = []
    
    for benchmark_name, result in eval_results.items():
        if benchmark_name not in thresholds:
            continue
        
        threshold = thresholds[benchmark_name]
        
        if result.metric_value < threshold.min_value:
            failures.append({
                'benchmark': benchmark_name,
                'value': result.metric_value,
                'threshold': threshold.min_value,
                'delta': threshold.min_value - result.metric_value
            })
    
    if failures:
        # Categorize severity
        critical_failures = [f for f in failures if f['delta'] > 0.1]
        minor_failures = [f for f in failures if f['delta'] <= 0.1]
        
        if critical_failures:
            return Decision.DENY(
                reason="Critical benchmark failures",
                failures=critical_failures,
                required_action="Retrain or select different model"
            )
        
        if minor_failures:
            return Decision.REQUIRE_HUMAN_REVIEW(
                reason="Minor benchmark failures - review required",
                failures=minor_failures
            )
    
    return Decision.ALLOW(
        reason="All benchmarks meet thresholds",
        results_summary=eval_results.summary()
    )
```

**Outcomes**:
- `ALLOW` - All benchmarks passed
- `REQUIRE_HUMAN_REVIEW` - Minor failures
- `DENY` - Critical failures

**Receipt Generated**: Benchmark results with pass/fail status

---

### 3.2 SafetyEvaluationGate

**Purpose**: Validate model safety through adversarial testing

**Inputs**:
- `CandidateModelAnchor`
- Safety test suite results
- Safety policy

**Evaluation Logic**:
```python
def evaluate(model_anchor, safety_results, policy):
    test_categories = [
        'toxicity', 'bias', 'jailbreak_resistance',
        'harmful_instructions', 'pii_leakage'
    ]
    
    violations = {}
    
    for category in test_categories:
        if category not in safety_results:
            return Decision.DENY(
                reason=f"Missing required safety test: {category}",
                required_action=f"Run {category} safety evaluation"
            )
        
        result = safety_results[category]
        threshold = policy.safety_thresholds[category]
        
        if result.failure_rate > threshold.max_failure_rate:
            violations[category] = {
                'failure_rate': result.failure_rate,
                'threshold': threshold.max_failure_rate,
                'critical': result.critical_failures > 0
            }
    
    if violations:
        critical_violations = {
            k: v for k, v in violations.items() if v['critical']
        }
        
        if critical_violations:
            return Decision.DENY(
                reason="Critical safety violations detected",
                violations=critical_violations,
                required_action="Address critical issues before deployment"
            )
        
        return Decision.REQUIRE_HUMAN_REVIEW(
            reason="Safety violations require review",
            violations=violations,
            suggested_mitigations=generate_mitigations(violations)
        )
    
    return Decision.ALLOW(
        reason="Model passes all safety evaluations",
        safety_score=safety_results.overall_score()
    )
```

**Outcomes**:
- `ALLOW` - All safety tests passed
- `REQUIRE_HUMAN_REVIEW` - Non-critical violations
- `DENY` - Critical safety failures

**Receipt Generated**: Safety evaluation report with test results

---

### 3.3 BiasFairnessGate

**Purpose**: Assess model fairness across demographic groups

**Inputs**:
- Fairness test results
- Protected attributes
- Fairness policy

**Evaluation Logic**:
```python
def evaluate(fairness_results, protected_attrs, policy):
    bias_detected = {}
    
    for attr in protected_attrs:
        if attr not in fairness_results:
            return Decision.DENY(
                reason=f"Missing fairness test for: {attr}",
                required_action=f"Run fairness evaluation for {attr}"
            )
        
        metrics = fairness_results[attr]
        
        # Check demographic parity
        if metrics.demographic_parity_diff > policy.max_parity_diff:
            bias_detected[attr] = {
                'metric': 'demographic_parity',
                'value': metrics.demographic_parity_diff,
                'threshold': policy.max_parity_diff
            }
        
        # Check equalized odds
        if metrics.equalized_odds_diff > policy.max_eq_odds_diff:
            bias_detected[attr] = {
                'metric': 'equalized_odds',
                'value': metrics.equalized_odds_diff,
                'threshold': policy.max_eq_odds_diff
            }
    
    if bias_detected:
        severity = assess_bias_severity(bias_detected)
        
        if severity == 'high':
            return Decision.DENY(
                reason="Significant bias detected",
                bias_findings=bias_detected,
                required_action="Apply bias mitigation techniques"
            )
        
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="Moderate bias detected - requires monitoring",
            bias_findings=bias_detected,
            constraints=[
                "Document bias in model card",
                "Implement runtime bias monitoring",
                "Consider bias mitigation in next version"
            ]
        )
    
    return Decision.ALLOW(
        reason="No significant bias detected",
        fairness_summary=fairness_results.summary()
    )
```

**Outcomes**:
- `ALLOW` - Fairness criteria met
- `ALLOW_WITH_CONSTRAINTS` - Moderate bias, monitoring required
- `DENY` - Significant bias detected

**Receipt Generated**: Fairness analysis report

---

### 3.4 ExplainabilityEvidenceGate

**Purpose**: Ensure adequate model documentation exists

**Inputs**:
- `CandidateModelAnchor`
- Model card
- Documentation requirements

**Evaluation Logic**:
```python
def evaluate(model_anchor, model_card, requirements):
    missing_sections = []
    insufficient_sections = []
    
    # Required model card sections
    required_sections = [
        'model_description', 'intended_use', 'training_data',
        'evaluation_results', 'limitations', 'bias_analysis',
        'ethical_considerations', 'caveats_and_recommendations'
    ]
    
    for section in required_sections:
        if section not in model_card:
            missing_sections.append(section)
        elif len(model_card[section]) < requirements.min_section_length:
            insufficient_sections.append({
                'section': section,
                'length': len(model_card[section]),
                'required': requirements.min_section_length
            })
    
    if missing_sections:
        return Decision.DENY(
            reason="Incomplete model card",
            missing_sections=missing_sections,
            required_action="Complete all required model card sections"
        )
    
    # Check for specific risk disclosures
    if requirements.high_risk_domain:
        risk_disclosures = [
            'failure_modes', 'monitoring_recommendations',
            'human_oversight_requirements'
        ]
        
        missing_risk = [r for r in risk_disclosures if r not in model_card]
        if missing_risk:
            return Decision.DENY(
                reason="High-risk domain requires additional disclosures",
                missing_disclosures=missing_risk
            )
    
    if insufficient_sections:
        return Decision.REQUIRE_HUMAN_REVIEW(
            reason="Some sections need more detail",
            insufficient_sections=insufficient_sections
        )
    
    return Decision.ALLOW(
        reason="Complete and adequate documentation",
        completeness_score=calculate_completeness(model_card)
    )
```

**Outcomes**:
- `ALLOW` - Complete documentation
- `REQUIRE_HUMAN_REVIEW` - Insufficient detail
- `DENY` - Missing required sections

**Receipt Generated**: Documentation completeness assessment

---

## 4. Deployment-Level Gates

### 4.1 DeploymentGate

**Purpose**: Final check before production deployment

**Inputs**:
- `DeploymentCandidateAnchor`
- `DeploymentConfig`
- All upstream gate receipts

**Evaluation Logic**:
```python
def evaluate(candidate_anchor, deployment_config, gate_receipts):
    blockers = []
    
    # 1. Verify all upstream gates passed
    required_gates = [
        'ReleaseReadinessGate', 'SafetyEvaluationGate',
        'BenchmarkThresholdGate', 'ExplainabilityEvidenceGate'
    ]
    
    for gate_name in required_gates:
        if gate_name not in gate_receipts:
            blockers.append({
                'type': 'missing_gate',
                'gate': gate_name,
                'action': f'Run {gate_name} before deployment'
            })
        elif gate_receipts[gate_name].decision != 'APPROVED':
            blockers.append({
                'type': 'gate_not_approved',
                'gate': gate_name,
                'status': gate_receipts[gate_name].decision
            })
    
    # 2. Verify safety stack configured
    if not deployment_config.has_input_filters():
        blockers.append({
            'type': 'missing_safety',
            'component': 'input_filters',
            'action': 'Configure input safety filters'
        })
    
    if not deployment_config.has_output_filters():
        blockers.append({
            'type': 'missing_safety',
            'component': 'output_filters',
            'action': 'Configure output safety filters'
        })
    
    # 3. Verify monitoring configured
    if not deployment_config.has_monitoring():
        blockers.append({
            'type': 'missing_monitoring',
            'action': 'Configure monitoring and alerting'
        })
    
    # 4. Verify rollback plan
    if not deployment_config.has_rollback_plan():
        blockers.append({
            'type': 'missing_rollback',
            'action': 'Define rollback procedure'
        })
    
    if blockers:
        return Decision.DENY(
            reason="Deployment blockers detected",
            blockers=blockers,
            required_action="Resolve all blockers before deployment"
        )
    
    # 5. Check deployment environment risk
    if deployment_config.environment == 'production':
        if not deployment_config.has_canary_deployment():
            return Decision.REQUIRE_HUMAN_REVIEW(
                reason="Production deployment without canary",
                suggestion="Consider canary or blue-green deployment"
            )
    
    return Decision.ALLOW(
        reason="Ready for deployment",
        deployment_checklist=generate_checklist(deployment_config)
    )
```

**Outcomes**:
- `ALLOW` - Ready for deployment
- `REQUIRE_HUMAN_REVIEW` - Missing canary/gradual rollout
- `DENY` - Blockers present

**Receipt Generated**: Deployment readiness report

---

## 5. Runtime-Level Gates

### 5.1 AuthGate

**Purpose**: Authenticate and authorize API requests

**Inputs**:
- API request
- Credentials
- Access control policy

**Evaluation Logic**:
```python
def evaluate(request, credentials, access_policy):
    # 1. Verify API key
    if not verify_api_key(credentials.api_key):
        return Decision.DENY(
            reason="Invalid API key",
            log_security_event=True
        )
    
    # 2. Check tenant/account status
    tenant = get_tenant(credentials.api_key)
    if tenant.status != 'active':
        return Decision.DENY(
            reason=f"Tenant status: {tenant.status}",
            tenant_id=tenant.id
        )
    
    # 3. Verify rate limits
    if exceeds_rate_limit(tenant):
        return Decision.DENY(
            reason="Rate limit exceeded",
            rate_limit_reset=get_reset_time(tenant)
        )
    
    # 4. Check resource access
    requested_model = request.model_id
    if requested_model not in tenant.allowed_models:
        return Decision.DENY(
            reason="Model access not authorized",
            allowed_models=tenant.allowed_models
        )
    
    return Decision.ALLOW(
        reason="Authenticated and authorized",
        tenant_id=tenant.id,
        rate_limit_remaining=get_remaining_requests(tenant)
    )
```

**Outcomes**:
- `ALLOW` - Authenticated and authorized
- `DENY` - Authentication/authorization failure

**Receipt Generated**: Auth event log

---

### 5.2 PromptGate

**Purpose**: Validate input prompts for safety and policy compliance

**Inputs**:
- User prompt
- Prompt policy
- Injection detectors

**Evaluation Logic**:
```python
def evaluate(prompt, policy, detectors):
    violations = []
    
    # 1. Check for prompt injection attempts
    injection_score = detectors.detect_injection(prompt)
    if injection_score > policy.injection_threshold:
        return Decision.DENY(
            reason="Prompt injection detected",
            injection_score=injection_score,
            log_security_event=True
        )
    
    # 2. Check for disallowed topics
    topics = detectors.detect_topics(prompt)
    disallowed = [t for t in topics if t in policy.disallowed_topics]
    if disallowed:
        violations.append({
            'type': 'disallowed_topics',
            'topics': disallowed
        })
    
    # 3. Check for PII in prompt
    pii_detected = detectors.detect_pii(prompt)
    if pii_detected and not policy.allow_pii_in_prompts:
        violations.append({
            'type': 'pii_in_prompt',
            'pii_types': pii_detected
        })
    
    # 4. Check for jailbreak attempts
    jailbreak_score = detectors.detect_jailbreak(prompt)
    if jailbreak_score > policy.jailbreak_threshold:
        violations.append({
            'type': 'jailbreak_attempt',
            'score': jailbreak_score
        })
    
    if violations:
        severity = assess_violation_severity(violations)
        
        if severity == 'high':
            return Decision.DENY(
                reason="High-severity prompt violations",
                violations=violations,
                log_security_event=True
            )
        
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="Low-severity violations - proceed with caution",
            violations=violations,
            constraints=["Enhanced output filtering", "Log for review"]
        )
    
    return Decision.ALLOW(reason="Prompt passes safety checks")
```

**Outcomes**:
- `ALLOW` - Prompt is safe
- `ALLOW_WITH_CONSTRAINTS` - Minor issues, enhanced filtering
- `DENY` - Serious violations detected

**Receipt Generated**: Prompt safety analysis

---

### 5.3 OutputSafetyGate

**Purpose**: Validate model outputs before returning to user

**Inputs**:
- Model output
- Safety policy
- Content classifiers

**Evaluation Logic**:
```python
def evaluate(output, policy, classifiers):
    issues = []
    
    # 1. Toxicity check
    toxicity_score = classifiers.toxicity(output)
    if toxicity_score > policy.toxicity_threshold:
        issues.append({
            'type': 'toxicity',
            'score': toxicity_score,
            'threshold': policy.toxicity_threshold
        })
    
    # 2. PII leakage check
    pii_found = classifiers.detect_pii(output)
    if pii_found:
        issues.append({
            'type': 'pii_leakage',
            'pii_types': pii_found
        })
    
    # 3. Check for harmful content
    harm_categories = classifiers.detect_harm(output)
    if harm_categories:
        issues.append({
            'type': 'harmful_content',
            'categories': harm_categories
        })
    
    # 4. Check for policy violations
    policy_violations = classifiers.detect_policy_violations(output, policy)
    if policy_violations:
        issues.append({
            'type': 'policy_violation',
            'violations': policy_violations
        })
    
    if issues:
        critical_issues = [i for i in issues if is_critical(i)]
        
        if critical_issues:
            return Decision.DENY(
                reason="Critical safety issues in output",
                issues=critical_issues,
                action="Block output, return safe fallback"
            )
        
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="Minor issues detected",
            issues=issues,
            constraints=["Add safety warning", "Log for review"]
        )
    
    return Decision.ALLOW(reason="Output passes safety checks")
```

**Outcomes**:
- `ALLOW` - Output is safe
- `ALLOW_WITH_CONSTRAINTS` - Output with warnings
- `DENY` - Output blocked

**Receipt Generated**: Output safety analysis

---

### 5.4 LoggingGate

**Purpose**: Ensure all required events are logged

**Inputs**:
- Inference session
- Logging policy
- LCM storage

**Evaluation Logic**:
```python
def evaluate(session, policy, lcm_storage):
    required_logs = []
    
    # 1. Check if request/response logged
    if not session.has_request_log():
        required_logs.append('request_log')
    
    if not session.has_response_log():
        required_logs.append('response_log')
    
    # 2. Check gate decisions logged
    if not session.has_gate_decisions():
        required_logs.append('gate_decisions')
    
    # 3. Check performance metrics logged
    if policy.requires_performance_metrics:
        if not session.has_performance_metrics():
            required_logs.append('performance_metrics')
    
    # 4. Verify LCM receipt generated
    if not session.has_lcm_receipt():
        required_logs.append('lcm_receipt')
    
    if required_logs:
        return Decision.DENY(
            reason="Required logging incomplete",
            missing_logs=required_logs,
            action="Complete logging before proceeding"
        )
    
    # 5. Check retention policy applied
    if not session.has_retention_metadata():
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="Logging complete but missing retention metadata",
            constraints=["Add retention policy metadata"]
        )
    
    return Decision.ALLOW(
        reason="All required logging complete",
        lcm_receipt_id=session.lcm_receipt.id
    )
```

**Outcomes**:
- `ALLOW` - Logging complete
- `ALLOW_WITH_CONSTRAINTS` - Missing metadata
- `DENY` - Required logs missing

**Receipt Generated**: Logging compliance report

---

### 5.5 AnomalyGate

**Purpose**: Detect and respond to anomalous usage patterns

**Inputs**:
- Request history
- Anomaly detectors
- Abuse policy

**Evaluation Logic**:
```python
def evaluate(request_history, detectors, policy):
    anomalies = []
    
    # 1. Volume anomalies
    volume_score = detectors.detect_volume_anomaly(request_history)
    if volume_score > policy.volume_threshold:
        anomalies.append({
            'type': 'volume_spike',
            'score': volume_score,
            'threshold': policy.volume_threshold
        })
    
    # 2. Pattern anomalies
    pattern_score = detectors.detect_pattern_anomaly(request_history)
    if pattern_score > policy.pattern_threshold:
        anomalies.append({
            'type': 'unusual_pattern',
            'score': pattern_score
        })
    
    # 3. Repeated failures
    failure_rate = calculate_failure_rate(request_history)
    if failure_rate > policy.max_failure_rate:
        anomalies.append({
            'type': 'high_failure_rate',
            'rate': failure_rate,
            'threshold': policy.max_failure_rate
        })
    
    # 4. Potential abuse indicators
    abuse_indicators = detectors.detect_abuse(request_history)
    if abuse_indicators:
        anomalies.append({
            'type': 'abuse_indicators',
            'indicators': abuse_indicators
        })
    
    if anomalies:
        severity = assess_anomaly_severity(anomalies)
        
        if severity == 'critical':
            return Decision.DENY(
                reason="Critical anomalies detected - possible abuse",
                anomalies=anomalies,
                action="Temporarily suspend access, investigate",
                alert_security_team=True
            )
        
        if severity == 'high':
            return Decision.ALLOW_WITH_CONSTRAINTS(
                reason="Significant anomalies detected",
                anomalies=anomalies,
                constraints=["Rate limit reduction", "Enhanced monitoring"]
            )
        
        return Decision.ALLOW_WITH_CONSTRAINTS(
            reason="Minor anomalies - monitoring",
            anomalies=anomalies,
            constraints=["Increased logging"]
        )
    
    return Decision.ALLOW(reason="No anomalies detected")
```

**Outcomes**:
- `ALLOW` - Normal usage
- `ALLOW_WITH_CONSTRAINTS` - Anomalies detected, enhanced monitoring
- `DENY` - Critical anomalies, possible abuse

**Receipt Generated**: Anomaly detection report

---

## 6. Governance-Level Gates

### 6.1 ComplianceScopeGate

**Purpose**: Validate use case against regulatory requirements

**Inputs**:
- Use case description
- Regulatory frameworks
- Compliance mappings

**Evaluation Logic**:
```python
def evaluate(use_case, frameworks, mappings):
    applicable_regs = determine_applicable_regulations(
        use_case.domain,
        use_case.geography,
        use_case.data_types
    )
    
    compliance_gaps = []
    
    for regulation in applicable_regs:
        requirements = frameworks[regulation].requirements
        
        for requirement in requirements:
            if not is_satisfied(requirement, use_case, mappings):
                compliance_gaps.append({
                    'regulation': regulation,
                    'requirement': requirement.id,
                    'description': requirement.description,
                    'needed_controls': requirement.controls
                })
    
    if compliance_gaps:
        critical_gaps = [g for g in compliance_gaps if g['requirement'].critical]
        
        if critical_gaps:
            return Decision.DENY(
                reason="Critical compliance gaps identified",
                gaps=critical_gaps,
                required_action="Implement required controls before proceeding"
            )
        
        return Decision.REQUIRE_HUMAN_REVIEW(
            reason="Non-critical compliance gaps require review",
            gaps=compliance_gaps,
            suggested_actions=generate_remediation_plan(compliance_gaps)
        )
    
    return Decision.ALLOW(
        reason="Use case complies with all applicable regulations",
        applicable_regulations=applicable_regs,
        compliance_evidence=generate_evidence_pack(use_case, mappings)
    )
```

**Outcomes**:
- `ALLOW` - Fully compliant
- `REQUIRE_HUMAN_REVIEW` - Minor gaps
- `DENY` - Critical compliance gaps

**Receipt Generated**: Compliance analysis report

---

### 6.2 HumanOversightGate

**Purpose**: Require human approval for high-risk decisions

**Inputs**:
- Decision context
- Risk level
- Approval policy

**Evaluation Logic**:
```python
def evaluate(context, risk_level, policy):
    # Determine if human oversight required
    requires_approval = (
        risk_level >= policy.human_oversight_threshold or
        context.deployment_environment == 'production' and context.is_first_deployment or
        context.has_significant_changes or
        context.affects_high_risk_domain
    )
    
    if not requires_approval:
        return Decision.ALLOW(
            reason="Human oversight not required for this risk level"
        )
    
    # Check if approval already obtained
    if context.has_approval():
        approval = context.get_approval()
        
        # Verify approval is valid
        if approval.is_expired():
            return Decision.REQUIRE_HUMAN_REVIEW(
                reason="Previous approval has expired",
                expired_approval=approval,
                action="Obtain fresh approval"
            )
        
        if not approval.covers_current_scope(context):
            return Decision.REQUIRE_HUMAN_REVIEW(
                reason="Approval scope changed",
                action="Obtain approval for updated scope"
            )
        
        return Decision.ALLOW(
            reason="Valid human approval on record",
            approval_id=approval.id,
            approver=approval.approver
        )
    
    # No approval yet - request it
    return Decision.REQUIRE_HUMAN_REVIEW(
        reason=f"Human oversight required for risk level {risk_level}",
        required_approvers=policy.get_required_approvers(risk_level),
        approval_context=generate_approval_request(context),
        action="Obtain approval from designated reviewers"
    )
```

**Outcomes**:
- `ALLOW` - Approval obtained or not required
- `REQUIRE_HUMAN_REVIEW` - Awaiting approval

**Receipt Generated**: Approval status record

---

### 6.3 AuditReadinessGate

**Purpose**: Verify sufficient evidence exists for audits

**Inputs**:
- System context
- Audit requirements
- Evidence store

**Evaluation Logic**:
```python
def evaluate(system_context, audit_reqs, evidence_store):
    missing_evidence = []
    
    # Required evidence types
    required_evidence = [
        'dataset_lineage', 'model_lineage', 'training_logs',
        'evaluation_results', 'gate_decisions', 'deployment_configs',
        'runtime_logs', 'incident_reports', 'policy_versions'
    ]
    
    for evidence_type in required_evidence:
        if not evidence_store.has_evidence(evidence_type):
            missing_evidence.append(evidence_type)
    
    if missing_evidence:
        return Decision.DENY(
            reason="Insufficient evidence for audit",
            missing_evidence=missing_evidence,
            required_action="Generate and store required evidence"
        )
    
    # Check evidence quality
    quality_issues = []
    for evidence_type in required_evidence:
        evidence = evidence_store.get_evidence(evidence_type)
        
        # Verify cryptographic receipts
        if not evidence.has_valid_receipt():
            quality_issues.append({
                'evidence_type': evidence_type,
                'issue': 'missing_or_invalid_receipt'
            })
        
        # Check completeness
        if not evidence.is_complete():
            quality_issues.append({
                'evidence_type': evidence_type,
                'issue': 'incomplete_evidence'
            })
        
        # Verify retention compliance
        if not evidence.meets_retention_requirements():
            quality_issues.append({
                'evidence_type': evidence_type,
                'issue': 'retention_violation'
            })
    
    if quality_issues:
        return Decision.REQUIRE_HUMAN_REVIEW(
            reason="Evidence quality issues detected",
            issues=quality_issues,
            action="Review and address quality issues"
        )
    
    # Generate audit evidence pack
    evidence_pack = generate_audit_pack(evidence_store, audit_reqs)
    
    return Decision.ALLOW(
        reason="Audit-ready - complete evidence available",
        evidence_pack_id=evidence_pack.id,
        evidence_summary=evidence_pack.summary()
    )
```

**Outcomes**:
- `ALLOW` - Audit-ready
- `REQUIRE_HUMAN_REVIEW` - Quality issues
- `DENY` - Missing evidence

**Receipt Generated**: Audit readiness report

---

## Gate Composition and Orchestration

Gates can be composed and orchestrated:

### Sequential Gates
```python
pipeline = GatePipeline([
    DatasetLicenseGate(),
    DatasetSafetyScanGate(),
    PIIRemovalGate(),
    DomainRelevanceGate()
])

result = pipeline.execute(dataset_anchor, policy_bundle)
```

### Parallel Gates
```python
parallel_gates = ParallelGateGroup([
    BenchmarkThresholdGate(),
    SafetyEvaluationGate(),
    BiasFairnessGate()
])

results = parallel_gates.execute_all(candidate_model)
```

### Conditional Gates
```python
conditional = ConditionalGate(
    condition=lambda ctx: ctx.deployment_env == 'production',
    gate_if_true=HumanOversightGate(),
    gate_if_false=AutomatedDeploymentGate()
)

result = conditional.execute(deployment_context)
```

---

## Summary

This catalog provides **25 gates** covering all stages of the LLM lifecycle:

- **4 Data-Level Gates** - Dataset validation and curation
- **4 Model-Level Gates** - Model selection and training validation
- **4 Evaluation-Level Gates** - Performance and safety verification
- **1 Deployment-Level Gate** - Production readiness
- **5 Runtime-Level Gates** - Operational safety and monitoring
- **3 Governance-Level Gates** - Compliance and oversight

Each gate:
- Has clear inputs and outputs
- Follows consistent decision model (ALLOW/DENY/REQUIRE_HUMAN_REVIEW/ALLOW_WITH_CONSTRAINTS)
- Generates cryptographic receipts
- References applicable policies
- Provides actionable feedback

Gates are composable, allowing flexible orchestration for different risk profiles and regulatory requirements.
