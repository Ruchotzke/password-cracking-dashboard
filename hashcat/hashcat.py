def run_hashcat_with_output(hashcat_args):
    """Run hashcat and forward stdout in real-time"""

    # Build the command
    cmd = ['hashcat'] + hashcat_args

    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        universal_newlines=True,
        bufsize=1  # Line buffered
    )

    # Read and forward output line by line
    try:
        for line in process.stdout:
            print("+++++++++: " + line)
            line = line.strip().split(":")
            if line[0].startswith("Session"):
                # We need to read the rest into an object
                # Current session
                print("\n\nUPDATE")
            elif line[0].startswith("Status"):
                # Status of this queued task
                print(line[1])
            elif line[0].startswith("Hash.Mode"):
                # Current hash mode
                continue
            elif line[0].startswith("Hash.Target"):
                # Targeted hash
                continue
            elif line[0].startswith("Time.Started"):
                # Start time for this task
                print(line[1:])
            elif line[0].startswith("Time.Estimated"):
                # Estimated end time for this task
                print(line[1:])
            elif line[0].startswith("Kernel"):
                # Kernel Feature
                continue
            elif line[0].startswith("Guess.Mask"):
                # Current mask
                print(line[1])
            elif line[0].startswith("Guess.Charset"):
                # Current charsets
                continue
            elif line[0].startswith("Guess.Queue"):
                # Current queued task
                continue
            elif line[0].startswith("Speed"):
                # Current hashing speed
                print(line[1])
            elif line[0].startswith("Recovered"):
                # How many hashes have been recovered
                print(f"Recovered: {line[1]}")
            elif line[0].startswith("Progress"):
                # Current progress through this set of guesses
                print(line[1])
            elif line[0].startswith("Rejected"):
                # No idea
                continue
            elif line[0].startswith("Restore.Point"):
                # Restore point
                continue
            elif line[0].startswith("Restore.Sub"):
                # ???
                continue
            elif line[0].startswith("Candidate.Engine"):
                # ???
                continue
            elif line[0].startswith("Candidates"):
                # Current guess candidates for this status message
                print(line[1])
            elif line[0].startswith("Hardware"):
                # Current hardware status
                continue
            else:
                # Not part of the status, so this must be a hash!
                print("\n\n" + str(line))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        process.terminate()

    # Wait for process to complete
    return_code = process.wait()
    print(f"\nHashcat finished with return code: {return_code}")
    return return_code


# Example usage
if __name__ == "__main__":
    args = [
        '-m', '0',                                          # MD5
        'md5.txt',                                          # Hash file
        '-a', '3',                                          # Brute force attack
        '-1', '?l?d!@#$%',                                  # Mask
        '?1?1?1?1?1?1?1?1?1?1',                             # Mask
        "-i",                                               # Iterate through mask by length
        "--quiet",                                          # Don't output garbage
        "--status",                                         # Output status continually
        "--status-timer", "1",                              # Output status every second
        "--potfile-disable"                                 # No potfile!
    ]

    run_hashcat_with_output(args)