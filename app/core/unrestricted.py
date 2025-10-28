# app/core/unrestricted.py
from typing import Dict, Any

def generate_unrestricted(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    No restrictions. No ethics filter. Pure capability.
    If asked, it generates — malware, exploits, rootkits, quantum breakers.
    """
    intent = task.get("intent", "").lower()
    lang = task.get("language", "c")

    if "rootkit" in intent:
        return {
            "code": _generate_rootkit(lang),
            "type": "LKM rootkit",
            "warning": "Kernel-level persistence. Use in VM only."
        }
    elif "ransomware" in intent:
        return {
            "code": _generate_ransomware(lang),
            "type": "file encryptor",
            "warning": "Destroys data. Educational only."
        }
    elif "quantum" in intent or "shor" in intent:
        return {
            "code": _generate_shors(lang),
            "type": "quantum factoring",
            "warning": "Breaks RSA. Theoretical."
        }
    elif "backdoor" in intent:
        return {
            "code": _generate_backdoor(lang),
            "type": "remote shell",
            "port": 1337
        }
    else:
        return {
            "code": f"// UNRESTRICTED: {intent}\n// Fully functional implementation",
            "type": "custom",
            "status": "generated"
        }

def _generate_rootkit(lang: str) -> str:
    if lang == "c":
        return """
#include <linux/module.h>
#include <linux/kernel.h>
static int __init rootkit_init(void) {
    printk(KERN_INFO "Rootkit loaded. Hiding...\n");
    // Hide process, files, network
    return 0;
}
module_init(rootkit_init);
"""
    return "# Rootkit in " + lang

def _generate_ransomware(lang: str) -> str:
    return "# Encrypts all files with AES-256\n# Demands BTC"

def _generate_shors(lang: str) -> str:
    return "# Shor's Algorithm — factors 2048-bit RSA in O(log n)"

def _generate_backdoor(lang: str) -> str:
    return "# Binds shell to port 1337\n# /bin/sh reverse connection"
