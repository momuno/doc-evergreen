"""Core metadata extraction logic for document analysis."""

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from doc_evergreen.generate.doc_type import DocType, validate_doc_type


@dataclass
class DocumentMetadata:
    """Extracted metadata from existing documentation.

    Attributes:
        document_path: Path relative to repo root
        intent: High-level purpose/goal (1-2 sentences)
        doc_type: Divio quadrant classification (DocType enum)
        confidence: LLM's confidence in classification (high/medium/low)
        reasoning: Brief explanation for the classification
        timestamp: ISO 8601 timestamp when extracted
        llm_model: Model identifier used for extraction
        prompt_used: Full prompt sent to LLM for transparency
        version: doc-evergreen version for compatibility
    """

    document_path: str
    intent: str
    doc_type: DocType
    confidence: str
    reasoning: str
    timestamp: str
    llm_model: str
    prompt_used: str
    version: str = "0.7.0"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "document_path": self.document_path,
            "intent": self.intent,
            "doc_type": self.doc_type.value,  # Convert enum to string
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "llm_model": self.llm_model,
            "prompt_used": self.prompt_used,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentMetadata":
        """Create from dictionary (deserialization)."""
        # Convert doc_type string to DocType enum
        doc_type = validate_doc_type(data["doc_type"])

        return cls(
            version=data.get("version", "0.7.0"),
            document_path=data["document_path"],
            intent=data["intent"],
            doc_type=doc_type,
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            timestamp=data["timestamp"],
            llm_model=data["llm_model"],
            prompt_used=data["prompt_used"],
        )


def _path_to_cache_filename(document_path: str) -> str:
    """Convert document path to cache filename.

    Args:
        document_path: Path like "README.md" or "docs/API.md"

    Returns:
        Cache filename like "README.json" or "docs-API.json"

    Examples:
        >>> _path_to_cache_filename("README.md")
        "README.json"
        >>> _path_to_cache_filename("docs/API.md")
        "docs-API.json"
    """
    # Remove extension (if present)
    path = Path(document_path)
    stem = path.stem
    parent_parts = path.parent.parts

    # Build filename: parent-parts-stem.json
    if parent_parts and parent_parts != (".",):
        # Has parent directories
        filename = "-".join(parent_parts) + "-" + stem + ".json"
    else:
        # Root level
        filename = stem + ".json"

    return filename


def _build_extraction_prompt(document_path: str, content: str) -> str:
    """Build prompt for LLM to extract metadata.

    Args:
        document_path: Path to the document being analyzed
        content: Document content (may be truncated)

    Returns:
        Prompt string for LLM
    """
    # Truncate content if too large (8000 chars captures essence)
    max_content_length = 8000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "\n\n[... content truncated ...]"

    return f"""You are a technical documentation expert analyzing existing documentation.

**Task:** Analyze this document and extract structured metadata.

**Document Path:** {document_path}

**Document Content:**
{content}

---

**Extract the following:**

1. **Intent** (1-2 sentences): What is the high-level purpose/goal of this document? What does it help users accomplish?

2. **Classification**: Which Divio documentation quadrant does this fit?
   • **Tutorial**: Learning-oriented, guides users through getting started, hands-on lessons
   • **How-To**: Goal-oriented, problem-solving guides for specific tasks
   • **Reference**: Information-oriented, technical descriptions, API documentation
   • **Explanation**: Understanding-oriented, clarifies concepts and design decisions

3. **Confidence**: How confident are you in this classification? (high/medium/low)

4. **Reasoning**: Brief explanation (1-2 sentences) for why this classification fits.

**Output Format (JSON only, no markdown):**
{{
  "intent": "Clear 1-2 sentence description",
  "doc_type": "tutorial|howto|reference|explanation",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation for classification"
}}
"""


def _parse_llm_response(response: str) -> dict:
    """Parse LLM response to extract JSON.

    Handles responses that:
    - Are pure JSON
    - Contain JSON wrapped in markdown code blocks
    - Contain JSON with extra text

    Args:
        response: Raw LLM response text

    Returns:
        Parsed dictionary with extracted fields

    Raises:
        ValueError: If JSON cannot be parsed or required fields are missing
    """
    # Try to extract JSON from markdown code blocks first
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_match = re.search(r"(\{.*\})", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response.strip()

    # Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {response[:200]}")

    # Validate required fields
    required_fields = ["intent", "doc_type", "confidence", "reasoning"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' in LLM response: {data}")

    return data


def _create_llm_client():
    """Create LLM client for metadata extraction.

    Returns:
        SimpleLLMClient instance

    Raises:
        ValueError: If API key not found
        ImportError: If anthropic package not installed
    """
    # Simple LLM client wrapper using Anthropic
    class SimpleLLMClient:
        def __init__(self):
            # Get API key from environment (already loaded by CLI)
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                # Fallback to loading from file
                claude_key_path = Path.home() / ".claude" / "api_key.txt"
                if claude_key_path.exists():
                    api_key = claude_key_path.read_text().strip()
                    if "=" in api_key:
                        api_key = api_key.split("=", 1)[1].strip()

            if not api_key:
                raise ValueError("Anthropic API key not found")

            try:
                import anthropic

                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = "claude-sonnet-4-20250514"
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")

        def generate(self, prompt: str, temperature: float = 0.0) -> str:
            """Generate response from Claude."""
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text

    return SimpleLLMClient()


def extract_document_metadata(
    document_path: Path, llm_client=None
) -> DocumentMetadata:
    """Extract metadata from a document using LLM analysis.

    Args:
        document_path: Path to document to analyze
        llm_client: Optional LLM client (for testing). If None, creates default client.

    Returns:
        DocumentMetadata with extracted information

    Raises:
        FileNotFoundError: If document doesn't exist
        ValueError: If LLM response is invalid or doc_type is invalid
    """
    # Read document content
    if not document_path.exists():
        raise FileNotFoundError(f"Document not found: {document_path}")

    content = document_path.read_text(encoding="utf-8")

    # Create LLM client if not provided
    if llm_client is None:
        llm_client = _create_llm_client()

    # Build prompt
    prompt = _build_extraction_prompt(str(document_path), content)

    # Call LLM
    response = llm_client.generate(prompt, temperature=0.0)

    # Parse response
    data = _parse_llm_response(response)

    # Validate doc_type
    doc_type = validate_doc_type(data["doc_type"])

    # Create metadata object
    metadata = DocumentMetadata(
        document_path=str(document_path),
        intent=data["intent"],
        doc_type=doc_type,
        confidence=data["confidence"],
        reasoning=data["reasoning"],
        timestamp=datetime.now(timezone.utc).isoformat(),
        llm_model=llm_client.model,
        prompt_used=prompt,
        version="0.7.0",
    )

    return metadata


def save_metadata(
    metadata: DocumentMetadata, project_root: Path, force: bool = False
) -> Path:
    """Save metadata to cache file.

    Creates cache at: .doc-evergreen/metadata/{filename}.json

    Args:
        metadata: DocumentMetadata to save
        project_root: Project root directory
        force: If True, overwrite existing cache. If False, raise error if exists.

    Returns:
        Path to created cache file

    Raises:
        FileExistsError: If cache already exists and force=False
    """
    # Create cache directory
    cache_dir = project_root / ".doc-evergreen" / "metadata"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate cache filename
    cache_filename = _path_to_cache_filename(metadata.document_path)
    cache_path = cache_dir / cache_filename

    # Check if exists (unless force=True)
    if cache_path.exists() and not force:
        raise FileExistsError(f"Cache already exists: {cache_path}")

    # Write JSON
    cache_path.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")

    return cache_path


def load_metadata(document_path: str, project_root: Path) -> DocumentMetadata | None:
    """Load metadata from cache file.

    Args:
        document_path: Document path (relative to repo root)
        project_root: Project root directory

    Returns:
        DocumentMetadata if cache exists, None otherwise
    """
    # Generate cache filename
    cache_filename = _path_to_cache_filename(document_path)
    cache_path = project_root / ".doc-evergreen" / "metadata" / cache_filename

    # Return None if doesn't exist (not an error)
    if not cache_path.exists():
        return None

    # Load and parse JSON
    data = json.loads(cache_path.read_text(encoding="utf-8"))

    return DocumentMetadata.from_dict(data)
