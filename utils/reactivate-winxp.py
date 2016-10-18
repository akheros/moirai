#!/usr/bin/python

import winrm

session = winrm.Session('localhost:55985', auth=('IEUser', 'Passw0rd!'))
session.run_cmd('rundll32.exe syssetup,SetupOobeBnk')

