import asyncio
import subprocess
from textual.widgets import Log


async def try_dictionary_attack(md5_file: str, log: Log) -> list:
    """
    Attempt a dictionary attack against a list of passwords.
    :param md5_file: The name of a file containing hashes
    :return: A list of cracked passwords.
    """
    # Run hashcat
    log.write_line(f"Awaiting process creation.")
    proc = await asyncio.create_subprocess_shell(
        cmd=f"hashcat -m0 {md5_file} -a0 /usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords.txt --quiet --potfile-disable",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    log.write_line(f"Running hashcat...")
    stdout, stderr = await proc.communicate()
    log.write_line(f"Hashcat returned with code {proc.returncode}. Parsing stdout.")

    # Process the output
    cracked = []
    for line in stdout.splitlines():
        line = line.decode("utf-8").strip()
        if ":" in line:
            duo = line.split(":")
            cracked.append(duo[1])

    return cracked