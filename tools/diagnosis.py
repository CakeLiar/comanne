from pydantic import Field
from sympy import sympify

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class DiagnosisToolInputSchema(BaseIOSchema):
    """
    Tool for performing diagnosis on piece of code to understand code language, framework, and design pattern.
    """

    piece_of_code: str = Field(..., description="Piece of code to analyze.")


#################
# OUTPUT SCHEMA #
#################
class DiagnosisToolOutputSchema(BaseIOSchema):
    """
    Schema for the output of the DiagnosisTool.
    """
    language: str = Field(..., description="The programming language identified")
    framework: str = Field(..., description="The framework being used")
    design_pattern: str = Field(..., description="The design pattern implemented")
    tool: str = Field(..., description="Use search tool") #TODO: remove hard code here


#################
# CONFIGURATION #
#################
class DiagnosisToolConfig(BaseToolConfig):
    """
    Configuration for the CalculatorTool.
    """

    pass


#####################
# MAIN TOOL & LOGIC #
#####################

class DiagnosisTool(BaseTool):
    """
    Tool for classifying code into a language, framework and design pattern vector.

    Attributes:
        input_schema (DiagnosisToolInputSchema): The schema for the input data.
        output_schema (DiagnosisToolOutputSchema): The schema for the output data.
    """

    input_schema = DiagnosisToolInputSchema
    output_schema = DiagnosisToolOutputSchema

    def __init__(self, config: DiagnosisToolConfig = DiagnosisToolConfig()):
        """
        Initializes the DiagnosisTool.

        Args:
            config (CalculatorToolConfig): Configuration for the tool.
        """
        super().__init__(config)

    def run(self, params: DiagnosisToolInputSchema) -> DiagnosisToolOutputSchema:
        """
        Executes the DiagnosisTool with the given parameters.

        Args:
            params (DiagnosisToolInputSchema): The input parameters for the tool.

        Returns:
            DiagnosisToolOutputSchema: The result of the classification.
        """

        # Convert the expression string to a symbolic expression
        params.piece_of_code
        #TODO: Call openai here


        return DiagnosisToolOutputSchema(language="Python", framework="Unknown", design_pattern="Unknown")


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    diagnosis = DiagnosisTool()
    piece_of_code = """    
    
    """
    result = diagnosis.run(DiagnosisTool(expression="sin(pi/2) + cos(pi/4)"))
    print(result)  # Expected output: {"language":"Python","framework":"Unknown","design_pattern":"Unknown"}
