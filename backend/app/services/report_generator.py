import os
import asyncio
from pathlib import Path
from typing import Dict, Any
from ..core.config import settings
import logging
import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Service for generating and saving security reports in multiple formats.
    """
    
    def __init__(self):
        self.reports_dir = Path(settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def _generate_filename(self, report_id: int, extension: str) -> str:
        """Generate timestamped filename."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"report_{report_id}_{timestamp}.{extension}"
    
    def save_as_markdown(self, content: str, report_id: int) -> str:
        """
        Save report content as Markdown file.
        
        Args:
            content: Report content in Markdown format
            report_id: Database report ID
            
        Returns:
            Absolute file path of saved report
        """
        filename = self._generate_filename(report_id, "md")
        filepath = self.reports_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved Markdown report to {filepath}")
            return str(filepath.resolve())
        except Exception as e:
            logger.error(f"Failed to save Markdown report: {e}")
            raise
    
    def save_as_pdf(self, content: str, report_id: int, summary: str = "") -> str:
        """
        Save report content as PDF file.
        
        Args:
            content: Report content in Markdown format
            report_id: Database report ID
            summary: Report summary for title
            
        Returns:
            Absolute file path of saved PDF
        """
        try:
            import markdown2
            from weasyprint import HTML, CSS
            
            # Convert Markdown to HTML
            html_content = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
            
            # Create styled HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>AlphaMapping Security Report</title>
                <style>
                    body {{
                        font-family: 'Arial', 'SimSun', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 20px;
                    }}
                    h1 {{
                        color: #00f2ff;
                        border-bottom: 3px solid #00f2ff;
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        color: #0ea5e9;
                        margin-top: 30px;
                    }}
                    h3 {{
                        color: #64748b;
                    }}
                    code {{
                        background-color: #f1f5f9;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Courier New', monospace;
                    }}
                    pre {{
                        background-color: #1e293b;
                        color: #e0f2fe;
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #cbd5e1;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f1f5f9;
                        font-weight: bold;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 40px;
                    }}
                    .footer {{
                        margin-top: 40px;
                        text-align: center;
                        color: #94a3b8;
                        font-size: 12px;
                        border-top: 1px solid #e2e8f0;
                        padding-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🛡️ AlphaMapping Security Report</h1>
                    <p style="color: #64748b;">{summary}</p>
                    <p style="color: #94a3b8; font-size: 12px;">Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                {html_content}
                <div class="footer">
                    <p>AlphaMapping - Mapping the Unknown in Cyberspace</p>
                </div>
            </body>
            </html>
            """
            
            filename = self._generate_filename(report_id, "pdf")
            filepath = self.reports_dir / filename
            
            # Generate PDF
            HTML(string=full_html).write_pdf(filepath)
            
            logger.info(f"Saved PDF report to {filepath}")
            return str(filepath.resolve())
            
        except ImportError:
            logger.error("PDF generation requires 'markdown2' and 'weasyprint' packages")
            raise
        except Exception as e:
            logger.error(f"Failed to save PDF report: {e}")
            raise
    
    def get_report_path(self, filename: str) -> Path:
        """Get full path for a report file."""
        return self.reports_dir / filename
