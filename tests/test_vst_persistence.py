"""
Test Virtual State Tree (VST) Persistence & POSIX Inode Consistency
Verifies that files created, modified, and removed persist deterministically
and that dynamic /proc entries reflect monotonic system state.
"""
import pytest
from backend.member1_deception_engine.vst_state_tree import VSTStateTree
from backend.member1_deception_engine.fast_path_router import FastPathRouter


def test_initial_fs_structure():
    vst = VSTStateTree()
    ok, passwd = vst.read_file("/etc/passwd")
    assert ok is True
    assert "ubuntu:x:1000:1000" in passwd

    ok, os_rel = vst.read_file("/etc/os-release")
    assert ok is True
    assert "Ubuntu 22.04.5 LTS" in os_rel


def test_file_creation_and_persistence():
    vst = VSTStateTree()
    router = FastPathRouter(vst)

    # Fast-path touch
    res = router.execute("touch /tmp/canary_file.txt")
    assert res["exit_code"] == 0
    assert res["latency_ms"] < 25.0

    # Write content via redirection
    router.execute("echo 'CHAMELEONSHELL_PAYLOAD_TEST' > /tmp/canary_file.txt")

    # Read back through VST
    ok, content = vst.read_file("/tmp/canary_file.txt")
    assert ok is True
    assert "CHAMELEONSHELL_PAYLOAD_TEST" in content

    # Directory listing contains the file
    ok, ls_out = vst.list_dir("/tmp")
    assert ok is True
    assert "canary_file.txt" in ls_out


def test_directory_creation_and_cd():
    vst = VSTStateTree()
    router = FastPathRouter(vst)

    router.execute("mkdir -p /home/ubuntu/nested/project")
    router.execute("cd /home/ubuntu/nested/project")
    assert vst.current_working_dir == "/home/ubuntu/nested/project"

    router.execute("pwd")
    assert router.execute("pwd")["stdout"].strip() == "/home/ubuntu/nested/project"


def test_dynamic_proc_monotonic_clock():
    vst = VSTStateTree()
    ok, uptime1 = vst.read_file("/proc/uptime")
    assert ok is True
    val1 = float(uptime1.split()[0])

    ok, uptime2 = vst.read_file("/proc/uptime")
    assert ok is True
    val2 = float(uptime2.split()[0])

    assert val2 >= val1
    assert val1 > 0.0

    ok, meminfo = vst.read_file("/proc/meminfo")
    assert ok is True
    assert "MemTotal:       32880128 kB" in meminfo


def test_permission_boundaries():
    vst = VSTStateTree()
    # Ubuntu user cannot read /etc/shadow
    ok, msg = vst.read_file("/etc/shadow")
    assert ok is False
    assert "Permission denied" in msg
