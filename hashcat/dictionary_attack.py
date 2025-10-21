import subprocess


def try_dictionary_attack(passwords: list) -> list:
    """
    Attempt a dictionary attack against a list of passwords.
    :param passwords:
    :return: A list of cracked passwords.
    """
    # Make a temp file for the plaintext and hashes
    plaintext_handle = open("plain.txt", "w")
    for password in passwords:
        plaintext_handle.write(password + "\n")

    # Run the hasher to produce a hashfile
    with open("plain.txt", "r") as plaintext_handle, open("md5.txt", "w") as output_file:
        hasher_process = subprocess.Popen(
            ['python', 'hashcat/hasher.py'],
            stdin=plaintext_handle,
            stdout=output_file,
        )
        hasher_process.wait()

    # Run hashcat
    result = subprocess.run(
        ['hashcat',
         '-m1000',
         'md5.txt',
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
        print(line)
        if ":" in line:
            duo = line.split(":")
            cracked.append(duo[1])

    return cracked