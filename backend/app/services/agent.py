import openai
from ..core.config import settings
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def translate_nl_to_cseql(self, nl_query: str, platform: str) -> str:
        """
        Translates natural language to Cyberspace Search Engine Query Language (CSEQL).
        """
        system_prompt = f"""
        You are an expert Cyberspace Search Engine specialist. Your goal is to translate Natural Language queries into precise, syntactically correct query strings for the {platform} platform.

        ### Platform Syntax Reference:
        
        **FOFA:**
        - Basic: 'app="Apache"', 'port="80"', 'country="CN"'
        - Logic: '&&', '||', '!='
        - Advanced: 'banner="users"', 'header="nginx"', 'cert="google"', 'icon_hash="-247388890"'
        - Geo: 'region="Zhejiang"', 'city="Hangzhou"'
        
        **ZoomEye:**
        - Basic: 'app:"Apache"', 'port:80', 'country:"CN"'
        - Logic: '+', ' ', '-'
        - Advanced: 'ver:"1.0"', 'os:"linux"', 'service:"http"', 'device:"router"'
        - CIDR: 'cidr:192.168.1.0/24'

        ### Rules:
        1. OUTPUT ONLY THE QUERY STRING. No explanations, no markdown code blocks.
        2. Handle implicit requirements (e.g., "login pages" -> 'body="login"' or 'title="login"').
        3. Optimize for precision to reduce false positives.
        4. If the query is ambiguous, assume the most common security context (e.g., "camera" -> 'app="Hikvision" || app="Dahua"').
        """
        
        user_prompt = f"Natural Language Query: {nl_query}\n\nTarget Platform: {platform}\n\nCSEQL Query String:"
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1 # Low temperature for consistent syntax
            )
            
            query = response.choices[0].message.content.strip()
            # Remove any potential markdown formatting
            query = query.replace("`", "").replace("json", "").strip()
            print(f"cseql is {query}")
            return query
            
        except Exception as e:
            logger.error(f"Error formulating CSEQL: {e}")
            # Fallback for simple cases if LLM fails
            return f'"{nl_query}"'

    def generate_security_report(self, assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a comprehensive security analysis report based on asset data.
        """
        # Optimize context window by selecting key fields
        asset_context = []
        for asset in assets[:50]: # Analyze up to 50 assets for performance
            asset_context.append({
                "ip": asset.get("ip"),
                "port": asset.get("port"),
                "service": asset.get("protocol") or asset.get("server"),
                "product": asset.get("title") or asset.get("server"),
                "geo": asset.get("country")
            })

        assets_str = json.dumps(asset_context, indent=2)
        
        system_prompt = """
        You are a Senior Cyber Threat Intelligence Analyst. Your task is to analyze a list of exposed network assets and generate a professional security assessment report.
        
        ### Analysis Objectives:
        1. **Exposure Assessment**: Identify sensitive services (databases, remote access, IoT).
        2. **Vulnerability Correlation**: Map identified versions to potential CVEs (generic mapping).
        3. **Attack Surface**: Evaluate the attack surface based on open ports and services.
        4. **Geopolitical Context**: Note any unusual geographic distribution.

        ### Output Format:
        Return a valid JSON object with the following structure:
        {
            "summary": "A concise 1-sentence executive summary of the risk findings.",
            "risk_level": "High/Medium/Low",
            "content": "Full report in Markdown format. Use headers (##), lists, and bold text. Include sections: 'Executive Summary', 'Key Findings', 'Risk Analysis', 'Attack Surface', 'Recommended Actions'."
        }
        
        **Risk Level Criteria:**
        - **High**: Remote Code Execution services (RDP, SSH, Telnet) exposed, Database ports (3306, 5432, 6379, 27017) open to internet, End-of-Life software.
        - **Medium**: Web servers with version info, Management interfaces exposed.
        - **Low**: Static web pages, CDN nodes.
        """
        
        user_prompt = f"Analyze these assets:\n{assets_str}"
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM JSON response")
            return {
                "summary": "Analysis generated but format prediction failed.",
                "risk_level": "Medium",
                "content": content if 'content' in locals() else "Error generating report."
            }
        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {
                "summary": "Automated analysis failed due to service error.",
                "risk_level": "Unknown",
                "content": f"## Analysis Error\n\nAn error occurred while communicating with the AI analysis engine: {str(e)}"
            }

    def analyze_single_asset(self, asset: dict) -> dict:
        """
        Analyze a single asset and return security assessment.
        
        Args:
            asset: Dictionary with asset information
            
        Returns:
            Dictionary with analysis results
        """
        try:
            prompt = f"""作为网络安全专家，请对以下单个资产进行安全分析：

资产信息：
- IP地址: {asset.get('ip', 'N/A')}
- 端口: {asset.get('port', 'N/A')}
- 协议: {asset.get('protocol', 'N/A')}
- 服务: {asset.get('server', 'N/A')}
- 标题: {asset.get('title', 'N/A')}
- 域名/主机: {asset.get('domain') or asset.get('host', 'N/A')}
- 国家/城市: {asset.get('country', 'N/A')} / {asset.get('city', 'N/A')}
- 组织: {asset.get('org', 'N/A')}

请提供以下分析：
1. **资产识别**：识别该资产的类型和用途
2. **风险评估**：评估该资产的安全风险等级（高/中/低）
3. **潜在漏洞**：列出可能存在的安全漏洞或弱点
4. **攻击面分析**：分析该资产可能面临的攻击向量
5. **安全建议**：提供具体的安全加固建议

请以JSON格式返回，包含以下字段：
{{
    "asset_type": "资产类型",
    "risk_level": "High|Medium|Low",
    "vulnerabilities": ["漏洞1", "漏洞2"],
    "attack_vectors": ["攻击向量1", "攻击向量2"],
    "recommendations": ["建议1", "建议2"],
    "summary": "简短的风险摘要（50字以内）"
}}"""

            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert specialized in asset security analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            import json
            analysis = json.loads(content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze asset: {e}")
            raise Exception(f"Failed to analyze asset: {str(e)}")
