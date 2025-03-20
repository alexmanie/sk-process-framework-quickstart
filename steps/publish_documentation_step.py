from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import KernelProcessStep

class PublishDocumentationStep(KernelProcessStep):

    @kernel_function
    async def publish_documentation(self, docs: str) -> None:
        print(f"[{PublishDocumentationStep.__name__}]\t Publishing product documentation:\n\n{docs}")