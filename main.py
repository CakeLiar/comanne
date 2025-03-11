from typing import Union
import openai
from pydantic import Field

import json
import requests


from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase

from tools.searxng_search import (
    SearxNGSearchTool,
    SearxNGSearchToolConfig,
    SearxNGSearchToolInputSchema,
    SearxNGSearchToolOutputSchema,
)

from tools.diagnosis import (
    DiagnosisTool,
    DiagnosisToolConfig,
    DiagnosisToolInputSchema,
    DiagnosisToolOutputSchema,
)

from lib.schemata.ioschemas import *
from lib.context.context import *

import instructor

from dotenv import load_dotenv
load_dotenv()

#######################
# AGENT CONFIGURATION #
#######################
class DiagnosticAgentConfig(BaseAgentConfig):
    """Configuration for the Diagnostic Agent."""

    searxng_config: SearxNGSearchToolConfig


######################
#   DIAGNOSIS AGENT  #
######################

diagnosis_agent = BaseAgent(
    BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI()),
        model="gpt-4o-mini",
        system_prompt_generator=SystemPromptGenerator( 
            background=[
                "You are a diagnosis Agent that takes a codes extracted from commits decides which of these is being used: design pattern, stack, framework and objective of commit.",
            ],
            output_instructions=[
                #"Run the 'search' tool on best practices related directly to the code. Be as specific as possible", # TODO: Better direction for the model.
                "Format the output using the appropriate schema.",
            ],
        ),
        input_schema=DiagnosisInputSchema,
        output_schema=DiagnosisOutputSchema,
    )
)


# Register the current date provider
# diagnosis_agent.register_context_provider("current_date", CurrentDateProvider("Current Date"))


def execute_tool(
    searxng_tool: SearxNGSearchTool,  _output: DiagnosisOutputSchema
) -> Union[SearxNGSearchToolOutputSchema, DiagnosisToolOutputSchema]:
    if _output.tool == "search":
        return searxng_tool.run(_output.tool_parameters)
    else:
        raise ValueError(f"Unknown tool: {_output.tool}")

#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    import os
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

    
    # Initialize Rich console
    console = Console()

    console.print("minecrafting")

    load_dotenv()

    client = instructor.from_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")))

    # Initialize the tools
    searxng_tool = SearxNGSearchTool(SearxNGSearchToolConfig(base_url="http://localhost:8080", max_results=5))


    # Print the full system prompt
    console.print(Panel(diagnosis_agent.system_prompt_generator.generate_prompt(), title="System Prompt", expand=False))
    console.print("\n")


    commit_infos = []
    commit_message = ""

    with open("commit_sample.json") as f: 
        s = f.read()
        j = json.loads(s)
        #TODO: switch to tools, i'm going to do it manually now.
        commit_message=j["commit"]["message"]
        
        for _file in j["files"]:

            _url = _file["raw_url"]
            _patch = _file["patch"]

            commit_infos.append([requests.get(_url).text, _patch])

    
    # Example inputs
    inputs = [
        "Review this commit: "+str(commit_infos),
    ]

    for user_input in inputs:
        print("minecrafting ")
        
        console.print(Panel(f"[bold cyan]User Input:[/bold cyan] {user_input[:100]+"..."}", expand=False))
        #input_schema = DiagnosisInputSchema(changes_made=commit_infos[0][1], commit_title=commit_message, relevant_code=commit_infos[0][0])
        input_schema = DiagnosisInputSchema(changes_made="cool commit", commit_title=commit_message, relevant_code="def minecraft();")

        _output = diagnosis_agent.run(input_schema)

        console.print("\n[bold magenta]Diagnosis Output:[/bold magenta]")
        diagnosis_syntax = Syntax(
            str(_output.model_dump_json(indent=2)), "json", theme="monokai", line_numbers=True
        )
        console.print(diagnosis_syntax)

        #response = execute_tool(searxng_tool, _output)

        # Print the tool output
        #console.print("\n[bold green]Tool Output:[/bold green]")
        #output_syntax = Syntax(str(response.model_dump_json(indent=2)), "json", theme="monokai", line_numbers=True)
        #console.print(output_syntax)

        # Reset the memory after each response

        diagnosis_agent.memory = AgentMemory()
