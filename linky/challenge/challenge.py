# Link Budget Challenge

import os
import sys

from time import sleep

from math import log10, isclose
# from math import sqrt

# from datetime import datetime

from timeout import timeout, TimeoutError
time = int(os.getenv("TIMEOUT", 180))


class Linky:
    def __init__(self):
        # General Constants
        self.c_ms = 299792458
        self.Frequency_Hz = 12.1E9
        self.lambda_m = self.c_ms / self.Frequency_Hz
        self.boltzmanns_dBW_K_Hz = 10*log10(1.3803E-23)
        # self.boltzmanns_dBW_K_Hz = -228.6

        # Transmit Constants
        self.Tx_line_loss_dB = -1
        self.Tx_Antenna_efficiency = 0.6
        self.Dt_m = 0.066
        self.Gt_dB = 20.4 + 20*log10(self.Dt_m) + 20*log10(self.Frequency_Hz/1E9) + 10*log10(self.Tx_Antenna_efficiency)
        self.Tx_Beamwidth_deg = 21/((self.Frequency_Hz/1E9)*self.Dt_m)
        self.Tx_Pointing_error_deg = 10.0

        # Caluclations for determining size and Gain based on HPBW
        # self.Tx_Beamwidth_deg = 140.0
        # self.Gt_dB = 44.3 - 10*log10(self.Tx_Beamwidth_deg ** 2)
        # self.Dt_m = 21 / (self.Frequency_Hz*self.Tx_Beamwidth_deg)

        # Initial Transmit Power, to be adjusted by user
        self.Pt_W = None
        self.Pt_dBW = None

        self.Tx_Pointing_loss_dB = -12*(self.Tx_Pointing_error_deg/self.Tx_Beamwidth_deg)**2
        self.Tx_EIRP_dBW = None

        # Link Constants
        self.Path_length_km = 2831
        self.Path_loss_db = -(22+20*log10((self.Path_length_km*1E3)/self.lambda_m))
        self.Polarization_loss_db = -0.5
        self.Atmospheric_loss_db = -2.1
        self.Ionospheric_loss_db = -0.1

        # Receive Constants
        self.Dr_m = 5.3
        self.Rx_Antenna_efficiency = 0.55
        self.Rx_line_loss = -2
        self.Gr_dB = None
        self.demod_implementation_loss_dB = -2

        self.Rx_Beamwidth_deg = None
        self.Rx_Pointing_error_deg = 0.2
        self.Rx_Pointing_loss_dB = None
        self.Tsystem_K = 522
        self.data_rate_bps = 10E6


        self.G_T_dB_K = None
        self.rssi_dBW = None
        self.SNo_dBHz = None
        self.eb_no_dB = None
        self.required_eb_no_ber_dB = 4.4
        self.margin_dB = None
    
    def __str__(self):
        output = "************** Global Parameters *****************\n" + \
                 "Frequency (Hz): {0}\n".format(self.Frequency_Hz) + \
                 "Wavelength (m): {0:.3f}\n".format(self.lambda_m) + \
                 "Data Rate (bps): {0}\n".format(self.data_rate_bps) + \
                 "************* Transmit Parameters ****************\n" + \
                 "Transmit Power (W): {0}\n".format(self.Pt_W) + \
                 "Transmit Power (dBW): {0:.2f}\n".format(self.Pt_dBW) + \
                 "Transmit Line Losses (dB): {0}\n".format(self.Tx_line_loss_dB) + \
                 "Transmit Half-power Beamwidth (deg): {0:.2f}\n".format(self.Tx_Beamwidth_deg) + \
                 "Transmit Antenna Gain (dBi): {0:.2f}\n".format(self.Gt_dB) + \
                 "Transmit Pointing Error (deg): {0:.2f}\n".format(self.Tx_Pointing_error_deg) + \
                 "Transmit Pointing Loss (dB): {0:.2f}\n".format(self.Tx_Pointing_loss_dB) + \
                 "Transmit Effective Isotropic Radiated Power (EIRP)(dBW): {0:.2f}\n".format(self.Tx_EIRP_dBW) + \
                 "*************** Path Parameters ******************\n" + \
                 "Path Length (km): {0}\n".format(self.Path_length_km) + \
                 "Polarization Loss (dB): {0}\n".format(self.Polarization_loss_db) + \
                 "Atmospheric Loss (dB): {0}\n".format(self.Atmospheric_loss_db) + \
                 "Ionospheric Loss (dB): {0}\n".format(self.Ionospheric_loss_db) + \
                 "************** Receive Parameters ****************\n" + \
                 "Receive Antenna Diameter (m): {0}\n".format(self.Dr_m) + \
                 "Receive Antenna Efficiency: {0}\n".format(self.Rx_Antenna_efficiency) + \
                 "Receive Antenna Gain (dBi): {0:.2f}\n".format(self.Gr_dB) + \
                 "Receive Half-power Beamwidth (deg): {0:.2f}\n".format(self.Rx_Beamwidth_deg) + \
                 "Receive Pointing Error (deg): {0}\n".format(self.Rx_Pointing_error_deg) + \
                 "Receive Pointing Loss (dB): {0:.2f}\n".format(self.Rx_Pointing_loss_dB) + \
                 "Receive System Noise Temperature (K): {0}\n".format(self.Tsystem_K) + \
                 "Receive Line Loss (antenna to LNA) (dB): {0}\n".format(self.Rx_line_loss) + \
                 "******************* Results **********************\n" + \
                 "RSSI (dBW): {0:.2f}\n".format(self.rssi_dBW) + \
                 "G/T (dB/K): {0:.2f}\n".format(self.G_T_dB_K) + \
                 "S/No (dB-HZ): {0:.2f}\n".format(self.SNo_dBHz) + \
                 "Eb/No (dB): {0:.2f}\n".format(self.eb_no_dB) + \
                 "Receive Demodulator Implementation Loss (dB): {0}\n".format(self.demod_implementation_loss_dB) + \
                 "Required Eb/No for BER (dB): {0}\n".format(self.required_eb_no_ber_dB) + \
                 "Margin(dB): {0:.2f}\n" .format(self.margin_dB)                
        return output

    def print_initial_state(self):
        output = "************** Global Parameters *****************\n" + \
                 "Frequency (Hz): {0}\n".format(self.Frequency_Hz) + \
                 "Wavelength (m): {0:.3f}\n".format(self.lambda_m) + \
                 "Data Rate (bps): {0}\n".format(self.data_rate_bps) + \
                 "************* Transmit Parameters ****************\n" + \
                 "Transmit Line Losses (dB): {0}\n".format(self.Tx_line_loss_dB) + \
                 "Transmit Half-power Beamwidth (deg): {0:.2f}\n".format(self.Tx_Beamwidth_deg) + \
                 "Transmit Antenna Gain (dBi): {0:.2f}\n".format(self.Gt_dB) + \
                 "Transmit Pointing Error (deg): {0:.2f}\n".format(self.Tx_Pointing_error_deg) + \
                 "Transmit Pointing Loss (dB): {0:.2f}\n".format(self.Tx_Pointing_loss_dB) + \
                 "*************** Path Parameters ******************\n" + \
                 "Path Length (km): {0}\n".format(self.Path_length_km) + \
                 "Polarization Loss (dB): {0}\n".format(self.Polarization_loss_db) + \
                 "Atmospheric Loss (dB): {0}\n".format(self.Atmospheric_loss_db) + \
                 "Ionospheric Loss (dB): {0}\n".format(self.Ionospheric_loss_db) + \
                 "************** Receive Parameters ****************\n" + \
                 "Receive Antenna Diameter (m): {0}\n".format(self.Dr_m) + \
                 "Receive Antenna Efficiency: {0}\n".format(self.Rx_Antenna_efficiency) + \
                 "Receive Pointing Error (deg): {0}\n".format(self.Rx_Pointing_error_deg) + \
                 "Receive System Noise Temperature (K): {0}\n".format(self.Tsystem_K) + \
                 "Receive Line Loss (antenna to LNA) (dB): {0}\n".format(self.Rx_line_loss) + \
                 "Receive Demodulator Implementation Loss (dB): {0}\n".format(self.demod_implementation_loss_dB) + \
                 "Required Eb/No for BER (dB): {0}\n".format(self.required_eb_no_ber_dB)      
        print(output)

    def calculate_rx_gain(self):
        self.Gr_dB = 20.4 + 20*log10(self.Dr_m) + 20*log10(self.Frequency_Hz/1E9) + 10*log10(self.Rx_Antenna_efficiency)

    def calculate_rx_params_from_gain(self):
        self.Rx_Beamwidth_deg = 21/((self.Frequency_Hz/1E9)*self.Dr_m)
        self.Rx_Pointing_loss_dB = -12*(self.Rx_Pointing_error_deg/self.Rx_Beamwidth_deg)**2
        print("Receive Antenna Gain (dBi): {0:.2f}\n".format(self.Gr_dB) + \
              "Receive Half-power Beamwidth (deg): {0:.2f}\n".format(self.Rx_Beamwidth_deg) + \
              "Receive Pointing Error (deg): {0}\n".format(self.Rx_Pointing_error_deg) + \
              "Receive Pointing Loss (dB): {0:.2f}\n".format(self.Rx_Pointing_loss_dB))

    def calculate_rx_G_T(self):
        self.G_T_dB_K = self.Gr_dB + self.Rx_line_loss - 10*log10(self.Tsystem_K)

    def calculate_budget(self,user_Pt_W):
        self.Pt_W = user_Pt_W
        self.Pt_dBW = 10*log10(self.Pt_W)
        self.Tx_EIRP_dBW = self.Pt_dBW + self.Gt_dB + self.Tx_line_loss_dB
        self.rssi_dBW = self.Tx_EIRP_dBW + self.Tx_Pointing_loss_dB + self.Path_loss_db + self.Polarization_loss_db + self.Atmospheric_loss_db + self.Ionospheric_loss_db
        # Need to use the G/T provided because a small rounding error between what we calculate and what a user
        # provides can drive a difference through the remaining calculations
        self.SNo_dBHz = self.rssi_dBW + self.Rx_Pointing_loss_dB - self.boltzmanns_dBW_K_Hz + self.G_T_dB_K
        self.eb_no_dB = self.SNo_dBHz - 10*log10(self.data_rate_bps)
        self.margin_dB = self.eb_no_dB - self.required_eb_no_ber_dB + self.demod_implementation_loss_dB
        return self.margin_dB


def render_intro():
    antenna = [
    " _     _       _",    
    "| |   (_)_ __ | | ___   _", 
    "| |   | | '_ \| |/ / | | |",
    "| |___| | | | |   <| |_| |",
    "|_____|_|_| |_|_|\_\\\__, |",
    "                    |___/", 
    "    .-.",
    "   (;;;)",
    "    \_|",
    "      \ _.--l--._",
    "     . \    |     `.",
    "   .` `.\   |    .` `.",
    " .`     `\  |  .`     `.",
    "/ __      \.|.`      __ \/",
    "|   ''--._ \V  _.--''   |",
    "|        _ (\") _        |",
    "| __..--'   ^   '--..__ | ",
    "\         .`|`.         /-.)",
    " `.     .`  |  `.     .`",
    "   `. .`    |    `. .`",
    "     `._    |    _.`|",
    "         `--l--`  | |",
    "                  | |",
    "                  | |",
    "                  | |",
    "         o        | |     o",
    "          )    o  | |    (",
    "         \|/  (   | |   \|/",
    "             \|/  | | o  WWwwwW",
    "                o | |  )  ",
    "        WWwwWww ( | | \|/",
    "               \|/WWwwWWwW",
    ]
    # Challenge Intro
    for row in antenna:
        print(row)
        # time.sleep(0.02)
        sleep(0.02)

    print("\n\nOur satellite has launched, but the user documentation and Critical Design Review package ")
    print("for the Telemetry link are missing a few key details. Fill in the details to configure")
    print("the Telemetry Transmitter and solve the challenge.\n\n")

@timeout(time)
def challenge():

    link_budget = Linky()

    print("Here's the information we have captured\n")
    link_budget.print_initial_state()

    # Antenna Gain Question - get value, check against truth +/- tolerance
    # If the value is close, set truth to the user data and continue
    print("Calculate and provide the receive antenna gain in dBi: ",end='')

    user_rx_gain = None

    try:
        user_rx_gain = float(input())
    except ValueError:
        print("\nWrong answer! You lose.\n")
        return False

    link_budget.calculate_rx_gain()
    if (isclose(user_rx_gain,link_budget.Gr_dB, abs_tol=0.1)):
        print("\nGood job.  You get to continue")
        link_budget.Gr_dB = user_rx_gain
        link_budget.calculate_rx_params_from_gain()
    else:
        print("Wrong answer! You lose.")
        return False

    # Receive G/T Question - Calculate G/T from Antenna Gain, Rx Line Loss, and System G/T
    print("Okay, now we know the receive antenna gain.\nCalculate and provide the ground terminal G/T (dB/K): ", end='')

    user_rx_G_T = None

    try:
        user_rx_G_T = float(input())
    except ValueError:
        print("\nWrong answer! You lose.\n")
        return False

    link_budget.calculate_rx_G_T()
    if (isclose(user_rx_G_T,link_budget.G_T_dB_K,abs_tol=0.1)):
        print("\nNicely done.  Let's keep going.\n")
        link_budget.G_T_dB_K = user_rx_G_T
    else:
        print("Wrong answer! You lose.")
        return False

    # Transmit power to obtain 10dB of Eb/No margin
    print("Determine the transmit power (in W) to achieve 10dB of Eb/No margin (above minimum for BER): ", end='')

    user_Pt_W = None

    try:
        user_Pt_W = float(input())
    except ValueError:
        print("\nWrong answer! You lose.\n")
        return False

    actual_margin = link_budget.calculate_budget(user_Pt_W)
    # print("actual margin: {0}".format(actual_margin))
    if(isclose(actual_margin,10.0,abs_tol=0.1)):
        print("\nWinner Winner Chicken Dinner\n")
        print(link_budget)
        return True
    else:
        print("Sorry, you lost")
        return False


if __name__ == "__main__":

    render_intro()

    try:
        success = challenge()
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)

    if success:
        print("You got it! Here's your flag:")
        flag = os.getenv('FLAG')
        print(flag)
    else:
        print("Wrong! Maybe next time.")
