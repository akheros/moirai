import base64
import paramiko
import winrm
from . import utils

class Task:
    def __init__(self, task, actions, files, artifacts):
        self.task = task
        self.actions = actions
        self.files = files
        self.artifacts = artifacts

    @staticmethod
    def run_task(task, items, config):
        print('launching task', task)

        machine = config.conf[items['target']]
        winrm = (machine.get('guest') == 'windows')
        if winrm:
            taskClass = WinrmTask
        else:
            taskClass = SshTask
        task = taskClass(task,
                items['actions'],
                items['files'],
                items['artifacts'],
                machine.get('username', 'vagrant'),
                machine.get('password', 'vagrant'),
                config.forwards[items['target']])
        task.send_files()
        task.exec_actions()
        task.recv_artifacts()


class WinrmTask(Task):
    chunk = 400
    del_script = """
$filePath = "{location}"
if (Test-Path $filePath) {{
  Remove-Item $filePath
}}
    """
    send_script = """
$filePath = "{location}"
$s = @"
{b64_content}
"@
$data = [System.Convert]::FromBase64String($s)
add-content -value $data -encoding byte -path $filePath
    """
    recv_script = """
$filePath = "{location}"
$buffer = New-Object byte[] {chunk}
$reader = [System.IO.File]::OpenRead($filepath)
$reader.Position = {offset}
$bytesRead = $reader.Read($buffer, 0, {chunk});
[Convert]::ToBase64String($buffer, 0, $bytesRead)
   """

    def __init__(self, task, actions, files, artifacts, username, password, forwards):
        super().__init__(task, actions, files, artifacts)
        self.session = winrm.Session('localhost:' + str(forwards[5985]),
                auth=(username, password))

    def send_files(self):
        try:
            for filename in self.files.split('\n'):
                if filename == '':
                    continue
                if '->' in filename:
                    filename, destination = utils.parse_associations(filename)[0]
                else:
                    destination = filename
                cmd = self.session.run_ps(self.del_script.format(location=destination))
                if cmd.status_code == 1:
                    print('[{}] File already exists and cannot be deleted: {}'
                            .format(self.task, filename))
                    print(cmd.std_err.decode('utf-8'))
                    continue
                with open(filename, 'rb') as f:
                    data = f.read(self.chunk)
                    while len(data) > 0:
                        cmd = self.session.run_ps(self.send_script.format(
                            location=destination,
                            b64_content=base64.b64encode(data).decode('utf-8')))
                        if cmd.status_code == 1:
                            print('[{}] Could not copy file: {}'
                                    .format(self.task, filename))
                            print(cmd.std_err.decode('utf-8'))
                            break
                        data = f.read(self.chunk)
        except:
            print('[{}] Winrm error while sending files'.format(self.task))
            raise

    def recv_artifacts(self):
        try:
            for filename in self.artifacts.split('\n'):
                if filename == '':
                    continue
                if '->' in filename:
                    filename, destination = utils.parse_associations(filename)[0]
                else:
                    destination = filename
                with open(destination, 'wb') as f:
                    offset = 0
                    while True:
                        cmd = self.session.run_ps(self.recv_script.format(
                            location=filename,
                            chunk=self.chunk,
                            offset=offset))
                        if cmd.status_code == 1:
                            print('[{}] Could not retrieve artifact: {}'
                                    .format(self.task, filename))
                            print(cmd.std_err.decode('utf-8'))
                            break
                        data = cmd.std_out.decode('utf-8').replace('\r\n','')
                        if len(data) == 0:
                            break
                        f.write(base64.b64decode(data))
                        offset += self.chunk
        except:
            print('[{}] Winrm error retrieving artifacts'.format(self.task))
            raise

    def exec_actions(self):
        try:
            for line in self.actions.split('\n'):
                if line == '':
                    continue
                cmd = self.session.run_ps(line)
                print('[{}]  return code:'.format(self.task), cmd.status_code)
                print('[{}]  STDOUT:'.format(self.task))
                print(cmd.std_out.decode('utf-8'))
                print('[{}]  STDERR:'.format(self.task))
                print(cmd.std_err.decode('utf-8'))
        except:
            print('[{}] Winrm error executing actions'.format(self.task))
            raise


class SshTask(Task):
    def __init__(self, task, actions, files, artifacts, username, password, forwards):
        super().__init__(task, actions, files, artifacts)
        self.port = forwards[22]
        self.username = username
        self.password = password

    def send_files(self):
        transport = paramiko.Transport(('localhost', self.port))
        try:
            transport.connect(None, self.username, self.password)
            sftp = transport.open_sftp_client()
            for filename in self.files.split('\n'):
                if filename == '':
                    continue
                if '->' in filename:
                    filename, destination = utils.parse_associations(filename)[0]
                else:
                    destination = filename
                sftp.put(filename, destination)
            transport.close()
        except:
            print('[{}] SFTP error while sending files'.format(self.task))
            raise

    def recv_artifacts(self):
        transport = paramiko.Transport(('localhost', self.port))
        try:
            transport.connect(None, self.username, self.password)
            sftp = transport.open_sftp_client()
            for filename in self.artifacts.split('\n'):
                if filename == '':
                    continue
                if '->' in filename:
                    filename, destination = utils.parse_associations(filename)[0]
                else:
                    destination = filename
                sftp.get(filename, destination)
            transport.close()
        except:
            print('[{}] SFTP error while retrieving artifacts'.format(self.task))
            raise

    def exec_actions(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect('localhost',
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    allow_agent=False,
                    look_for_keys=False)
            for line in self.actions.split('\n'):
                if line == '':
                    continue
                stdin, stdout, stderr = client.exec_command(line)
                exit_code = stdout.channel.recv_exit_status()
                print('[{}]  return code:'.format(self.task), exit_code)
                print('[{}]  STDOUT:'.format(self.task))
                print(stdout.read().decode('utf-8'))
                print('[{}]  STDERR:'.format(self.task))
                print(stderr.read().decode('utf-8'))
            client.close()
        except:
            print('[{}] SSH error executing actions'.format(self.task))
            raise

