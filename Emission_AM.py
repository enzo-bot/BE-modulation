#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Emission_AM
# Author: slamnia
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from gnuradio import audio
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio import vocoder
from gnuradio import qtgui

class Emission_AM(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Emission_AM")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Emission_AM")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
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
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 44.1e3*8
        self.sampPerSymbol = sampPerSymbol = 2
        self.pskType = pskType = 3
        self.center_freq = center_freq = 433.5e6

        ##################################################
        # Blocks
        ##################################################
        self.vocoder_cvsd_decode_bf_0 = vocoder.cvsd_decode_bf(8,0.5)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0.set_gain(50, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=8,
                taps=None,
                fractional_bw=None)
        self.digital_psk_demod_0 = digital.psk.psk_demod(
            constellation_points=2**pskType,
            differential=True,
            samples_per_symbol=sampPerSymbol,
            excess_bw=0.35,
            phase_bw=6.28/100.0,
            timing_bw=6.28/100.0,
            mod_code="gray",
            verbose=False,
            log=False)
        self.audio_sink_0_0 = audio.sink(44100, '', True)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_psk_demod_0, 0), (self.vocoder_cvsd_decode_bf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.audio_sink_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.digital_psk_demod_0, 0))
        self.connect((self.vocoder_cvsd_decode_bf_0, 0), (self.rational_resampler_xxx_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Emission_AM")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_sampPerSymbol(self):
        return self.sampPerSymbol

    def set_sampPerSymbol(self, sampPerSymbol):
        self.sampPerSymbol = sampPerSymbol

    def get_pskType(self):
        return self.pskType

    def set_pskType(self, pskType):
        self.pskType = pskType

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_source_0.set_center_freq(self.center_freq, 0)



def main(top_block_cls=Emission_AM, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()
    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
