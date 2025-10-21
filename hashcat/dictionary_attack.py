import subprocess
from textual.widgets import Log


def try_dictionary_attack(md5_file: str, log: Log) -> list:
    """
    Attempt a dictionary attack against a list of passwords.
    :param md5_file: The name of a file containing hashes
    :return: A list of cracked passwords.
    """
    # Run hashcat
    result = subprocess.run(
        ['hashcat',
         '-m1000',
         md5_file,
         '-a0',
         '/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt',
         '--quiet',
         '--potfile-disabled'],
        capture_output=True,
        text=True
    )

    # Process the output
    cracked = []
    for line in result.stdout.splitlines():
        log.write_line(line)
        if ":" in line:
            duo = line.split(":")
            cracked.append(duo[1])

    return cracked