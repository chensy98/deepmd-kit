# SPDX-License-Identifier: LGPL-3.0-or-later
import unittest
from typing import (
    Any,
)

import numpy as np
import torch

from deepmd.dpmodel.descriptor.dpa2 import (
    RepformerArgs,
    RepinitArgs,
)
from deepmd.env import (
    GLOBAL_NP_FLOAT_PRECISION,
)
from deepmd.pt.model.descriptor.dpa2 import (
    DescrptDPA2,
)
from deepmd.pt.utils.env import DEVICE as PT_DEVICE
from deepmd.pt.utils.nlist import build_neighbor_list as build_neighbor_list_pt
from deepmd.pt.utils.nlist import (
    extend_coord_with_ghosts as extend_coord_with_ghosts_pt,
)

from ...consistent.common import (
    parameterized,
)


def eval_pt_descriptor(
    pt_obj: Any, natoms, coords, atype, box, mixed_types: bool = False
) -> Any:
    ext_coords, ext_atype, mapping = extend_coord_with_ghosts_pt(
        torch.from_numpy(coords).to(PT_DEVICE).reshape(1, -1, 3),
        torch.from_numpy(atype).to(PT_DEVICE).reshape(1, -1),
        torch.from_numpy(box).to(PT_DEVICE).reshape(1, 3, 3),
        pt_obj.get_rcut(),
    )
    nlist = build_neighbor_list_pt(
        ext_coords,
        ext_atype,
        natoms[0],
        pt_obj.get_rcut(),
        pt_obj.get_sel(),
        distinguish_types=(not mixed_types),
    )
    result, _, _, _, _ = pt_obj(ext_coords, ext_atype, nlist, mapping=mapping)
    return result


@parameterized(("float32", "float64"), (True, False))
class TestDescriptorDPA2(unittest.TestCase):
    def setUp(self):
        (self.dtype, self.type_one_side) = self.param
        if self.dtype == "float32":
            self.skipTest("FP32 has bugs:")
            # ../../../../deepmd/pt/model/descriptor/repformer_layer.py:521: in forward
            # torch.matmul(attnw.unsqueeze(-2), gg1v).squeeze(-2).view(nb, nloc, nh * ni)
            # E       RuntimeError: expected scalar type Float but found Double
        if self.dtype == "float32":
            self.atol = 1e-5
        elif self.dtype == "float64":
            self.atol = 1e-10
        self.seed = 21
        self.sel = [10]
        self.rcut_smth = 5.80
        self.rcut = 6.00
        self.neuron = [6, 12, 24]
        self.axis_neuron = 3
        self.ntypes = 2
        self.coords = np.array(
            [
                12.83,
                2.56,
                2.18,
                12.09,
                2.87,
                2.74,
                00.25,
                3.32,
                1.68,
                3.36,
                3.00,
                1.81,
                3.51,
                2.51,
                2.60,
                4.27,
                3.22,
                1.56,
            ],
            dtype=GLOBAL_NP_FLOAT_PRECISION,
        )
        self.atype = np.array([0, 1, 1, 0, 1, 1], dtype=np.int32)
        self.box = np.array(
            [13.0, 0.0, 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 13.0],
            dtype=GLOBAL_NP_FLOAT_PRECISION,
        )
        self.natoms = np.array([6, 6, 2, 4], dtype=np.int32)

        repinit = RepinitArgs(
            rcut=self.rcut,
            rcut_smth=self.rcut_smth,
            nsel=10,
            tebd_input_mode="strip",
            type_one_side=self.type_one_side,
        )
        repformer = RepformerArgs(
            rcut=self.rcut - 1,
            rcut_smth=self.rcut_smth - 1,
            nsel=9,
        )

        self.descriptor = DescrptDPA2(
            ntypes=self.ntypes,
            repinit=repinit,
            repformer=repformer,
            precision=self.dtype,
        )

    def test_compressed_forward(self):
        result_pt = eval_pt_descriptor(
            self.descriptor,
            self.natoms,
            self.coords,
            self.atype,
            self.box,
        )
        self.descriptor.enable_compression(0.5)
        result_pt_compressed = eval_pt_descriptor(
            self.descriptor,
            self.natoms,
            self.coords,
            self.atype,
            self.box,
        )

        self.assertEqual(result_pt.shape, result_pt_compressed.shape)
        torch.testing.assert_close(
            result_pt,
            result_pt_compressed,
            atol=self.atol,
            rtol=self.atol,
        )


if __name__ == "__main__":
    unittest.main()