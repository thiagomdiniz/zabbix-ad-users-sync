import logging

class LogManager:

    # Log variables
    _log_level = "INFO"
    _logger_name = __name__
    _log_file = 'python.log'
    logger = None

    def __init__(self, log_level=_log_level, logger_name=_logger_name, log_file=_log_file):
        """
        Metodo construtor.

        Parameters
        ----------
        log_level : str
            Nivel de log a ser exibido. Valores possiveis: "INFO", "WARN" e "DEBUG".
        log_file : str
            Nome do arquivo no qual os logs serao gravados.
        """
        self._log_level = self.getLogLevel(log_level)
        self._log_file = log_file
        self._logger_name = logger_name
        self.logger = logging.getLogger(self._logger_name)
        self.logger.setLevel(self._log_level)
        handler = logging.FileHandler(self._log_file)
        handler.setLevel(self._log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def getLogLevel(self, log_level):
        """
        Metodo que retorna o nivel de log a ser utilizado com base na string informada.

        Parameters
        ----------
        log_level : str
            Nivel de log a ser exibido. Valores possiveis: "INFO", "WARN" e "DEBUG".

        Returns
        -------
        int
            Nivel de log a ser utilizado pela classe.
        """
        result = logging.INFO
        if log_level == 'WARN':
            result = logging.WARN
        elif log_level == 'DEBUG':
            result = logging.DEBUG

        return result

if __name__ == "__main__":
    lg = LogManager("DEBUG")
    lg.logger.debug("debug...")
