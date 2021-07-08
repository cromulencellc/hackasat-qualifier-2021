#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: QPSK CCSDS RX
# Author: Cromulence
# Description: QPSK and CSSDS FEC
# GNU Radio version: 3.7.13.5
##################################################


from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import fec
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import cmath
import math
import pmt


class qpsk_ccsds_demod(gr.top_block):

    def __init__(self, frame_size=10, puncpat='11'):
        gr.top_block.__init__(self, "QPSK CCSDS RX")

        ##################################################
        # Parameters
        ##################################################
        self.frame_size = frame_size
        self.puncpat = puncpat

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 4
        self.rate = rate = 2
        self.polys = polys = [109, 79]
        self.nfilts = nfilts = 32
        self.k = k = 7
        self.samp_rate = samp_rate = 100000
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(nfilts, nfilts, 1.0/float(sps), 0.35, 11*sps*nfilts)


        self.enc_ccsds = enc_ccsds = fec.ccsds_encoder_make(frame_size*8, 0, fec.CC_STREAMING)



        self.dec_cc = dec_cc = fec.cc_decoder.make(frame_size*8, k, rate, (polys), 0, -1, fec.CC_STREAMING, False)


        self.constel = constel = digital.constellation_calcdist(([(1+1j),(-1-1j),(1-1j),(-1+1j)]), (digital.psk_4()[1]), 4, 1).base()

        self.constel.gen_soft_dec_lut(8)
        self.arity = arity = 4

        ##################################################
        # Blocks
        ##################################################
        self.fec_extended_decoder_0 = fec.extended_decoder(decoder_obj_list=dec_cc, threading='capillary', ann=None, puncpat=puncpat, integration_period=10000)
        self.digital_pfb_clock_sync_xxx_0_0 = digital.pfb_clock_sync_ccf(sps, 6.28/100.0, (rrc_taps), nfilts, nfilts/2, 1.5, 1)
        self.digital_constellation_soft_decoder_cf_0_0 = digital.constellation_soft_decoder_cf(constel)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)
        self.blocks_file_source_1 = blocks.file_source(gr.sizeof_gr_complex*1, '/out/intermediate.bin', False)
        self.blocks_file_source_1.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/out/out.bin', False)
        self.blocks_file_sink_0.set_unbuffered(False)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_1, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.digital_pfb_clock_sync_xxx_0_0, 0))
        self.connect((self.digital_constellation_soft_decoder_cf_0_0, 0), (self.fec_extended_decoder_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0_0, 0), (self.digital_constellation_soft_decoder_cf_0_0, 0))
        self.connect((self.fec_extended_decoder_0, 0), (self.blocks_pack_k_bits_bb_0, 0))

    def get_frame_size(self):
        return self.frame_size

    def set_frame_size(self, frame_size):
        self.frame_size = frame_size

    def get_puncpat(self):
        return self.puncpat

    def set_puncpat(self, puncpat):
        self.puncpat = puncpat

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), 0.35, 11*self.sps*self.nfilts))

    def get_rate(self):
        return self.rate

    def set_rate(self, rate):
        self.rate = rate

    def get_polys(self):
        return self.polys

    def set_polys(self, polys):
        self.polys = polys

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), 0.35, 11*self.sps*self.nfilts))

    def get_k(self):
        return self.k

    def set_k(self, k):
        self.k = k

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.digital_pfb_clock_sync_xxx_0_0.update_taps((self.rrc_taps))

    def get_enc_ccsds(self):
        return self.enc_ccsds

    def set_enc_ccsds(self, enc_ccsds):
        self.enc_ccsds = enc_ccsds

    def get_dec_cc(self):
        return self.dec_cc

    def set_dec_cc(self, dec_cc):
        self.dec_cc = dec_cc

    def get_constel(self):
        return self.constel

    def set_constel(self, constel):
        self.constel = constel

    def get_arity(self):
        return self.arity

    def set_arity(self, arity):
        self.arity = arity


def argument_parser():
    description = 'QPSK and CSSDS FEC'
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option, description=description)
    parser.add_option(
        "", "--frame-size", dest="frame_size", type="intx", default=10,
        help="Set Frame Size [default=%default]")
    parser.add_option(
        "", "--puncpat", dest="puncpat", type="string", default='11',
        help="Set puncpat [default=%default]")
    return parser


def main(top_block_cls=qpsk_ccsds_demod, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(frame_size=options.frame_size, puncpat=options.puncpat)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
