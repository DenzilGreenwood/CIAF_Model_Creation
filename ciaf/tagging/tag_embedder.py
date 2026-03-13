"""
Tag Embedding for Different Output Types

Embeds output tags into text, images, and structured data.
Supports multiple embedding formats.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

from typing import Dict, Optional, Union, Any, Tuple
import json
import base64
import io

from .output_tag import OutputTag


class TagEmbedder:
    """
    Embeds output tags in different output types.

    Supports:
    - Text: JSON comments, hidden metadata, XML
    - Images: Steganography, metadata
    - Structured: JSON fields
    """

    @staticmethod
    def embed_in_text(
        output_text: str,
        tag: OutputTag,
        format: str = "json_comment",
    ) -> str:
        """
        Embed tag in text output.

        Args:
            output_text: The AI-generated text
            tag: OutputTag to embed
            format: Embedding format
                - "json_comment": Add as comment in JSON
                - "hidden_metadata": Append as metadata field
                - "xml_metadata": Wrap in XML with metadata

        Returns:
            Text with embedded tag
        """
        if format == "json_comment":
            return TagEmbedder._embed_json_comment(output_text, tag)
        elif format == "hidden_metadata":
            return TagEmbedder._embed_hidden_metadata(output_text, tag)
        elif format == "xml_metadata":
            return TagEmbedder._embed_xml_metadata(output_text, tag)
        else:
            raise ValueError(f"Unknown format: {format}")

    @staticmethod
    def _embed_json_comment(output_text: str, tag: OutputTag) -> str:
        """Embed tag as JSON comment."""
        # Create tag header that looks like a comment
        minimal_tag = tag.to_minimal_dict()
        tag_json = json.dumps(minimal_tag, indent=2)

        # Wrap in comment
        header = f"""
<!-- CIAF Output Tag (Do not modify)
{tag_json}
-->
"""
        return header + output_text

    @staticmethod
    def _embed_hidden_metadata(output_text: str, tag: OutputTag) -> str:
        """
        Embed tag as hidden metadata field.

        Uses a metadata section that can be parsed programmatically.
        """
        metadata = {
            "ciaf_metadata": tag.to_minimal_dict(),
        }

        # Append as structured metadata
        separator = "\n\n---\n[METADATA]\n"
        return output_text + separator + json.dumps(metadata, indent=2)

    @staticmethod
    def _embed_xml_metadata(output_text: str, tag: OutputTag) -> str:
        """Embed tag in XML metadata wrapper."""
        minimal_tag = tag.to_minimal_dict()
        tag_xml = "\n    ".join([f"<{k}>{v}</{k}>" for k, v in minimal_tag.items()])

        xml_wrapper = f"""<?xml version="1.0" encoding="UTF-8"?>
<ciaf_output>
    <metadata>
{tag_xml}
    </metadata>
    <content>
{output_text}
    </content>
</ciaf_output>
"""
        return xml_wrapper

    @staticmethod
    def embed_in_image(
        image_bytes: bytes,
        tag: OutputTag,
        include_visual: bool = True,
    ) -> bytes:
        """
        Embed tag in image metadata.

        Args:
            image_bytes: Image binary data
            tag: OutputTag to embed
            include_visual: Add visual watermark footer to image

        Returns:
            Image bytes with embedded tag

        Note:
            This is a simplified version. Production use would require
            PIL/Pillow for proper image handling.
        """
        # For this implementation, we'll append metadata to PNG
        # In production, use PIL to embed in EXIF or as comment

        metadata_json = json.dumps(tag.to_minimal_dict())
        metadata_bytes = metadata_json.encode("utf-8")

        # Simple approach: append JSON as comment in bytes
        # Real implementation would use proper image library
        separator = b"\n\n[CIAF_METADATA_START]\n"
        return image_bytes + separator + metadata_bytes + b"\n[CIAF_METADATA_END]\n"

    @staticmethod
    def embed_in_structured(
        data: Dict[str, Any],
        tag: OutputTag,
        tag_field_name: str = "_ciaf_tag",
    ) -> Dict[str, Any]:
        """
        Embed tag in structured data (dict/JSON).

        Args:
            data: Structured data to embed in
            tag: OutputTag to embed
            tag_field_name: Field name for tag in data

        Returns:
            Data with embedded tag
        """
        # Create copy to avoid modifying original
        embedded = data.copy()

        # Add tag as field
        embedded[tag_field_name] = tag.to_minimal_dict()

        return embedded

    @staticmethod
    def extract_tag_from_text(output_text: str) -> Optional[OutputTag]:
        """
        Extract tag from text output.

        Tries multiple formats in order.

        Returns:
            Extracted OutputTag or None if not found
        """
        # Try JSON comment format
        tag_data = TagEmbedder._extract_json_comment(output_text)
        if tag_data:
            return TagEmbedder._dict_to_tag(tag_data)

        # Try hidden metadata format
        tag_data = TagEmbedder._extract_hidden_metadata(output_text)
        if tag_data:
            return TagEmbedder._dict_to_tag(tag_data)

        # Try XML format
        tag_data = TagEmbedder._extract_xml_metadata(output_text)
        if tag_data:
            return TagEmbedder._dict_to_tag(tag_data)

        return None

    @staticmethod
    def _extract_json_comment(output_text: str) -> Optional[Dict]:
        """Extract tag from JSON comment."""
        if "<!-- CIAF Output Tag" in output_text:
            start = output_text.find("{")
            end = output_text.find("}", start) + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(output_text[start:end])
                except json.JSONDecodeError:
                    pass
        return None

    @staticmethod
    def _extract_hidden_metadata(output_text: str) -> Optional[Dict]:
        """Extract tag from hidden metadata."""
        if "[METADATA]" in output_text:
            start = output_text.find("[METADATA]") + len("[METADATA]")
            remaining = output_text[start:].strip()
            try:
                data = json.loads(remaining)
                return data.get("ciaf_metadata")
            except json.JSONDecodeError:
                pass
        return None

    @staticmethod
    def _extract_xml_metadata(output_text: str) -> Optional[Dict]:
        """Extract tag from XML metadata."""
        if "<ciaf_output>" in output_text and "<metadata>" in output_text:
            start = output_text.find("<metadata>") + len("<metadata>")
            end = output_text.find("</metadata>")
            if start > 0 and end > start:
                metadata_section = output_text[start:end]
                # Simple XML parsing - extract tag_id, etc.
                tag_data = {}
                for field in ["tag_id", "session_id", "output_content_hash", "inference_receipt_id"]:
                    field_start = metadata_section.find(f"<{field}>")
                    field_end = metadata_section.find(f"</{field}>")
                    if field_start >= 0 and field_end > field_start:
                        value = metadata_section[
                            field_start + len(f"<{field}>") : field_end
                        ].strip()
                        tag_data[field] = value
                return tag_data if tag_data else None
        return None

    @staticmethod
    def _dict_to_tag(data: Dict) -> Optional[OutputTag]:
        """Convert dict to OutputTag."""
        try:
            return OutputTag(
                tag_id=data.get("tag_id"),
                session_id=data.get("session_id"),
                output_content_hash=data.get("output_content_hash"),
                inference_receipt_id=data.get("inference_receipt_id"),
                agent_ids=[],  # Not stored in minimal tag
                organization_id="",  # Not stored in minimal tag
                timestamp=data.get("timestamp", ""),
            )
        except (KeyError, TypeError):
            return None

    @staticmethod
    def extract_tag_from_image(image_bytes: bytes) -> Optional[OutputTag]:
        """
        Extract tag from image bytes.

        Looks for appended JSON metadata.
        """
        if b"[CIAF_METADATA_START]" in image_bytes:
            start = image_bytes.find(b"[CIAF_METADATA_START]") + len(
                b"[CIAF_METADATA_START]"
            )
            end = image_bytes.find(b"[CIAF_METADATA_END]")
            if start > 0 and end > start:
                try:
                    metadata_json = image_bytes[start:end].decode("utf-8").strip()
                    data = json.loads(metadata_json)
                    return TagEmbedder._dict_to_tag(data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        return None

    @staticmethod
    def extract_tag_from_structured(
        data: Dict[str, Any],
        tag_field_name: str = "_ciaf_tag",
    ) -> Optional[OutputTag]:
        """
        Extract tag from structured data.

        Args:
            data: Structured data to extract from
            tag_field_name: Field name containing tag

        Returns:
            Extracted OutputTag or None
        """
        if tag_field_name in data:
            tag_data = data[tag_field_name]
            return TagEmbedder._dict_to_tag(tag_data)
        return None
