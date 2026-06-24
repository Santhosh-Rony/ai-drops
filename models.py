from dataclasses import dataclass
from typing import Dict, Any

def trim_text(text: str, max_length: int) -> str:
    """
    Trims text to max_length without cutting words in half.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
        
    trimmed = text[:max_length]
    last_space = trimmed.rfind(" ")
    
    # If we found a space, cut there. Otherwise, hard cut to avoid breaking layout.
    if last_space > 0:
        return trimmed[:last_space]
    return trimmed

@dataclass
class ToolContent:
    name: str
    point_1: str
    point_2: str
    point_3: str

    def trim_to_limits(self):
        """Applies length limits to the tool content."""
        self.name = trim_text(self.name, 25)
        self.point_1 = trim_text(self.point_1, 60)
        self.point_2 = trim_text(self.point_2, 60)
        self.point_3 = trim_text(self.point_3, 60)

    def validate(self):
        """Validates that the required fields are present."""
        if not self.name:
            raise ValueError("Tool name cannot be empty")
        if not self.point_1:
            raise ValueError("Tool point_1 cannot be empty")

@dataclass
class PostContent:
    header: str
    tool_1: ToolContent
    tool_2: ToolContent
    tool_3: ToolContent
    caption: str
    hashtags: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostContent":
        return cls(
            header=data.get("header", "AI DROPS"),
            tool_1=ToolContent(**data.get("tool_1", {})),
            tool_2=ToolContent(**data.get("tool_2", {})),
            tool_3=ToolContent(**data.get("tool_3", {})),
            caption=data.get("caption", ""),
            hashtags=data.get("hashtags", "")
        )

    def trim_to_limits(self):
        """Trims all nested tool contents."""
        self.tool_1.trim_to_limits()
        self.tool_2.trim_to_limits()
        self.tool_3.trim_to_limits()

    def validate(self):
        """Validates the entire post content structure."""
        if self.header != "AI DROPS":
            raise ValueError(f"Header must be 'AI DROPS', got '{self.header}'")
        self.tool_1.validate()
        self.tool_2.validate()
        self.tool_3.validate()

