import io
import sys
from typing import Any

from autogpt_server.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from autogpt_server.data.model import SchemaField


class PythonExecutionBlock(Block):
    class Input(BlockSchema):
        code: str = SchemaField(
            description="Python code to execute", placeholder="print(f'Hello, {name}!')"
        )
        args: dict[str, Any] = SchemaField(
            description="Arguments to pass to the code",
            default={},
            # placeholder={"name": "World", "number": 42},
        )
        timeout: int = SchemaField(
            description="Execution timeout in seconds", default=5
        )

    class Output(BlockSchema):
        result: str = SchemaField(description="Execution result or output")
        error: str = SchemaField(description="Error message if execution failed")

    def __init__(self):
        super().__init__(
            id="a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
            description="This block executes Python code with provided arguments and returns the output or any error messages.",
            categories={BlockCategory.BASIC},
            input_schema=PythonExecutionBlock.Input,
            output_schema=PythonExecutionBlock.Output,
            test_input={
                "code": "print(f'Hello, {name}! Your number is {number}.')",
                "args": {"name": "Alice", "number": 42},
                "timeout": 5,
            },
            test_output=[
                ("result", "Hello, Alice! Your number is 42.\n"),
            ],
        )

    def run(self, input_data: Input) -> BlockOutput:
        code = input_data.code
        args = input_data.args
        timeout = input_data.timeout

        # Redirect stdout to capture print statements
        stdout = io.StringIO()
        sys.stdout = stdout

        try:
            # Prepare the execution environment with the provided args
            exec_globals = args.copy()

            # Execute the code with a timeout
            exec(code, exec_globals)

            # Get the output
            output = stdout.getvalue()

            if output:
                yield "result", output
            else:
                # If there's no output, return the last expression's result
                last_expression = list(exec_globals.values())[-1]
                yield "result", str(last_expression)

        except Exception as e:
            yield "error", str(e)

        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__