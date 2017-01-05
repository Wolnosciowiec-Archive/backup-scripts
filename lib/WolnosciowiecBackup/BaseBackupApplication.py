import yaml
import os

from WolnosciowiecBackup.NonZeroExitCodeException import NonZeroExitCodeException

class BaseBackupApplication:
    configuration = []

    def read_configuration(self):
        self.configuration = yaml.load(open(os.path.dirname(__file__) + "/../../backup.yml", "r"))

    def log(self, output):
        print(" >> " + output)
        
    def get_setting_value(self, key, default = None):
        """
           Get value from section "settings"
        """
    
        if not "settings" in self.configuration or not key in self.configuration['settings']:
            return default
        
        return self.configuration['settings'][key]

    def execute_command(self, command):
        """ Execute a command with exit status verification """

        if os.system(command) != 0:
            self.log('ERROR: Command "' + command + '" returned with a non-zero exit code')
            raise NonZeroExitCodeException('Non-zero exit code')
