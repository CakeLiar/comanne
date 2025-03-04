import operator
from dataclasses import dataclass, field
from functools import partial
from typing import Annotated, Optional, Sequence

from langgraph.constants import END, START
from langgraph.graph.state import StateGraph


def wide_state(n: int) -> StateGraph:
    @dataclass(kw_only=True)
    class State:
        messages: Annotated[list, operator.add] = field(default_factory=list)
        trigger_events: Annotated[list, operator.add] = field(default_factory=list)
        """The external events that are converted by the graph."""
        primary_issue_medium: Annotated[str, lambda x, y: y or x] = field(
            default="email"
        )
        autoresponse: Annotated[Optional[dict], lambda _, y: y] = field(
            default=None
        )  # Always overwrite
        issue: Annotated[dict | None, lambda x, y: y if y else x] = field(default=None)
        relevant_rules: Optional[list[dict]] = field(default=None)
        """SOPs fetched from the rulebook that are relevant to the current conversation."""
        memory_docs: Optional[list[dict]] = field(default=None)
        """Memory docs fetched from the memory service that are relevant to the current conversation."""
        categorizations: Annotated[list[dict], operator.add] = field(
            default_factory=list
        )
        """The issue categorizations auto-generated by the AI."""
        responses: Annotated[list[dict], operator.add] = field(default_factory=list)
        """The draft responses recommended by the AI."""

        user_info: Annotated[Optional[dict], lambda x, y: y if y is not None else x] = (
            field(default=None)
        )
        """The current user state (by email)."""
        crm_info: Annotated[Optional[dict], lambda x, y: y if y is not None else x] = (
            field(default=None)
        )
        """The CRM information for organization the current user is from."""
        email_thread_id: Annotated[
            Optional[str], lambda x, y: y if y is not None else x
        ] = field(default=None)
        """The current email thread ID."""
        slack_participants: Annotated[dict, operator.or_] = field(default_factory=dict)
        """The growing list of current slack participants."""
        bot_id: Optional[str] = field(default=None)
        """The ID of the bot user in the slack channel."""
        notified_assignees: Annotated[dict, operator.or_] = field(default_factory=dict)

    def read_write(read: str, write: Sequence[str], input: State) -> dict:
        val = getattr(input, read)
        val_single = val[-1] if isinstance(val, list) else val
        val_list = val if isinstance(val, list) else [val]
        return {
            k: val_list if isinstance(getattr(input, k), list) else val_single
            for k in write
        }

    builder = StateGraph(State)
    builder.add_edge(START, "one")
    builder.add_node(
        "one",
        partial(read_write, "messages", ["trigger_events", "primary_issue_medium"]),
    )
    builder.add_edge("one", "two")
    builder.add_node(
        "two",
        partial(read_write, "trigger_events", ["autoresponse", "issue"]),
    )
    builder.add_edge("two", "three")
    builder.add_edge("two", "four")
    builder.add_node(
        "three",
        partial(read_write, "autoresponse", ["relevant_rules"]),
    )
    builder.add_node(
        "four",
        partial(
            read_write,
            "trigger_events",
            ["categorizations", "responses", "memory_docs"],
        ),
    )
    builder.add_node(
        "five",
        partial(
            read_write,
            "categorizations",
            [
                "user_info",
                "crm_info",
                "email_thread_id",
                "slack_participants",
                "bot_id",
                "notified_assignees",
            ],
        ),
    )
    builder.add_edge(["three", "four"], "five")
    builder.add_edge("five", "six")
    builder.add_node(
        "six",
        partial(read_write, "responses", ["messages"]),
    )
    builder.add_conditional_edges(
        "six", lambda state: END if len(state.messages) > n else "one"
    )

    return builder


if __name__ == "__main__":
    import asyncio

    import uvloop

    from langgraph.checkpoint.memory import MemorySaver

    graph = wide_state(1000).compile(checkpointer=MemorySaver())
    input = {
        "messages": [
            {
                str(i) * 10: {
                    str(j) * 10: ["hi?" * 10, True, 1, 6327816386138, None] * 5
                    for j in range(5)
                }
                for i in range(5)
            }
        ]
    }
    config = {"configurable": {"thread_id": "1"}, "recursion_limit": 20000000000}

    async def run():
        async for c in graph.astream(input, config=config):
            print(c.keys())

    uvloop.install()
    asyncio.run(run())
