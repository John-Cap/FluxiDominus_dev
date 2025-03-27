import atexit
import subprocess
import os
import sys

'''
TODO:
1. Are subprocess children also killed?
2. Only terminates subprocesses on normal exit?
'''

class FdSubprocess:
    def __init__(self):
        self.pythonPaths = {}
        self.subprocesses = {}
        self._pathCnt = 0
        
        atexit.register(self.terminateAllProcesses)

    def addPythonPath(self, path):
        cntr = self._pathCnt
        self.pythonPaths[cntr] = path
        self._pathCnt += 1
        return cntr

    def spawnExternalMain(self, scriptDir):
        if os.name == 'nt':
            pythonPath = os.path.join(scriptDir, '.venv', 'Scripts', 'python.exe')
        else:
            pythonPath = os.path.join(scriptDir, '.venv', 'bin', 'python')

        scriptPath = os.path.join(scriptDir, 'main.py')
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        process = subprocess.Popen(
            [pythonPath, scriptPath],
            cwd=scriptDir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        processId = self.addPythonPath(pythonPath)
        self.subprocesses[processId] = process

        print(f"✅ Spawned subprocess {processId} for {scriptPath}")
        return processId

    def checkProcessOutput(self, processId):
        proc = self.subprocesses.get(processId)
        if proc is None:
            print(f"No subprocess with ID {processId}")
            return

        stdout, stderr = proc.communicate(timeout=0.1) if proc.poll() is not None else ("", "")

        if stdout:
            print(f"[{processId} STDOUT]: {stdout}")
        if stderr:
            print(f"[{processId} STDERR]: {stderr}")
            
    def terminateAllProcesses(self):
        for pid, proc in self.subprocesses.items():
            if proc.poll() is None:  # Still running
                print(f"Auto-terminating subprocess {pid}")
                proc.terminate()
                
    def terminateProcess(self, processId):
        proc = self.subprocesses.get(processId)
        if proc and proc.poll() is None:
            proc.terminate()
            print(f"Terminated subprocess {processId}")
        else:
            print(f"Subprocess {processId} already exited or doesn't exist.")
            
if __name__ == "__main__":
    fdSubprocess = FdSubprocess()
    baseDir = os.path.dirname(os.path.abspath(__file__))
    evaluatorDir = os.path.join(baseDir, 'OPTIMIZATION_TEMP', 'Evaluator')

    pid = fdSubprocess.spawnExternalMain(evaluatorDir)

    print("Main script continues...")
