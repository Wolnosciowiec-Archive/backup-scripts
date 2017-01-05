Wolnościowiec: Backup scripts
=============================

A set of simple backup scripts.

##### Installation

To start simply copy the `backup.yml-example` into `backup.yml` and modify, then run scripts from `bin` directory.

Requires:
- ssh
- sshpass
- mysqldump
- python
- GNU tar
- git

Includes:
- git backup (`Server A` to `Server B`, use case: simplest mirroring of a git server)
- tar & gzip the whole server via SSH
- Backup of local/remote MySQL server, compatible with SSH and Docker

Todo:
- tar & gzip only specified remote files/directories and be able to restore them later
- FTP backup to tar & gzip