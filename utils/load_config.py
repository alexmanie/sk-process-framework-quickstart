import os
import yaml
from pyprojroot import here

class LoadConfig:
    def __init__(self) -> None:
        with open(here("app_config.yaml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.app_config = app_config
        self.load_config(app_config=app_config)

    def __get_process_by_id(self, process_id: str):
        """Get the process by name."""
        return next((x for x in self.app_config['processes'] if x['id'] == process_id), None)
    
    def __get_process_by_name(self, process_name: str):
        """Get the process by name."""
        return next((x for x in self.app_config['processes'] if x['name'] == process_name), None)


    def load_config(self, app_config):
        # load config
        self.documentation_new_product_process = self.__get_process_by_id("new_product")
