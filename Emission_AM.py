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
from gnuradio import iio
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
        self.qpsk = qpsk = digital.constellation_qpsk().base()
        self.qpsk.set_npwr(1.0)
        self.timeErrorDetectionGain = timeErrorDetectionGain = 1
        self.samp_rate = samp_rate = 44100*8
        self.sampPerSymbol = sampPerSymbol = 2
        self.pskType = pskType = 2
        self.center_freq = center_freq = 500000000
        self.CMA_algo = CMA_algo = digital.adaptive_algorithm_cma( qpsk, .0001, 4).base()

        ##################################################
        # Blocks
        ##################################################

        self._timeErrorDetectionGain_range = Range(0, 10, 0.1, 1, 200)
        self._timeErrorDetectionGain_win = RangeWidget(self._timeErrorDetectionGain_range, self.set_timeErrorDetectionGain, "'timeErrorDetectionGain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._timeErrorDetectionGain_win)
        self.vocoder_cvsd_decode_bf_0 = vocoder.cvsd_decode_bf(8,0.5)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=8,
                taps=[],
                fractional_bw=0)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('' if '' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(center_freq)
        self.iio_pluto_source_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_MUELLER_AND_MULLER,
            2,
            0.045,
            1.0,
            timeErrorDetectionGain,
            1.5,
            4,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_psk_demod_0 = digital.psk.psk_demod(
            constellation_points=(2**pskType),
            differential=True,
            samples_per_symbol=sampPerSymbol,
            excess_bw=0.35,
            phase_bw=(6.28/100.0),
            timing_bw=(6.28/100.0),
            mod_code="gray",
            verbose=False,
            log=False)
        self.digital_linear_equalizer_0 = digital.linear_equalizer(5, 2, CMA_algo, False, [ ], 'corr_est')
        self.audio_sink_0_0 = audio.sink(44100, '', True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_linear_equalizer_0, 0), (self.digital_psk_demod_0, 0))
        self.connect((self.digital_psk_demod_0, 0), (self.vocoder_cvsd_decode_bf_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_linear_equalizer_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.audio_sink_0_0, 0))
        self.connect((self.vocoder_cvsd_decode_bf_0, 0), (self.rational_resampler_xxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Emission_AM")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_qpsk(self):
        return self.qpsk

    def set_qpsk(self, qpsk):
        self.qpsk = qpsk

    def get_timeErrorDetectionGain(self):
        return self.timeErrorDetectionGain

    def set_timeErrorDetectionGain(self, timeErrorDetectionGain):
        self.timeErrorDetectionGain = timeErrorDetectionGain
        self.digital_symbol_sync_xx_0.set_ted_gain(self.timeErrorDetectionGain)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_pluto_source_0.set_samplerate(self.samp_rate)

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
        self.iio_pluto_source_0.set_frequency(self.center_freq)

    def get_CMA_algo(self):
        return self.CMA_algo

    def set_CMA_algo(self, CMA_algo):
        self.CMA_algo = CMA_algo




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
