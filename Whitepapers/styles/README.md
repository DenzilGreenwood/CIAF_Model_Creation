# CIAF Document Styles Package

## Overview

The `ciaf_document_styles.sty` package provides comprehensive styling for all CIAF project documents, ensuring consistency, professionalism, and easy maintenance across the entire documentation suite.

## Features

### 🎨 **Professional Styling**
- CIAF branded color scheme
- Consistent typography and spacing
- Professional headers and footers
- Optimized for A4 paper format

### 📦 **Comprehensive Package Management**
- All necessary LaTeX packages included
- Automatic dependency management
- Version controlled styling
- Easy to update across all documents

### 🎯 **Custom Elements**
- 7 different styled boxes for various content types
- Professional code highlighting
- CIAF-branded section formatting
- Mathematical theorem environments

### 🔧 **Easy Integration**
- Single line import: `\usepackage{styles/ciaf_document_styles}`
- Simple setup commands
- Backward compatible with existing documents

## Installation

1. Place the `ciaf_document_styles.sty` file in your `styles/` directory
2. Include the package in your LaTeX document: `\usepackage{styles/ciaf_document_styles}`
3. Set up your document using the provided commands

## Basic Usage

```latex
\documentclass[12pt,a4paper]{article}

% Load the CIAF styles package
\usepackage{styles/ciaf_document_styles}

% Setup document metadata
\setupdocument{Document Title}{Document Subtitle}{Author Name}{Version}

% Setup header and footer
\setupheaderfooter{Header Title}{Header Subtitle}

\begin{document}
% Your content here
\end{document}
```

## Custom Boxes

### Executive Box
```latex
\begin{executivebox}
Executive summary content, key points, and important highlights.
\end{executivebox}
```

### Value Box
```latex
\begin{valuebox}
Value propositions, benefits, and positive information.
\end{valuebox}
```

### Risk Box
```latex
\begin{riskbox}
Warnings, risks, and important considerations.
\end{riskbox}
```

### Technical Box
```latex
\begin{technicalbox}
Technical specifications and detailed technical information.
\end{technicalbox}
```

### Info Box
```latex
\begin{infobox}
General information and notes.
\end{infobox}
```

### Alert Box
```latex
\begin{alertbox}
Critical alerts and urgent information.
\end{alertbox}
```

### Contact Box
```latex
\begin{contactbox}
Contact information and communication details.
\end{contactbox}
```

## Utility Commands

### Document Setup
```latex
\setupdocument{Title}{Subtitle}{Author}{Version}
```

### Header/Footer Configuration
```latex
% Professional header/footer
\setupheaderfooter{Document Title}{Subtitle}

% Simple header/footer
\setupsimpleheader{Document Title}{Subtitle}
```

### Spacing Commands
```latex
\ciafvspace      % Small vertical space (0.5cm)
\ciafbigspace    % Medium vertical space (1cm)
\ciafhugeSpace   % Large vertical space (2cm)
```

### Professional Tables
```latex
\begin{ciaftable}{lcc}
\textbf{Column 1} & \textbf{Column 2} & \textbf{Column 3} \\
\midrule
Data 1 & Data 2 & Data 3 \\
\end{ciaftable}
```

## Color Scheme

The package defines the complete CIAF color palette:

- **ciafblue**: Primary blue (#2980B9)
- **ciafgray**: Secondary gray (#7F8C8D)
- **ciafdarkblue**: Dark blue (#16435B)
- **ciaflightblue**: Light blue (#AED6F1)
- **ciafgreen**: Success green (#27AE60)
- **ciaforange**: Warning orange (#E67E22)
- **ciafred**: Error red (#E74C3C)

## Code Highlighting

The package automatically configures code highlighting with CIAF colors:

```latex
\begin{lstlisting}[caption={Example Code}]
def example_function():
    """Automatically styled with CIAF colors"""
    return "Professional code formatting"
\end{lstlisting}
```

## Mathematical Environments

CIAF-styled theorem environments:

```latex
\begin{ciafdefinition}
Your definition content here.
\end{ciafdefinition}

\begin{ciaftheorem}
Your theorem content here.
\end{ciaftheorem}

\begin{ciaflemma}
Your lemma content here.
\end{ciaflemma}

\begin{ciafcorollary}
Your corollary content here.
\end{ciafcorollary}
```

## Migration Guide

### From Existing Documents

1. **Remove old package imports**: Remove individual package imports that are now included in the styles package
2. **Replace color definitions**: Remove custom color definitions
3. **Update box definitions**: Replace custom tcolorbox definitions with the new box environments
4. **Add package import**: Add `\usepackage{styles/ciaf_document_styles}` at the top
5. **Set up headers**: Use `\setupheaderfooter{}{}` instead of manual fancyhdr configuration

### Example Migration

**Before:**
```latex
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
% ... many package imports ...
\definecolor{ciafblue}{RGB}{41, 128, 185}
% ... color definitions ...
\newtcolorbox{valuebox}{...}
% ... custom box definitions ...
```

**After:**
```latex
\documentclass[12pt,a4paper]{article}
\usepackage{styles/ciaf_document_styles}
\setupdocument{Title}{Subtitle}{Author}{Version}
\setupheaderfooter{Header}{Subtitle}
```

## Version History

- **v1.0.0** (2025-10-24): Initial release with complete CIAF styling

## Support

For questions or issues with the styles package, please refer to the project documentation or contact the development team.

## License

This styles package is part of the CIAF project and follows the same licensing terms as the main project.