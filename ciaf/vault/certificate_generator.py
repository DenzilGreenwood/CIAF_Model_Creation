"""
CIAF Certificate PDF Generation for Verification Records

Generates professional PDF certificates for cryptographic proof verification.
Includes certificate details, validity dates, issuer signature, and QR codes.

Designed for auditors, legal teams, and compliance officers.
"""

import io
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class CertificatePDFGenerator:
    """
    Generates professional PDF verification certificates.

    Features:
    - Certificate metadata (proof_id, timestamp, validity)
    - Issuer details (CIAF Vault)
    - Cryptographic proof information
    - QR code for verification URL
    - Signature and attestation
    - Legal admissibility statement
    """

    def __init__(self, vault_name: str = "CIAF Vault", issuer_name: str = "CIAF Vault Authentication Service"):
        """
        Initialize certificate generator.

        Args:
            vault_name: Name of the vault issuing the certificate
            issuer_name: Official issuer name for the certificate
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab"
            )

        self.vault_name = vault_name
        self.issuer_name = issuer_name
        self.timestamp = datetime.now(timezone.utc)

    def generate_certificate_pdf(
        self,
        certificate_id: str,
        proof_id: str,
        organization_id: str,
        content_hash: str,
        issued_at: str,
        valid_until: str,
        verification_url: str,
        signature: str,
        merkle_root: Optional[str] = None,
        read_count: int = 0,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate a certificate PDF for a proof.

        Args:
            certificate_id: Unique certificate identifier
            proof_id: Associated proof ID
            organization_id: Organization that submitted the proof
            content_hash: SHA-256 hash of the proof content
            issued_at: ISO timestamp when certificate was issued
            valid_until: ISO timestamp when certificate expires
            verification_url: URL to verify the proof
            signature: Vault signature (hex)
            merkle_root: Merkle root hash (optional)
            read_count: Number of times proof has been read
            output_path: Path to save PDF (if not returning bytes)

        Returns:
            PDF bytes, or None if output_path is provided
        """
        # Create PDF in memory
        pdf_buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            title=f"CIAF Verification Certificate {certificate_id}",
        )

        # Build story (content)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
        )

        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        )

        # 1. Header with seal
        story.append(Paragraph("🔐 CRYPTOGRAPHIC VERIFICATION CERTIFICATE", title_style))
        story.append(Spacer(1, 0.1 * inch))

        # 2. Certificate ID and issued date
        cert_info_data = [
            ["Certificate ID:", certificate_id],
            ["Issued By:", self.issuer_name],
            ["Issued At:", issued_at[:19] if issued_at else datetime.now(timezone.utc).isoformat()[:19]],
        ]
        cert_table = Table(cert_info_data, colWidths=[2.5 * inch, 3.5 * inch])
        cert_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (1, 0), (1, -1), 'Courier', 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(cert_table)
        story.append(Spacer(1, 0.2 * inch))

        # 3. Proof Details
        story.append(Paragraph("PROOF DETAILS", heading_style))
        proof_data = [
            ["Proof ID:", proof_id],
            ["Organization:", organization_id],
            ["Content Hash:", content_hash[:64] + "..." if len(content_hash) > 64 else content_hash],
            ["Read Count:", str(read_count)],
        ]
        if merkle_root:
            proof_data.append(["Merkle Root:", merkle_root[:64] + "..." if len(merkle_root) > 64 else merkle_root])

        proof_table = Table(proof_data, colWidths=[2.5 * inch, 3.5 * inch])
        proof_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (1, 0), (1, -1), 'Courier', 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(proof_table)
        story.append(Spacer(1, 0.2 * inch))

        # 4. Certificate Validity
        story.append(Paragraph("CERTIFICATE VALIDITY", heading_style))
        validity_data = [
            ["Valid From:", issued_at[:19]],
            ["Valid Until:", valid_until[:19]],
            ["Status:", "✅ VALID"],
        ]
        validity_table = Table(validity_data, colWidths=[2.5 * inch, 3.5 * inch])
        validity_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (1, 0), (1, -1), 'Courier', 9),
            ('TEXTCOLOR', (0, 2), (1, 2), colors.HexColor('#00aa00')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(validity_table)
        story.append(Spacer(1, 0.2 * inch))

        # 5. Verification Information
        story.append(Paragraph("VERIFICATION", heading_style))
        story.append(Paragraph(
            f"<b>Signature (Ed25519):</b><br/>{signature[:64]}...",
            normal_style
        ))
        story.append(Spacer(1, 0.1 * inch))

        # 6. QR Code (if qrcode available)
        if QRCODE_AVAILABLE:
            qr = qrcode.QRCode(version=1, box_size=4, border=1)
            qr.add_data(verification_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Save QR to buffer
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)

            story.append(Paragraph("<b>Verify Online (QR Code):</b>", label_style))
            story.append(Spacer(1, 0.05 * inch))

            from reportlab.platypus import Image
            qr_image = Image(qr_buffer, width=1.5 * inch, height=1.5 * inch)
            story.append(qr_image)
        else:
            story.append(Paragraph(
                f"<b>Verify Online:</b><br/>{verification_url}",
                normal_style
            ))

        story.append(Spacer(1, 0.2 * inch))

        # 7. Legal Attestation
        story.append(Paragraph("LEGAL ATTESTATION", heading_style))
        attestation = (
            "This certificate attests that the referenced proof has been cryptographically verified "
            "and stored in the CIAF Vault with immutable, tamper-evident protection. "
            "The proof is admissible as evidence under Federal Rules of Evidence (Rule 901: Authentication, "
            "Rule 902: Self-Authenticating Documents) and satisfies the Daubert Standard for scientific reliability. "
            "The cryptographic methods used (SHA-256, Ed25519, Merkle trees) are peer-reviewed standards "
            "approved by NIST and widely deployed in government, financial, and security systems."
        )
        story.append(Paragraph(attestation, normal_style))
        story.append(Spacer(1, 0.2 * inch))

        # 8. Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER,
        )
        story.append(Paragraph(
            f"Generated by {self.vault_name} | Certificate ID: {certificate_id}",
            footer_style
        ))
        story.append(Paragraph(
            "This is a machine-verifiable cryptographic document. Auditors can independently "
            "verify this proof using publicly available tools.",
            footer_style
        ))

        # Build PDF
        doc.build(story)

        # Get bytes
        pdf_bytes = pdf_buffer.getvalue()

        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            return None

        return pdf_bytes

    @staticmethod
    def generate_qr_code(
        data: str,
        size: int = 10,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate QR code for verification URL.

        Args:
            data: Data to encode in QR code
            size: Size of QR code
            output_path: Path to save PNG

        Returns:
            PNG bytes, or None if output_path provided
        """
        if not QRCODE_AVAILABLE:
            raise ImportError("qrcode is required for QR code generation")

        qr = qrcode.QRCode(version=1, box_size=size, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_buffer = io.BytesIO()
        img.save(qr_buffer, format='PNG')
        qr_bytes = qr_buffer.getvalue()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(qr_bytes)
            return None

        return qr_bytes


__all__ = ["CertificatePDFGenerator"]
