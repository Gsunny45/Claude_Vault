#!/usr/bin/env python3
"""Keyboard <-> Vault key/config injection test harness (stdlib only).

Cross-check runner for the ADB key-injection contract of CteKeysActivity on the
live HermeticA-Z keyboard. NON-DESTRUCTIVE by default: injects a throwaway keyRef
and restores the encrypted prefs file at teardown.

Contract verified from source 2026-05-29 (CteKeysActivity.kt / KeyVault.kt):
    am start -n <pkg>/...CteKeysActivity --ei inject 1 -e keyRef <R> -e keyValue <V>
Success log:  "Key injected via ADB: <R> (<N> chars)"
Reject log:   "ADB inject: missing keyRef or keyValue extras"
Storage: EncryptedSharedPreferences (names+values encrypted) -> verify via logcat
+ prefs entry-count delta, not plaintext.

Usage:
    python test_key_injection.py
    python test_key_injection.py --real-key-ref GROQ_KEY --real-key-value sk-...
"""
import argparse
import re
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime

ADB = r"C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe"
PKG = "dev.patrickgold.florisboard.vault.debug"
ACT = "dev.patrickgold.florisboard.ime.ai.CteKeysActivity"
SERIAL = "ZY22G7NFLK"
PREFS = "shared_prefs/florisboard_ai_keyvault.xml"
COMP = f"{PKG}/{ACT}"
TEST_REF = "__TEST_INJECT_KEY__"

results = []  # (id, name, pass:bool, detail)


def adb(*args, timeout=40):
    return subprocess.run([ADB, "-s", SERIAL, *args],
                          capture_output=True, text=True, timeout=timeout).stdout


def run_as(cmd):
    return adb("shell", f"run-as {PKG} {cmd}")


def rec(tid, name, ok, detail):
    results.append((tid, name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {tid:<7} {name} — {detail}")


def entry_count():
    xml = run_as(f"cat {PREFS}")
    if "<map" not in xml:
        return -1
    return len(re.findall(r"<string name=", xml))


def inject(extras=None, no_extras=False):
    # CteKeysActivity is a singleTask deep-link activity; inject logic is in
    # onCreate only. Force-stop first (fresh onCreate), and launch with explicit
    # component PLUS matching action+data to bypass the ui:// resolver chooser.
    adb("shell", "am", "force-stop", PKG)
    time.sleep(0.5)
    adb("logcat", "-c")
    args = ["shell", "am", "start", "-n", COMP,
            "-a", "android.intent.action.VIEW", "-d", "ui://hermetica-z/cte/keys"]
    if not no_extras and extras:
        for k, v in extras.items():
            if k == "inject":
                args += ["--ei", "inject", str(v)]
            else:
                args += ["-e", k, str(v)]
    adb(*args)
    time.sleep(1.2)
    return adb("logcat", "-d", "-s", "CteKeysActivity:*", "KeyVault:*")


def inject_shell(key_ref, raw_value):
    """Inject via a single device-shell string so the value is tokenized by the
    device shell, not subprocess. Required for whitespace-only values, which the
    arg-split form drops (am errors 'Argument expected after keyValue' before the
    activity runs). Nested-quoted, the blank token reaches the app isNotBlank guard."""
    adb("shell", "am", "force-stop", PKG)
    time.sleep(0.5)
    adb("logcat", "-c")
    cmd = (f"am start -n {COMP} -a android.intent.action.VIEW "
           f"-d 'ui://hermetica-z/cte/keys' --ei inject 1 "
           f"-e keyRef {key_ref} -e keyValue '{raw_value}'")
    adb("shell", cmd)
    time.sleep(1.2)
    return adb("logcat", "-d", "-s", "CteKeysActivity:*", "KeyVault:*")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real-key-ref")
    ap.add_argument("--real-key-value")
    a = ap.parse_args()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"\n=== Keyboard<->Vault Key Injection Tests ({ts}) ===\n")

    # PRECONDITIONS
    abort = False
    dev = adb("devices")
    p1 = bool(re.search(rf"{re.escape(SERIAL)}\s+device", dev))
    rec("PRE-1", "Device present/authorized", p1, SERIAL + (" online" if p1 else " not found"))
    abort |= not p1

    if not abort:
        path = adb("shell", "pm", "path", PKG)
        p2 = "package:" in path
        rec("PRE-2", "Package installed", p2, path.strip())
        abort |= not p2
    if not abort:
        win = adb("shell", "dumpsys", "window")
        awake = "mAwake=true" in win
        unlocked = "mDreamingLockscreen=false" in win
        p3 = awake and unlocked
        rec("PRE-3", "Device unlocked/awake", p3, f"awake={awake} unlocked={unlocked}")
        if not p3:
            print("  -> KeyVault no-ops while locked. Unlock and re-run.")
        abort |= not p3
    if not abort:
        ls = run_as(f"ls {PREFS}")
        p4 = "florisboard_ai_keyvault.xml" in ls
        rec("PRE-4", "run-as access", p4, ls.strip())
        abort |= not p4
    if not abort:
        tj = run_as("cat files/cte/configs/triggers.json")
        p5 = '"providers"' in tj
        rec("PRE-5", "triggers.json present", p5, "providers found" if p5 else "missing")
        abort |= not p5

    if abort:
        print("\nPreconditions failed — aborting before any mutation.\n")
        sys.exit(2)

    # Snapshot
    snap = tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="w", encoding="utf-8")
    snap.write(run_as(f"cat {PREFS}"))
    snap.close()
    base = entry_count()
    print(f"\nBaseline entry count: {base}  (snapshot: {snap.name})\n")

    # TC-1 happy path
    val = "sk-test-" + uuid.uuid4().hex[:12]
    log = inject({"inject": 1, "keyRef": TEST_REF, "keyValue": val})
    m = re.search(rf"Key injected via ADB: {re.escape(TEST_REF)} \((\d+) chars\)", log)
    logged = int(m.group(1)) if m else -1
    c1 = entry_count()
    rec("TC-1", "Happy-path inject", bool(m) and logged == len(val) and c1 > base,
        f"loggedChars={logged} expected={len(val)} count {base}->{c1}")

    # TC-2 trim (shell variant so padding survives device tokenizer)
    log = inject_shell(TEST_REF, "  sk-pad  ")
    m = re.search(r"\((\d+) chars\)", log)
    tn = int(m.group(1)) if m else -1
    rec("TC-2", "Trim behaviour", tn == len("sk-pad"), f"loggedChars={tn} expectedTrim=6")

    # TC-3 blank value (shell variant; whitespace reaches isNotBlank guard)
    cpre = entry_count()
    log = inject_shell(TEST_REF, "   ")
    cpost = entry_count()
    rej = "missing keyRef or keyValue extras" in log
    rec("TC-3", "Blank value rejected", rej and cpost == cpre, f"reject={rej} count {cpre}->{cpost}")

    # TC-4 missing keyValue
    cpre = entry_count()
    log = inject({"inject": 1, "keyRef": TEST_REF})
    cpost = entry_count()
    rej = "missing keyRef or keyValue extras" in log
    rec("TC-4", "Missing keyValue rejected", rej and cpost == cpre, f"reject={rej} count {cpre}->{cpost}")

    # TC-5 missing keyRef
    cpre = entry_count()
    log = inject({"inject": 1, "keyValue": "sk-orphan"})
    cpost = entry_count()
    rej = "missing keyRef or keyValue extras" in log
    rec("TC-5", "Missing keyRef rejected", rej and cpost == cpre, f"reject={rej} count {cpre}->{cpost}")

    # TC-6 inject off
    cpre = entry_count()
    log = inject({"inject": 0, "keyRef": TEST_REF, "keyValue": "sk-noinject"})
    cpost = entry_count()
    no_inject = "Key injected via ADB" not in log
    rec("TC-6", "inject=0 no write", no_inject and cpost == cpre, f"noInject={no_inject} count {cpre}->{cpost}")
    adb("shell", "am", "force-stop", PKG)

    # TC-8 idempotent
    cpre = entry_count()
    inject({"inject": 1, "keyRef": TEST_REF, "keyValue": "first-aaaa"})
    inject({"inject": 1, "keyRef": TEST_REF, "keyValue": "second-bbbb"})
    cpost = entry_count()
    rec("TC-8", "Idempotent overwrite", cpost <= cpre + 1, f"count {cpre}->{cpost} (expected <= +1)")

    # TC-7 real key
    if a.real_key_ref or a.real_key_value:
        if not (a.real_key_ref and a.real_key_value):
            rec("TC-7", "Real-provider roundtrip", False, "need both --real-key-ref and --real-key-value")
        else:
            log = inject({"inject": 1, "keyRef": a.real_key_ref, "keyValue": a.real_key_value})
            ok = f"Key injected via ADB: {a.real_key_ref}" in log
            rec("TC-7", "Real-provider roundtrip", ok, f"ref={a.real_key_ref} (NOT auto-restored)")

    # TEARDOWN
    print("\nRestoring KeyVault prefs from snapshot...")
    dev_tmp = f"/data/local/tmp/keyvault_restore_{ts}.xml"
    adb("push", snap.name, dev_tmp)
    run_as(f"cp {dev_tmp} {PREFS}")
    adb("shell", "rm", "-f", dev_tmp)
    adb("shell", "am", "force-stop", PKG)
    final = entry_count()
    rec("TEARDOWN", "Restore baseline", final == base, f"count now {final} (baseline {base})")
    if final != base:
        print(f"  -> WARNING: count differs. Snapshot kept at {snap.name}")

    core = [r for r in results if r[0].startswith("TC-") and r[0] != "TC-7"]
    pre = [r for r in results if r[0].startswith("PRE-")]
    verdict = "PASS" if all(r[2] for r in core) and all(r[2] for r in pre) else "FAIL"
    print(f"\n================ RESULT: {verdict} ================")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
