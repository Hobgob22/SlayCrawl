from typing import Union, Dict, List
from .models import ScrapedData

class Formatter:
    @staticmethod
    def to_json(data: Union[ScrapedData, List[ScrapedData]]) -> Union[Dict, List[Dict]]:
        if isinstance(data, list):
            return [item.dict() for item in data]
        return data.dict()

    @staticmethod
    def to_markdown(data: Union[ScrapedData, List[ScrapedData]]) -> str:
        if isinstance(data, list):
            return "\n\n---\n\n".join([Formatter._single_to_markdown(item) for item in data])
        return Formatter._single_to_markdown(data)

    @staticmethod
    def _single_to_markdown(data: ScrapedData) -> str:
        md = f"# {data.title}\n\n"
        
        # Add metadata section
        if data.metadata:
            md += "## Metadata\n\n"
            for key, value in data.metadata.items():
                if value:
                    md += f"- **{key}**: {value}\n"
            md += "\n"

        # Add content section
        md += "## Content\n\n"
        md += data.content + "\n\n"

        # Add source URL
        md += f"\n*Source: [{data.url}]({data.url})*\n"
        
        return md

    @staticmethod
    def format_output(data: Union[ScrapedData, List[ScrapedData]], format_type: str = "json") -> Union[Dict, List[Dict], str]:
        if format_type == "markdown":
            return Formatter.to_markdown(data)
        return Formatter.to_json(data)
