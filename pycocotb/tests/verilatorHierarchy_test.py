import unittest

from tempfile import TemporaryDirectory
from pycocotb.hdlSimulator import HdlSimulator
from pycocotb.tests.common import build_sim


class VerilatorHierarchyTC(unittest.TestCase):
    """
    Simple test of verilator simulation wrapper hiearchical access
    """

    def build_sim(self, build_dir):
        DATA_WIDTH = 64
        accessible_signals = [
            # (signal_name, read_only, is_signed, type_width)
            ("clk", 0, 0, 1),
            ("dataIn_data", 0, 0, DATA_WIDTH),
            ("dataIn_rd", 1, 0, 1),
            ("dataIn_vld", 0, 0, 1),
            ("dataOut_data", 1, 0, DATA_WIDTH),
            ("dataOut_rd", 0, 0, 1),
            ("dataOut_vld", 1, 0, 1),
            ("rst_n", 0, 0, 1),
            ("size", 1, 0, 3),
            
            #(("fifo_inst", "clk"), 1, 0, 1),
            #(("fifo_inst", "dataIn_data"), 1, 0, DATA_WIDTH),
            #(("fifo_inst", "dataIn_wait"), 1, 0, 1),
            #(("fifo_inst", "dataIn_en"), 1, 0, 1),
            #(("fifo_inst", "dataOut_data"), 1, 0, DATA_WIDTH),
            #(("fifo_inst", "dataOut_wait"), 1, 0, 1),
            #(("fifo_inst", "dataOut_en"), 1, 0, 1),
            #(("fifo_inst", "rst_n"), 0, 1, 1),
            #(("fifo_inst", "size"), 1, 1, 3),
            (("fifo_inst", "fifo_read"), 1, 0, 1),
            (("fifo_inst", "fifo_write"), 1, 0, 1),
        ]
        files = ["fifo.v", "HandshakedFifo.v"]
        return build_sim(files, accessible_signals, self, build_dir, "HandshakedFifo")
    
    def test_sim_HandshakedFifo(self):
        build_dir = "tmp"
        if True:
        # with TemporaryDirectory() as build_dir:
            rtl_sim = self.build_sim(build_dir)
            io = rtl_sim.io
            sim = HdlSimulator(rtl_sim)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(VerilatorWireTC('test_wire64'))
    suite.addTest(unittest.makeSuite(VerilatorHierarchyTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
