import os
import sys
import socket
import time
import re
from math import log10

class LinkySolver:
    def __init__(self):
        self.c_ms = 299792458
        self.boltzmanns_dBW_K_Hz = 10*log10(1.3803E-23)

        self.Frequency_Hz =  None
        self.lambda_m = None
        self.Dr_m =  None
        self.Rx_Antenna_efficiency =  None
        self.Tsystem_K =  None
        self.Rx_line_loss = None
        self.data_rate_bps =  None
        self.demod_implementation_loss_dB =  None
        self.Rx_Beamwidth_deg = None
        self.Rx_Pointing_error_deg =  None
        self.Rx_Pointing_loss_dB = None
        self.Path_length_km =  None
        self.Path_loss_db = None
        self.Polarization_loss_db = None
        self.Atmospheric_loss_db =  None
        self.Ionospheric_loss_db =  None
        self.Gt_dB =  None
        self.Tx_line_loss_dB =  None
        self.Tx_Pointing_loss_dB = None

        self.Gr_dB = None
        self.G_T_dB_K = None
        self.rssi_dBW = None
        self.SNo_dBHz = None
        self.eb_no_dB = None
        self.required_eb_no_ber_dB = None
        self.Tx_EIRP_dBW = None
        self.Pt_W = None
        self.Pt_dBW = None


    def calculate_gain(self):
        self.Gr_db = 20.4+20*log10(self.Dr_m)+20*log10(self.Frequency_Hz/1E9)+10*log10(self.Rx_Antenna_efficiency)
        return self.Gr_db

    def calculate_G_T(self):
        self.G_T_dB_K = self.Gr_db + self.Rx_line_loss - 10*log10(self.Tsystem_K)
        return self.G_T_dB_K
    
    def calculate_Pt(self):
        # Calculate required S/No to achive 10 dB of margin on top of 4.4 BER requirement
        self.SNo_dBHz = 10 + self.required_eb_no_ber_dB + 10*log10(self.data_rate_bps) - self.demod_implementation_loss_dB
        # print(self.SNo_dBHz)

        # Calculate receive pointing loss - We also give this to them after getting gain right
        self.Rx_Beamwidth_deg = 21/(self.Frequency_Hz/1E9*self.Dr_m)
        # print(self.Rx_Beamwidth_deg)

        self.Rx_Pointing_loss_dB = -12*(self.Rx_Pointing_error_deg/self.Rx_Beamwidth_deg)**2
        # print(self.Rx_Pointing_loss_dB)

        # Calculate Path Loss
        self.Path_loss_db = -(22+20*log10((self.Path_length_km*1E3)/self.lambda_m))
        # print(self.Path_loss_db)

        # Calculate the required RSSI
        self.rssi_dBW = self.SNo_dBHz - self.Rx_Pointing_loss_dB + self.boltzmanns_dBW_K_Hz - self.G_T_dB_K
        # print(self.rssi_dBW)

        # Calculate required EIRP
        self.Tx_EIRP_dBW = self.rssi_dBW - self.Path_loss_db - self.Polarization_loss_db - self.Atmospheric_loss_db - self.Ionospheric_loss_db - self.Tx_Pointing_loss_dB
        # print(self.Tx_EIRP_dBW)

        # Calculate required Pt (W)
        self.Pt_dBW = self.Tx_EIRP_dBW - self.Gt_dB - self.Tx_line_loss_dB
        self.Pt_W = 10**(self.Pt_dBW/10)
        # print(self.Pt_W)
        return self.Pt_W

    def handle_challenge_intro(self,intro):
        # Didn't do anything to make this robust.  If you change the challenge output, this will need updating
        # It reads the values provided by the challenge versus hardcoding the same values between the solver and challenge
        self.Frequency_Hz =  float(re.findall("Frequency \(Hz\): ([0-9.]*)", intro)[0])
        self.lambda_m = self.c_ms / self.Frequency_Hz
        self.Dr_m =  float(re.findall("Receive Antenna Diameter \(m\): ([0-9.]*)", intro)[0])
        self.Rx_Antenna_efficiency =  float(re.findall("Receive Antenna Efficiency: ([0-9.]*)", intro)[0])
        self.Tsystem_K =  float(re.findall("Receive System Noise Temperature \(K\): ([0-9.]*)", intro)[0])
        self.Rx_line_loss =  float(re.findall("Receive Line Loss \(antenna to LNA\) \(dB\): ([0-9.\-]*)", intro)[0])
        self.data_rate_bps =  float(re.findall("Data Rate \(bps\): ([0-9.]*)", intro)[0])
        self.demod_implementation_loss_dB =  float(re.findall("Receive Demodulator Implementation Loss \(dB\): ([0-9.\-]*)", intro)[0])
        self.Rx_Pointing_error_deg =  float(re.findall("Receive Pointing Error \(deg\): ([0-9.]*)", intro)[0])
        self.Path_length_km =  float(re.findall("Path Length \(km\): ([0-9.]*)", intro)[0])
        self.Path_loss_db = -(22+20*log10((self.Path_length_km*1E3)/self.lambda_m))
        self.Polarization_loss_db =  float(re.findall("Polarization Loss \(dB\): ([0-9.\-]*)", intro)[0])
        self.Atmospheric_loss_db =  float(re.findall("Atmospheric Loss \(dB\): ([0-9.\-]*)", intro)[0])
        self.Ionospheric_loss_db =  float(re.findall("Ionospheric Loss \(dB\): ([0-9.\-]*)", intro)[0])
        self.Gt_dB =  float(re.findall("Transmit Antenna Gain \(dBi\): ([0-9.]*)", intro)[0])
        self.Tx_line_loss_dB =  float(re.findall("Transmit Line Losses \(dB\): ([0-9.\-]*)", intro)[0])
        self.Tx_Pointing_loss_dB =  float(re.findall("Transmit Pointing Loss \(dB\): ([0-9.\-]*)", intro)[0])
        self.required_eb_no_ber_dB =  float(re.findall("Required Eb/No for BER \(dB\): ([0-9.\-]*)", intro)[0])



if __name__ == "__main__":
    # get host from environment
    host = os.getenv("CHAL_HOST")
    if not host:
        print("No HOST supplied from environment")
        sys.exit(-1)

    # get port from environment
    port = int(os.getenv("CHAL_PORT","0"))
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

    challenge = s.recv(2048)
    challenge = challenge.decode('UTF-8')
    print("\n************************   SOLVER: Receiving Challenge   ************************")

    print(challenge, end = '')

    solver = LinkySolver()
    solver.handle_challenge_intro(challenge)

    # Solve Gain part of challenge
    gain = solver.calculate_gain()
    response = str(gain) + "\n"
    print(gain)
    s.send(response.encode("utf-8"))
    print("\n************************   SOLVER: Solved Part 1   ************************")

    challenge = s.recv(2048)
    challenge = challenge.decode('UTF-8')
    print(challenge, end = '')

    # Solve G/T part of challenge
    G_T = solver.calculate_G_T()
    response = str(G_T) + "\n"
    print(G_T)
    s.send(response.encode("utf-8"))
    print("\n************************   SOLVER: Solved Part 2   ************************")

    challenge = s.recv(2048)
    challenge = challenge.decode('UTF-8')
    print(challenge, end = '')

    # Solve Pt part of challenge
    Pt = solver.calculate_Pt()
    response = str(Pt) + "\n"
    print(Pt)
    s.send(response.encode("utf-8"))
    print("\n************************   SOLVER: Solved Part 3   ************************")


    challenge = s.recv(2048)
    challenge = challenge.decode('UTF-8')
    print(challenge, end = '')
