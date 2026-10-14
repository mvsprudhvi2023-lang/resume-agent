import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])


async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS FOUND:")
            for tool in tools.tools:
                print(" -", tool.name)

            print("\nmask_pii_text:")
            r = await session.call_tool(
                "mask_pii_text",
                {"text": "Mail hr@company-example.com or call +1 555 123 4567"},
            )
            print(r.content[0].text)

            print("\nskill_match:")
            r = await session.call_tool(
                "skill_match",
                {
                    "candidate_skills": ["Python", "SQL", "LangChain"],
                    "required_skills": ["Python", "SQL", "Power BI"],
                },
            )
            print(r.content[0].text)

            print("\nparse_job:")
            r = await session.call_tool(
                "parse_job",
                {"job_description": "We need an AI Business Analyst with Python, SQL and Power BI."},
            )
            print(r.content[0].text)


asyncio.run(main())