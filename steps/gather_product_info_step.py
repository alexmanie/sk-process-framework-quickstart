from typing import ClassVar

from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import KernelProcessStep
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from semantic_kernel import Kernel

class GatherProductInfoStep(KernelProcessStep):

    @kernel_function
    async def gather_product_information(self, product_name: str, kernel: Kernel) -> str:
        print(f"[{GatherProductInfoStep.__name__}]\t Gathering product information for Product Name: {product_name}")

        system_prompt = """
Your job is to write high quality and engaging customer facing general information for a new product from Contoso. You will 
be provided with a product name and you will generate a product description, product features, and troubleshooting information. 
You must use this information and nothing else to generate the documentation. If suggestions are provided on the 
documentation you create, take the suggestions into account and rewrite the documentation. Make sure the product 
sounds amazing.
"""

        # call an LLM to generate dynamic product information
        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(f"Product Name: {product_name}")

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec

        response = await chat_service.get_chat_message_content(chat_history=chat_history, settings=settings)

        return str(response)
    


#         return """
# Product Description:

# GlowBrew is a revolutionary AI driven coffee machine with industry leading number of LEDs and 
# programmable light shows. The machine is also capable of brewing coffee and has a built in grinder.

# Product Features:
# 1. **Luminous Brew Technology**: Customize your morning ambiance with programmable LED lights that sync 
#     with your brewing process.
# 2. **AI Taste Assistant**: Learns your taste preferences over time and suggests new brew combinations 
#     to explore.
# 3. **Gourmet Aroma Diffusion**: Built-in aroma diffusers enhance your coffee's scent profile, energizing 
#     your senses before the first sip.

# Troubleshooting:
# - **Issue**: LED Lights Malfunctioning
#     - **Solution**: Reset the lighting settings via the app. Ensure the LED connections inside the 
#         GlowBrew are secure. Perform a factory reset if necessary.
#         """