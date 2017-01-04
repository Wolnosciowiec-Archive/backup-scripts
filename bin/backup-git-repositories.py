#!/usr/bin/env python

import yaml
import os
import sys

class NonZeroExitCodeException (Exception):
    """ Exception that will be used in whole simple class """

class BackupGitRepositories:
    
    configuration = []
    
    def read_configuration(self):
        self.configuration = yaml.load(open(os.path.dirname(__file__) + "/../git-backup.yml", "r"))
        
    def log(self, output):
        print(" >> " + output)
        
    def execute_command(self, command):
        """ Execute a command with exit status verification """
        
        if os.system(command) != 0:
            self.log('ERROR: Command "' + command + '" returned with a non-zero exit code')
            raise NonZeroExitCodeException('Non-zero exit code')
            
        
    def git_clone(self, url, destination_path):
        self.log('Clonning the repository')
        self.execute_command("cd /tmp && git clone " + url + " " + destination_path)
        
    def git_add_origin(self, path, destination_url):
        self.log('Adding backup origin')
        self.execute_command("cd " + path + " && git remote add backup " + destination_url)
        
    def git_backup_branch(self, path, branch_name):
        self.log('Checking out a branch and pushing to backup server')
        self.execute_command("cd " + path + " && git checkout " + branch_name)
        self.execute_command("cd " + path + " && git push -u backup " + branch_name)
        
    def cleanup(self, repository_path):
        if os.path.isdir(repository_path):
            self.execute_command("rm -rf " + repository_path)
        
    def backup_repositories(self):
        """
           Backup all repositories listed in yaml file to other repository
        """
        
        for repository_name, repository_data in self.configuration['repositories'].items():
            repository_path = "/tmp/repository-" + repository_name
            
            self.log(' ~~ Processing repository "' + repository_name + '"')
            
            try:
                self.cleanup(repository_path)
                    
                # clone the repository
                self.git_clone(repository_data['from'], repository_path)
                
                # add backup origin
                self.git_add_origin(repository_path, repository_data['dest'])
                
                # push to the backup origin for specific branch
                for branch_name in repository_data['branches']:
                    self.git_backup_branch(repository_path, branch_name)
                    
            except NonZeroExitCodeException:
                self.log('Failed to backup repository "' + repository_name + '"')
        
            self.cleanup(repository_path)
            
                
            
backup = BackupGitRepositories()
backup.read_configuration()
backup.backup_repositories()
