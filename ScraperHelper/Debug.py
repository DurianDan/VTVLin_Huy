# logging
import logging

class LoggingQuickSetup():
    def __init__(self,logging_file_path:str | None = None) -> None:
        '''
        If `logging_file_path` is None
        then program will only log to the terminal, or Notebook output
        '''
        self.logging_file = logging_file_path
    def minimalConfig(self,
                     tofilemode:str="a",
                     level=logging.INFO,
                     output_format="%(process)d-%(levelname)s-%(message)s",
                     toterminal=True):
        output_handlers = []
        if self.logging_file:
            output_handlers.append(
                logging.FileHandler(
                    self.logging_file,
                    mode=tofilemode))
        if toterminal:
            output_handlers.append(
                logging.StreamHandler()
            )
        logging.basicConfig(
            level=level,
            format=output_format,
            handlers=output_handlers
        )