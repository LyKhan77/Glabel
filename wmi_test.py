import subprocess

def get_windows_gpus():
    try:
        output = subprocess.check_output(['wmic', 'path', 'win32_VideoController', 'get', 'name'], text=True)
        lines = [line.strip() for line in output.split('\n') if line.strip() and line.strip().lower() != 'name']
        return lines
    except Exception as e:
        return str(e)

print("Detected GPUs:", get_windows_gpus())
