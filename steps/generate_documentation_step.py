from typing import ClassVar
from typing import Any
from pydantic import BaseModel, Field
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import KernelProcessStep, KernelProcessStepContext, KernelProcessStepState

class GeneratedDocumentationState(BaseModel):
    """State for the GenerateDocumentationStep."""
    chat_history: ChatHistory | None = None

class GenerateDocumentationStep(KernelProcessStep[GeneratedDocumentationState]):
    state: GeneratedDocumentationState = Field(default_factory=GeneratedDocumentationState)

    system_prompt: ClassVar[str] = """
Your job is to write high quality and engaging customer facing documentation for a new product from Contoso. You will 
be provided with information about the product in the form of internal documentation, specs, and troubleshooting guides 
and you must use this information and nothing else to generate the documentation. If suggestions are provided on the 
documentation you create, take the suggestions into account and rewrite the documentation. Make sure the product 
sounds amazing.
"""

    async def activate(self, state: KernelProcessStepState[GeneratedDocumentationState]):
        self.state = state.state
        if self.state.chat_history is None:
            self.state.chat_history = ChatHistory(system_message=self.system_prompt)

    @kernel_function
    async def generate_documentation(self, context: KernelProcessStepContext, product_info: str, kernel: Kernel) -> None:
        print(f"[{GenerateDocumentationStep.__name__}]\t Generating documentation for provided product_info...")

        self.state.chat_history.add_user_message(f"Product Information:\n{product_info}")

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec

        response = await chat_service.get_chat_message_content(chat_history=self.state.chat_history, settings=settings)

        # hack the text - REMOVE THIS LATER // just for testing
        hack_response = str(response).replace("light", "ligth")
        await context.emit_event(process_event="documentation_generated", data=hack_response)

        # await context.emit_event(process_event="documentation_generated", data=str(response))
    
    @kernel_function
    async def apply_suggestions(self, proofread_response: dict[str, str], context: KernelProcessStepContext, kernel: Kernel) -> None:
        print(f"[{GenerateDocumentationStep.__name__}]\t Rewriting documentation with provided suggestions...")

        self.state.chat_history.add_user_message(
            f"Rewrite the documentation with the following suggestions:\n\n{proofread_response['suggestions']}\n\n"
            f"Reason:\n\n{proofread_response['explanation']}\n\n"
        )

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec

        generated_documentation_response = await chat_service.get_chat_message_content(
            chat_history=self.state.chat_history, settings=settings
        )

        await context.emit_event(process_event="documentation_generated", data=str(generated_documentation_response))
