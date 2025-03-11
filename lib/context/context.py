#####################
# CONTEXT PROVIDERS #
#####################
from datetime import datetime

from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase


class CurrentDateProvider(SystemPromptContextProviderBase):
    def __init__(self, title):
        super().__init__(title)
        self.date = datetime.now().strftime("%Y-%m-%d")

    def get_info(self) -> str:
        return f"Current date in format YYYY-MM-DD: {self.date}"

