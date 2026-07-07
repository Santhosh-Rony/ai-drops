from dataclasses import dataclass
from typing import Dict, Any, Optional

def trim_text(text: str, max_length: int) -> str:
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    trimmed = text[:max_length]
    last_space = trimmed.rfind(" ")
    if last_space > 0:
        return trimmed[:last_space]
    return trimmed

@dataclass
class ContentBlock:
    title: str # e.g. Tool Name, # Tip 1, # Prompt 1
    point_1: str = "" # Used for Drops
    point_2: str = ""
    point_3: str = ""
    passage: str = "" # Used for Tips/Prompts

    def trim_to_limits(self, is_passage: bool = False):
        if is_passage:
            self.title = trim_text(self.title, 40)
            self.passage = trim_text(self.passage, 200)
        else:
            self.title = trim_text(self.title, 25)
            self.point_1 = trim_text(self.point_1, 60)
            self.point_2 = trim_text(self.point_2, 60)
            self.point_3 = trim_text(self.point_3, 60)

    def validate(self, is_passage: bool = False):
        if not self.title:
            raise ValueError("Block title cannot be empty")
        if is_passage:
            if not self.passage:
                raise ValueError("Block passage cannot be empty for tips/prompts")
        else:
            if not self.point_1:
                raise ValueError("Block point_1 cannot be empty for drops")

@dataclass
class PostContent:
    header: str
    tool_1: ContentBlock
    tool_2: ContentBlock
    tool_3: ContentBlock
    caption: str
    hashtags: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostContent":
        return cls(
            header=data.get("header", "AI DROPS"),
            tool_1=ContentBlock(**data.get("tool_1", {})),
            tool_2=ContentBlock(**data.get("tool_2", {})),
            tool_3=ContentBlock(**data.get("tool_3", {})),
            caption=data.get("caption", ""),
            hashtags=data.get("hashtags", "")
        )

    def trim_to_limits(self, is_passage: bool = False):
        self.tool_1.trim_to_limits(is_passage)
        self.tool_2.trim_to_limits(is_passage)
        self.tool_3.trim_to_limits(is_passage)

    def validate(self, is_passage: bool = False):
        if not self.header:
            raise ValueError("Header cannot be empty")
        self.tool_1.validate(is_passage)
        self.tool_2.validate(is_passage)
        self.tool_3.validate(is_passage)
