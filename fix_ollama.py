import subprocess

svc = open("/etc/systemd/system/ollama.service").read()
if "OLLAMA_HOST" not in svc:
    svc = svc.replace(
        "ExecStart=/usr/local/bin/ollama serve",
        'Environment="OLLAMA_HOST=0.0.0.0:11434"\nExecStart=/usr/local/bin/ollama serve'
    )
    open("/etc/systemd/system/ollama.service","w").write(svc)
    print("Added OLLAMA_HOST")
else:
    print("Already set")

subprocess.run(["systemctl","daemon-reload"])
subprocess.run(["systemctl","restart","ollama"])
import time; time.sleep(3)
r = subprocess.run(["systemctl","is-active","ollama"], capture_output=True, text=True)
print("Ollama status:", r.stdout.strip())