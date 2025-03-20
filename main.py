import asyncio

from processes.documentation_new_product import DocumentationNewProductProcess

from dotenv import load_dotenv
load_dotenv(override=True)

from utils.load_config import LoadConfig
config = LoadConfig()

async def run_the_process():
    """Run the process."""
    # Start the process
    process = DocumentationNewProductProcess()
    await process.start_the_process()

if __name__ == "__main__":
    asyncio.run(run_the_process())
