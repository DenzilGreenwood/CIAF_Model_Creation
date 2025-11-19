# CIAF License Migration Summary
## Apache 2.0 → Business Source License 1.1 (BUSL-1.1)

**Date:** November 19, 2025  
**Author:** Denzil James Greenwood  
**Status:** ✅ COMPLETE

---

## Executive Summary

CIAF has successfully migrated from Apache License 2.0 to a **dual-license structure** using Business Source License 1.1 (BUSL-1.1) as the default license, with commercial licensing available for production/enterprise use.

This strategic change balances **research accessibility** with **commercial protection**, following the proven model used by HashiCorp, MariaDB, Couchbase, Sentry, and Elastic.

---

## What Changed

### 1. License Files
- ✅ **LICENSE** - Replaced Apache 2.0 with comprehensive BUSL-1.1 terms
- ✅ **LICENSE.COMMERCIAL** - New commercial license agreement with tiered pricing

### 2. Core Documentation
- ✅ **README.md** - Updated with dual-license explanation and commercial license information
  - License badges updated (Apache 2.0 → BUSL-1.1)
  - New "Dual Licensing Model" section with clear use case guidance
  - Commercial license contact information and pricing tiers
  - "Why This Model?" rationale

### 3. Package Metadata
- ✅ **pyproject.toml** - Updated license metadata
  - Changed `license = {text = "Apache-2.0"}` → `license = {text = "BUSL-1.1"}`
  - Updated classifier from "License :: OSI Approved :: Apache Software License" → "License :: Other/Proprietary License"

---

## License Structure

### BUSL-1.1 (Default License) - Non-Commercial Use

**✅ ALLOWED:**
- ✅ Academic research and scholarly study
- ✅ Personal learning and experimentation
- ✅ 90-day production evaluation
- ✅ Open source contributions (PRs, bug fixes)
- ✅ Educational use (courses, tutorials)
- ✅ Internal testing and development

**❌ PROHIBITED (without commercial license):**
- ❌ Offering CIAF as a commercial service (SaaS, hosted solutions)
- ❌ Integrating CIAF into revenue-generating products
- ❌ Production deployments beyond 90-day evaluation period
- ❌ Creating competing commercial AI governance platforms
- ❌ Distributing CIAF as part of a paid product/service

**🔄 AUTOMATIC CONVERSION:**
- **Change Date:** January 1, 2029
- **Change License:** Apache License 2.0
- After 4 years, all BUSL-1.1 restrictions automatically lift and the code becomes fully open source under Apache 2.0

### Commercial License - Enterprise Use

**Licensing Tiers:**

1. **STARTUP LICENSE** - $5,000/year
   - Up to 10 production deployments
   - Standard support (24-48 hour response)
   - Email support
   - Basic security patches

2. **PROFESSIONAL LICENSE** - $25,000/year
   - Unlimited production deployments (single organization)
   - Priority support (8-hour response)
   - Advanced security features
   - Slack/Teams support
   - Quarterly business reviews

3. **ENTERPRISE LICENSE** - Custom Pricing
   - Unlimited deployments across organization
   - Premium 24/7 support (2-hour critical response)
   - Dedicated customer success manager
   - Custom feature development
   - Legal indemnification
   - Custom SLAs

4. **OEM/RESELLER LICENSE** - Custom Pricing
   - Rights to embed in third-party products
   - White-label options
   - Reseller and distribution rights
   - Revenue sharing models

**Contact:** licensing@cognitiveinsight.ai

---

## Business Rationale

### Why BUSL-1.1?

**1. Research-Friendly**
- Academic institutions can freely use CIAF without restrictions
- Students and researchers have unrestricted access
- Open source community can contribute without legal concerns

**2. Commercial Protection**
- Prevents cloud providers from offering CIAF as a competing service
- Protects against "strip mining" (taking the code without contributing back)
- Creates revenue stream to fund continued development and maintenance

**3. Time-Limited Monopoly**
- Automatic Apache 2.0 conversion after 4 years ensures eventual full open source
- Balances commercial interests with long-term community benefit
- Provides certainty for users about future licensing

**4. Proven Model**
- Used successfully by billion-dollar companies:
  - **HashiCorp:** Terraform, Vault, Consul, Nomad
  - **MariaDB:** MaxScale
  - **Couchbase:** Couchbase Server
  - **Sentry:** Sentry (error tracking)
  - **Elastic:** Elasticsearch, Kibana (previous licensing)

**5. Competitive Advantage**
- Differentiates CIAF from generic open source alternatives
- Creates sustainable business model for long-term development
- Enables enterprise-grade support and SLAs

### What Problems Does This Solve?

**Old Apache 2.0 License:**
- ❌ No commercial protection
- ❌ Anyone could take CIAF, rebrand it, and sell it as a service
- ❌ No revenue mechanism to fund development
- ❌ Difficult to justify enterprise investment without guaranteed support

**New BUSL-1.1 Dual-License:**
- ✅ Research community maintains full access
- ✅ Commercial use requires paid license (revenue for development)
- ✅ Legal protection against competing services
- ✅ Enterprise customers get guaranteed support and SLAs
- ✅ Automatic open source conversion ensures long-term community benefit

---

## Impact Analysis

### Who This Affects

**✅ NO IMPACT (continue as before):**
- Academic researchers
- Students learning AI governance
- Personal projects and experimentation
- Open source contributors
- Evaluation and proof-of-concept testing (≤90 days)

**📋 REQUIRES COMMERCIAL LICENSE:**
- Startups using CIAF in production products
- Enterprises with revenue-generating AI systems
- SaaS providers offering CIAF-based services
- Systems integrators deploying CIAF for clients
- Production deployments beyond 90-day evaluation

**💰 BUSINESS OPPORTUNITIES:**
- Enables sustainable funding for CIAF development
- Creates clear path for enterprise adoption
- Supports dedicated customer success and support teams
- Funds continued innovation in AI governance

---

## Technical Implementation

### Files Modified

1. **LICENSE** (173 lines)
   - Complete BUSL-1.1 license text
   - Licensor: Denzil James Greenwood / CognitiveInsight.ai
   - Change Date: January 1, 2029
   - Change License: Apache 2.0
   - Additional Use Grant for research/evaluation
   - Prohibited commercial uses clearly defined

2. **LICENSE.COMMERCIAL** (NEW - 200+ lines)
   - Commercial license agreement template
   - Four licensing tiers with pricing
   - Support SLAs and benefits
   - Warranties and indemnification
   - Payment terms and conditions
   - Contact information for licensing inquiries

3. **README.md**
   - Updated license badges (Apache 2.0 → BUSL-1.1)
   - New "Dual Licensing Model" section (comprehensive)
   - Commercial license contact information
   - Pricing tier overview
   - Rationale for dual-license structure
   - Updated footer license section

4. **pyproject.toml**
   - Changed `license = {text = "Apache-2.0"}` → `license = {text = "BUSL-1.1"}`
   - Updated classifier: "License :: OSI Approved :: Apache Software License" → "License :: Other/Proprietary License"

### No Breaking Changes

- ✅ Existing research/academic users: **No action required**
- ✅ GitHub repository access: **Unchanged**
- ✅ Documentation and examples: **Remain freely available**
- ✅ Open source contributions: **Still welcome**

### Action Required for Commercial Users

If you are currently using CIAF in production for commercial purposes:

1. **Evaluate your use case** against BUSL-1.1 terms
2. **Determine if you need a commercial license** (revenue-generating deployments, SaaS, production use >90 days)
3. **Contact licensing team:** licensing@cognitiveinsight.ai
4. **Choose appropriate tier:** Startup ($5K), Professional ($25K), Enterprise (custom)
5. **Sign commercial license agreement** before production deployment

---

## Comparison to Other Models

### Why BUSL-1.1 vs. Other Licenses?

| License Model | Research Use | Commercial Protection | Automatic Open Source | Industry Adoption |
|---------------|--------------|----------------------|----------------------|-------------------|
| **Apache 2.0** | ✅ Free | ❌ None | ✅ Already open | ✅ Very high |
| **BUSL-1.1** | ✅ Free | ✅ Strong (4 years) | ✅ After change date | ✅ Growing (HashiCorp, etc.) |
| **GPL/AGPL** | ✅ Free | ⚠️ Copyleft (limited) | ✅ Already open | ⚠️ Enterprise concerns |
| **Proprietary** | ❌ Restricted | ✅ Strong | ❌ Never | ⚠️ Adoption barrier |
| **Fair Source** | ✅ Free (limited) | ⚠️ Weak | ❌ Manual decision | ⚠️ Limited adoption |

**BUSL-1.1 Advantages:**
- ✅ Best balance of research access + commercial protection
- ✅ Proven at scale (billion-dollar companies)
- ✅ Automatic open source conversion (no perpetual lock-in)
- ✅ Clear terms (less ambiguity than copyleft)
- ✅ VC-friendly (enables commercial licensing revenue)

---

## Communication Strategy

### Internal Messaging
- **CIAF remains research-friendly** - academic and personal use unchanged
- **Commercial use now requires license** - creates sustainable funding
- **Automatic Apache 2.0 conversion** - long-term open source guarantee
- **Proven industry model** - used by HashiCorp, MariaDB, Couchbase

### External Messaging
- **Announcement:** "CIAF Adopts Dual-License Model for Sustainable Development"
- **Key Points:**
  - Research and academic use remains free and unrestricted
  - Commercial licensing funds continued innovation and enterprise support
  - Automatic Apache 2.0 conversion on January 1, 2029
  - Following proven model used by industry leaders

### FAQ

**Q: Can I still use CIAF for research?**  
A: Yes! Academic research, personal projects, and evaluation remain completely free.

**Q: Do I need a commercial license for a startup?**  
A: If you're generating revenue from CIAF-based products/services, yes. If purely internal R&D, no.

**Q: What happens after January 1, 2029?**  
A: CIAF automatically converts to Apache 2.0 - fully open source with no restrictions.

**Q: Can I contribute to CIAF as an open source project?**  
A: Absolutely! Contributions via GitHub are encouraged and fall under the Additional Use Grant.

**Q: How much does a commercial license cost?**  
A: Startup tier: $5K/year, Professional: $25K/year, Enterprise: Custom pricing. Contact licensing@cognitiveinsight.ai

**Q: Can I evaluate CIAF in production before licensing?**  
A: Yes, 90-day evaluation period is included in BUSL-1.1 Additional Use Grant.

---

## Next Steps

### Immediate Actions ✅ COMPLETE
- ✅ Replace LICENSE file with BUSL-1.1
- ✅ Create LICENSE.COMMERCIAL with commercial terms
- ✅ Update README.md with dual-license explanation
- ✅ Update pyproject.toml license metadata

### Near-Term Actions 🔄 RECOMMENDED
- 🔄 Add license headers to source files (optional but recommended)
  - Recommended header: `# Licensed under BUSL-1.1 — non-commercial research use only`
- 🔄 Update contribution guidelines (CONTRIBUTING.md) with license implications
- 🔄 Create pricing page on cognitiveinsight.ai website
- 🔄 Prepare commercial license sales process and contracts

### Long-Term Actions 🎯 PLANNED
- 🎯 Monitor license compliance and commercial inquiries
- 🎯 Track automatic Apache 2.0 conversion date (January 1, 2029)
- 🎯 Review licensing terms annually and adjust pricing as needed
- 🎯 Consider enterprise partnerships and OEM agreements

---

## References

### BUSL-1.1 Specification
- **Official Text:** https://mariadb.com/bsl11/
- **FAQ:** https://mariadb.com/bsl-faq-mariadb/
- **Adoption Examples:** HashiCorp Blog (Terraform licensing change)

### Industry Precedents
- **HashiCorp:** Terraform, Vault licensing change (2023)
- **Elastic:** Elasticsearch licensing (previous BUSL implementation)
- **MariaDB:** MaxScale licensing (original BUSL adopter)
- **Couchbase:** Couchbase Server licensing

### Legal Resources
- Business Source License 1.1 full text: LICENSE file
- Commercial License Agreement: LICENSE.COMMERCIAL file
- Contact for legal inquiries: licensing@cognitiveinsight.ai

---

## Conclusion

The migration to BUSL-1.1 dual-license structure positions CIAF for **sustainable commercial success** while maintaining its commitment to **research accessibility** and **eventual full open source status**.

This proven licensing model:
- ✅ Protects intellectual property and investment
- ✅ Enables commercial revenue for continued development
- ✅ Maintains research community access
- ✅ Guarantees future open source conversion
- ✅ Follows successful industry precedents

**Result:** CIAF can grow as a sustainable business while serving the research community and ensuring long-term open source benefit.

---

**Migration Completed:** November 19, 2025  
**Contact:** licensing@cognitiveinsight.ai  
**Documentation:** See LICENSE, LICENSE.COMMERCIAL, and README.md for complete details

---

© 2025 Denzil James Greenwood. All rights reserved.  
Cognitive Insight™ and LCM™ are trademarks of Denzil James Greenwood.
