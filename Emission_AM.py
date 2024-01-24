#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Emission_AM
# Author: slamnia
# GNU Radio version: 3.10.8.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import vocoder
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



class Emission_AM(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Emission_AM", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Emission_AM")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "Emission_AM")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.timeErrorDetectionGain = timeErrorDetectionGain = 1
        self.samp_rate = samp_rate = 44100
        self.sampPerSymbol = sampPerSymbol = 2
        self.pskType = pskType = 2
        self.ook = ook = digital.constellation_calcdist([1+1j, 1-1j, -1+1j, -1-1j], [0, 1, 2, 3],
        4, 1, digital.constellation.AMPLITUDE_NORMALIZATION).base()
        self.ook.set_npwr(1.0)
        self.loop_bandwidth = loop_bandwidth = 0.06
        self.center_freq = center_freq = 500000000

        ##################################################
        # Blocks
        ##################################################

        self.vocoder_cvsd_encode_fb_0 = vocoder.cvsd_encode_fb(8,0.5)
        self.vocoder_cvsd_decode_bf_0 = vocoder.cvsd_decode_bf(8,0.5)
        self._timeErrorDetectionGain_range = Range(0, 10, 0.1, 1, 200)
        self._timeErrorDetectionGain_win = RangeWidget(self._timeErrorDetectionGain_range, self.set_timeErrorDetectionGain, "'timeErrorDetectionGain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._timeErrorDetectionGain_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=8,
                taps=[],
                fractional_bw=0)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=ook,
            differential=False,
            samples_per_symbol=sampPerSymbol,
            pre_diff_code=True,
            excess_bw=0.35,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(ook)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/bina/Documents/lmms/projects/wheelies_on.4.wav', True)
        self.audio_sink_0_0 = audio.sink(44100, '', True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_wavfile_source_0, 0), (self.vocoder_cvsd_encode_fb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.vocoder_cvsd_decode_bf_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.audio_sink_0_0, 0))
        self.connect((self.vocoder_cvsd_decode_bf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.vocoder_cvsd_encode_fb_0, 0), (self.digital_constellation_modulator_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Emission_AM")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_timeErrorDetectionGain(self):
        return self.timeErrorDetectionGain

    def set_timeErrorDetectionGain(self, timeErrorDetectionGain):
        self.timeErrorDetectionGain = timeErrorDetectionGain

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_sampPerSymbol(self):
        return self.sampPerSymbol

    def set_sampPerSymbol(self, sampPerSymbol):
        self.sampPerSymbol = sampPerSymbol

    def get_pskType(self):
        return self.pskType

    def set_pskType(self, pskType):
        self.pskType = pskType

    def get_ook(self):
        return self.ook

    def set_ook(self, ook):
        self.ook = ook
        self.digital_constellation_decoder_cb_0.set_constellation(self.ook)

    def get_loop_bandwidth(self):
        return self.loop_bandwidth

    def set_loop_bandwidth(self, loop_bandwidth):
        self.loop_bandwidth = loop_bandwidth

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq




def main(top_block_cls=Emission_AM, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
