#!/usr/bin/env python

import yaml
import os
import sys
from datetime import datetime

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
    
    
    def get_backup_file_name(self, server_name):
        """ 
           Returns a file name for backup file
        """
        
        return datetime.now().strftime('%Y-%m-%d-%H_%M-_' + server_name) + '.sql'
    
    def do_cleanup(self):
        """
           Remove old backups
        """
        
        if not self.get_setting_value('max_mysql_backups_count'):
            self.log('settings/max_mysql_backups_count not defined, skipping clean up')
            return True
        
        maxAmount = int(self.get_setting_value('max_mysql_backups_count'))
        files     = {}
        
        if maxAmount < 1:
            self.log('settings/max_mysql_backups_count is lower than 1, it should not be')
            return False

        self.log('Looking for old backups to clean up')

        for entry in os.scandir(self.get_backups_dir()):
            if entry.name.endswith('.sql') and entry.is_file():
                parts = entry.name.split('-_')

                if not parts[1] in files:
                    files[parts[1]] = []

                files[parts[1]].append(entry.name)

        for type_name, data in files.items():
            data.sort()
            data.reverse()
            num = 0

            for file in data:
                num = num + 1

                if num > maxAmount:
                    self.log('Removing file "' + file + '"')
                    os.remove(self.get_backups_dir() + '/' + file)

    def get_backups_dir(self):
        """
           Directory where to place backups
        """

        return self.get_setting_value('mysql_backups_dir', './backups')

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
            command        = self.create_command(server_name) + ' > ' + self.get_backups_dir() + '/' + self.get_backup_file_name(server_name)

            self.execute_command(command)
            
app = BackupMySQLServers()
app.read_configuration()
app.do_backup()
app.do_cleanup()
