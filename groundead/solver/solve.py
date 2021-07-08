import os
import sys
import socket
import time

if __name__ == "__main__":

    # get host from environment
    host = os.getenv("CHAL_HOST")
    if not host:
        print("No HOST supplied from environment")
        sys.exit(-1)

    # get port from environment
    port = int(os.getenv("CHAL_PORT", "0"))
    if port == 0:
        print("No PORT supplied from environment")
        sys.exit(-1)

    # get ticket from environment
    ticket = os.getenv("TICKET")

    # connect to service
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # pass ticket to ticket-taker
    if ticket:
        prompt = s.recv(128)  # "Ticket please:"
        s.send((ticket + "\n").encode("utf-8"))
        print("Sent Ticket")

    try:
        for i in range(5):            
            # hex_string = "0FFFC07F000D071ACFFC1D0F80C07F000008"  # WORKS
            # hex_string = "0FFFC07F000F07AA171ACFFC1D0F80C07F000008"  # WORKS
            hex_string = "0FFFC07F000F07AA171ACFFC1D0F80C07F000008BBAABBCCDD1ACFFC1D0F0FC07F000407DEADBEEF" # ORIGINAL

            s.send(hex_string.encode())

            time.sleep(1)

            received = s.recv(4096)

            print(f"{received.decode('utf-8')}")

    except socket.error:
        pass

    finally:
        s.close()
