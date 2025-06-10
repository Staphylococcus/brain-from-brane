# Abstraction Altitude Indicators

## Visual Indicators for Document Headers

To help readers quickly identify the abstraction altitude of any document, use these standardized indicators:

### High Altitude (Overview/Panoramic)
```markdown
# 🔭 Document Title
*High Altitude Overview*

or 

📍 **Altitude**: High (10,000+ feet) - Panoramic Overview
```

### Medium Altitude (Conceptual/Exploratory)
```markdown
# 🔍 Document Title
*Medium Altitude Exploration*

or

📍 **Altitude**: Medium (1,000-10,000 feet) - Conceptual Exploration
```

### Low Altitude (Detailed/Technical)
```markdown
# ⚙️ Document Title
*Low Altitude Analysis*

or

📍 **Altitude**: Low (0-1,000 feet) - Detailed Analysis
```

## Navigation Integration with Automated System

The project uses `generate_nav.py` to automatically create navigation footers. Altitude indicators should **complement**, not replace, this automated navigation.

### Header-Based Altitude Navigation
Place altitude context in document headers (above automated footers):

```markdown
⬆️ **Context**: Higher Level Concept (../parent-document.md) <!-- Example placeholder -->
⬇️ **Explore Deeper**: 
- Specific Mechanism (sub-section-a.md) <!-- Example placeholder -->
- Detailed Application (sub-section-b.md) <!-- Example placeholder -->
```

### Altitude-Enhanced Automated Navigation
The navigation script could be enhanced to include altitude awareness in footers:

```markdown
---
🔭 Previous: Higher Level Overview (prev-doc.md) | Home: README.md (../../README.md) | Next: Related Concept (next-doc.md) <!-- Example placeholder navigation -->
```

## Section Indicators Within Documents

For mixed-altitude documents, use these indicators for individual sections:

```markdown
### 🔭 High-Level Overview
*Quick orientation and key takeaways*

### 🔍 Detailed Exploration  
*Comprehensive analysis and examples*

### ⚙️ Technical Implementation
*Precise specifications and protocols*
```

## Document Header Template

Since automated navigation handles footers, focus altitude indicators in headers:

```markdown
# ⚙️ Document Title
*Low Altitude Analysis*

📍 **Altitude**: Low (0-1,000 feet) - Detailed Analysis  
👥 **Primary Audience**: Researchers, practitioners, specialists  
⬆️ **Context**: This analysis is part of Parent Concept (../parent-doc.md) <!-- Example placeholder -->

⬇️ **Explore Deeper**: 
- Statistical Validation (validation.md) <!-- Example placeholder -->
- Implementation Guide (implementation.md) <!-- Example placeholder -->

---

## Overview
Your content begins here...

<!-- Automated navigation footer will be added by generate_nav.py -->
```

## Audience Indicators

```markdown
👥 **Primary Audience**: General readers, executives, newcomers
🎓 **Primary Audience**: Students, researchers, practitioners  
🔬 **Primary Audience**: Specialists, implementers, technical analysts
```

## Implementation Notes

1. **Consistency**: Use these indicators consistently across all framework documents
2. **Optional**: These are suggested standards—adapt as needed for specific contexts
3. **Progressive Rollout**: Can be implemented gradually across existing documents
4. **Accessibility**: Ensure indicators don't interfere with screen readers or accessibility tools

## Example Implementation

```markdown
# ⚙️ Bio-Informational Complex Assessment Protocol
*Low Altitude Analysis*

📍 **Altitude**: Low (0-1,000 feet) - Detailed Analysis  
👥 **Primary Audience**: Researchers, practitioners, assessment specialists  
⬆️ **Context**: Competitive Dynamics (../5-competitive-dynamics.md) > BIC Overview (5e-bio-informational-complex.md) <!-- Example placeholders -->

## Overview
This document provides detailed assessment protocols for identifying and analyzing Bio-Informational Complexes...

⬇️ **Explore Deeper**: 
- Statistical Validation (assessment-validation.md) <!-- Example placeholder -->
- Cross-Cultural Applications (cross-cultural-bic.md) <!-- Example placeholder -->
```

This system provides clear visual cues while maintaining document readability and professional appearance.
