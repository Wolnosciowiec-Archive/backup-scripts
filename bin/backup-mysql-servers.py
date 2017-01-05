#!/usr/bin/env python

import yaml
import os
import sys

t = sys.argv[0].replace(os.path.basename(sys.argv[0]), "") + "/../lib/"

if os.path.isdir(t):
    sys.path.append(t)

import WolnosciowiecBackup.BaseBackupApplication
from WolnosciowiecBackup.NonZeroExitCodeException import NonZeroExitCodeException

class BackupMySQLServers (WolnosciowiecBackup.BaseBackupApplication):
    
    def get_default_values(self):
        """
           Default values for a mysql_servers node
        """
        
        return {
            'ssh': False,
            'ssh_user': 'root',
            'ssh_pass': '',
            'ssh_host': 'localhost',
            'ssh_port': 22,
            'mysql_host': 'localhost',
            'mysql_port': 3306,
            'mysql_user': 'root',
            'mysql_pass': '',
            'mysql_database': 'put_your_database_info_in_backup_yml',
            'command_wrapping': "%s"
        }
    
    
    def correct_node(self, server_name):
        """
           Puts the default values to fill missing keys in configuration (as not all keys are required of course)
        """
        
        for key, default_value in self.get_default_values().items():
            if not key in self.configuration['mysql_servers'][server_name]:
                self.configuration['mysql_servers'][server_name][key] = default_value
        
        return self.configuration['mysql_servers'][server_name]


    def create_command(self, server_name):
        """
           Create a shell command that would be executed to dump the database
        """
        
        server_details = self.configuration['mysql_servers'][server_name]
        command        = ""
        
        if server_details['ssh'] == True:
            command += "sshpass -p " + server_details['ssh_pass']
            command += " ssh -o StrictHostKeyChecking=no " + server_details['ssh_user'] + "@" + server_details['ssh_host'] + " -p " + str(server_details['ssh_port'])
            command += ' "'
            
        mysql_dump_command = " mysqldump -h " + server_details['mysql_host'] + " -u " + server_details['mysql_user']
        
        if len(server_details['mysql_pass']) > 0:
            mysql_dump_command += " -p" + server_details['mysql_pass']
            
        if server_details['mysql_port']:
            mysql_dump_command += " -P " + str(server_details['mysql_port'])
            
        mysql_dump_command += " " + server_details['mysql_database'] 
        
        command += server_details['command_wrapping'].replace('%s', mysql_dump_command)
        
        if server_details['ssh'] == True:
            command += '"'
            
        return command
 
 
    def do_backup(self):
        """
           Main action, a controller
        """
        
        if not "mysql_servers" in self.configuration:
            self.log('No an mysql servers configured, exiting...')
            sys.exit(0)
            
        for server_name, server_details in self.configuration['mysql_servers'].items():
            self.log('Running backup of "' + server_name + '"')

            server_details = self.correct_node(server_name)
            command        = self.create_command(server_name) + ' > ./backups/' + server_name + '.sql'

            self.execute_command(command)
            
app = BackupMySQLServers()
app.read_configuration()
app.do_backup()
