from pydantic import BaseModel, Field
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.processes.kernel_process import KernelProcessStep, KernelProcessStepContext

# A sample response model for the ProofreadingStep structured output
class ProofreadingResponse(BaseModel):
    """A class to represent the response from the proofreading step."""

    meets_expectations: bool = Field(description="Specifies if the proposed docs meets the standards for publishing.")
    explanation: str = Field(description="An explanation of why the documentation does or does not meet expectations.")
    suggestions: list[str] = Field(description="List of suggestions, empty if there are no suggestions for improvement.")

# A process step to proofread documentation
class ProofreadStep(KernelProcessStep):
    @kernel_function
    async def proofread_documentation(self, docs: str, context: KernelProcessStepContext, kernel: Kernel) -> None:
        print(f"[{ProofreadStep.__name__}]\t Proofreading product documentation...")

        system_prompt = """
        Your job is to proofread customer facing documentation for a new product from Contoso. You will be provided with 
        proposed documentation for a product and you must do the following things:

        1. Determine if the documentation passes the following criteria:
            1. Documentation must use a professional tone.
            1. Documentation should be free of spelling or grammar mistakes.
            1. Documentation should be free of any offensive or inappropriate language.
            1. Documentation should be technically accurate.
        2. If the documentation does not pass 1, you must write detailed feedback of the changes that are needed to 
            improve the documentation. 
        """

        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(docs)

        # Use structured output to ensure the response format is easily parsable
        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec
        assert isinstance(settings, OpenAIChatPromptExecutionSettings)  # nosec

        settings.response_format = ProofreadingResponse

        response = await chat_service.get_chat_message_content(chat_history=chat_history, settings=settings)

        formatted_response: ProofreadingResponse = ProofreadingResponse.model_validate_json(response.content)

        suggestions_text = "\n\t\t".join(formatted_response.suggestions)
        print(
            "\n\t"
            f"Grade: {'Pass' if formatted_response.meets_expectations else 'Fail'}\n\t"
            f"Explanation: {formatted_response.explanation}\n\t"
            f"Suggestions: {suggestions_text}"
        )

        if formatted_response.meets_expectations:
            await context.emit_event(process_event="documentation_approved", data=docs)
        else:
            assert isinstance(suggestions_text, str)
            
            # single suggestions parameter
            # await context.emit_event(
            #     process_event="documentation_rejected",
            #     data=suggestions_text,
            # )

            # metadata parameter
            await context.emit_event(
                process_event="documentation_rejected",
                data={"explanation": formatted_response.explanation, "suggestions": suggestions_text},
            )
