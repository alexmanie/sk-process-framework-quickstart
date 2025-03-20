import os
from enum import Enum

from semantic_kernel.kernel import Kernel
from semantic_kernel.processes import ProcessBuilder
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.processes.local_runtime.local_event import KernelProcessEvent
from semantic_kernel.processes.local_runtime.local_kernel_process import start

# import steps
from steps.gather_product_info_step import GatherProductInfoStep
from steps.generate_documentation_step import GenerateDocumentationStep
from steps.publish_documentation_step import PublishDocumentationStep
from steps.proofread_step import ProofreadStep

from dotenv import load_dotenv
load_dotenv(override=True)

from utils.load_config import LoadConfig
config = LoadConfig()

class ChatBotEvents(Enum):
    StartProcess = "start"
    # IntroComplete = "introComplete"
    # AssistantResponseGenerated = "assistantResponseGenerated"
    Exit = "exit"

class DocumentationNewProductProcess:
    """Documentation New Product Process."""

    def __init__(self):
        """Initialize the process."""
        
        # Create the process builder
        process_builder = ProcessBuilder(name=config.documentation_new_product_process['name'])

        # Add the steps
        info_gathering_step = process_builder.add_step(GatherProductInfoStep)
        docs_generation_step = process_builder.add_step(GenerateDocumentationStep)
        docs_proofread_step = process_builder.add_step(ProofreadStep)
        docs_publish_step = process_builder.add_step(PublishDocumentationStep)

        # Orchestrate the events
        process_builder.on_input_event(ChatBotEvents.StartProcess).send_event_to(
            target=info_gathering_step, 
            parameter_name="product_name"
        )

        info_gathering_step.on_function_result(
            function_name=GatherProductInfoStep.gather_product_information.__name__
        ).send_event_to(
            target=docs_generation_step, 
            function_name="generate_documentation", 
            parameter_name="product_info"
        )

        # simple flow without proofreading
        # docs_generation_step.on_event("documentation_generated").send_event_to(target=docs_publish_step)

        # flow with proofreading
        docs_generation_step.on_event("documentation_generated").send_event_to(
            target=docs_proofread_step, parameter_name="docs"
        )

        docs_proofread_step.on_event("documentation_rejected").send_event_to(
            target=docs_generation_step,
            function_name="apply_suggestions",
            parameter_name="proofread_response"
        )

        docs_proofread_step.on_event("documentation_approved").send_event_to(target=docs_publish_step)

        # Configure the kernel with an AI Service and connection details, if necessary
        self.kernel = Kernel()
        self.kernel.add_service(
            AzureChatCompletion(
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  
                # # If you don't provide an API key, the service will attempt to authenticate using the Entra token.
                # api_key="my-api-key", 
            )
        )

        # Build the process
        self.kernel_process = process_builder.build()
    

    async def start_the_process(self):
        """Start the process with the given kernel and initial event."""
        
        # async with await start(
        #     process=self.kernel_process,
        #     kernel=self.kernel,
        #     initial_event=KernelProcessEvent(id="Start", data="Contoso GlowBrew"),
        # ) as process_context:
        #     _ = await process_context.get_state()

        await start(
            process=self.kernel_process,
            kernel=self.kernel,
            initial_event=KernelProcessEvent(id=ChatBotEvents.StartProcess, data="Lavalamp 2.0"),
        )

