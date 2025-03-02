# SPDX-License-Identifier: LGPL-3.0-or-later
from typing import (
    Any,
    Literal,
    Optional,
    Union,
    overload,
)

import numpy as np

from deepmd.dpmodel.output_def import (
    FittingOutputDef,
    ModelOutputDef,
    OutputVariableDef,
)

from .deep_eval import (
    DeepEval,
)


class DeepPot(DeepEval):
    """Potential energy model.

    Parameters
    ----------
    model_file : Path
        The name of the frozen model file.
    *args : list
        Positional arguments.
    auto_batch_size : bool or int or AutoBatchSize, default: True
        If True, automatic batch size will be used. If int, it will be used
        as the initial batch size.
    neighbor_list : ase.neighborlist.NewPrimitiveNeighborList, optional
        The ASE neighbor list class to produce the neighbor list. If None, the
        neighbor list will be built natively in the model.
    **kwargs : dict
        Keyword arguments.

    Examples
    --------
    >>> from deepmd.infer import DeepPot
    >>> import numpy as np
    >>> dp = DeepPot("graph.pb")
    >>> coord = np.array([[1, 0, 0], [0, 0, 1.5], [1, 0, 3]]).reshape([1, -1])
    >>> cell = np.diag(10 * np.ones(3)).reshape([1, -1])
    >>> atype = [1, 0, 1]
    >>> e, f, v = dp.eval(coord, cell, atype)

    where `e`, `f` and `v` are predicted energy, force and virial of the system, respectively.
    """

    @property
    def output_def(self) -> ModelOutputDef:
        """Get the output definition of this model."""
        return ModelOutputDef(
            FittingOutputDef(
                [
                    OutputVariableDef(
                        "energy",
                        shape=[1],
                        reducible=True,
                        r_differentiable=True,
                        c_differentiable=True,
                        atomic=True,
                        r_hessian=True,
                    ),
                ]
            )
        )

    @property
    def output_def_mag(self) -> ModelOutputDef:
        """Get the output definition of this model with magnetic parts."""
        return ModelOutputDef(
            FittingOutputDef(
                [
                    OutputVariableDef(
                        "energy",
                        shape=[1],
                        reducible=True,
                        r_differentiable=True,
                        c_differentiable=True,
                        atomic=True,
                        magnetic=True,
                    ),
                ]
            )
        )

    @overload
    def eval(
        self,
        coords: np.ndarray,
        cells: Optional[np.ndarray],
        atom_types: Union[list[int], np.ndarray],
        atomic: Literal[True],
        fparam: Optional[np.ndarray],
        aparam: Optional[np.ndarray],
        mixed_type: bool,
        **kwargs: Any,
    ) -> Union[
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ]:
        pass

    @overload
    def eval(
        self,
        coords: np.ndarray,
        cells: Optional[np.ndarray],
        atom_types: Union[list[int], np.ndarray],
        atomic: Literal[False],
        fparam: Optional[np.ndarray],
        aparam: Optional[np.ndarray],
        mixed_type: bool,
        **kwargs: Any,
    ) -> Union[
        tuple[np.ndarray, np.ndarray, np.ndarray],
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ]:
        pass

    @overload
    def eval(
        self,
        coords: np.ndarray,
        cells: Optional[np.ndarray],
        atom_types: Union[list[int], np.ndarray],
        atomic: bool,
        fparam: Optional[np.ndarray],
        aparam: Optional[np.ndarray],
        mixed_type: bool,
        **kwargs: Any,
    ) -> tuple[np.ndarray, ...]:
        pass

    def eval(
        self,
        coords: np.ndarray,
        cells: Optional[np.ndarray],
        atom_types: Union[list[int], np.ndarray],
        atomic: bool = False,
        fparam: Optional[np.ndarray] = None,
        aparam: Optional[np.ndarray] = None,
        mixed_type: bool = False,
        **kwargs: Any,
    ) -> tuple[np.ndarray, ...]:
        """Evaluate energy, force, and virial. If atomic is True,
        also return atomic energy and atomic virial.

        Parameters
        ----------
        coords : np.ndarray
            The coordinates of the atoms, in shape (nframes, natoms, 3).
        cells : np.ndarray
            The cell vectors of the system, in shape (nframes, 9). If the system
            is not periodic, set it to None.
        atom_types : list[int] or np.ndarray
            The types of the atoms. If mixed_type is False, the shape is (natoms,);
            otherwise, the shape is (nframes, natoms).
        atomic : bool, optional
            Whether to return atomic energy and atomic virial, by default False.
        fparam : np.ndarray, optional
            The frame parameters, by default None.
        aparam : np.ndarray, optional
            The atomic parameters, by default None.
        mixed_type : bool, optional
            Whether the atom_types is mixed type, by default False.
        **kwargs : dict[str, Any]
            Keyword arguments.

        Returns
        -------
        energy
            The energy of the system, in shape (nframes,).
        force
            The force of the system, in shape (nframes, natoms, 3).
        virial
            The virial of the system, in shape (nframes, 9).
        atomic_energy
            The atomic energy of the system, in shape (nframes, natoms). Only returned
            when atomic is True.
        atomic_virial
            The atomic virial of the system, in shape (nframes, natoms, 9). Only returned
            when atomic is True.
        hessian
            The Hessian matrix of the system, in shape (nframes, 3 * natoms, 3 * natoms). Returned when available.
        """
        # This method has been used by:
        # documentation python.md
        # dp model_devi: +fparam, +aparam, +mixed_type
        # dp test: +atomic, +fparam, +aparam, +efield, +mixed_type
        # finetune: +mixed_type
        # dpdata
        # ase
        (
            coords,
            cells,
            atom_types,
            fparam,
            aparam,
            nframes,
            natoms,
        ) = self._standard_input(coords, cells, atom_types, fparam, aparam, mixed_type)
        results = self.deep_eval.eval(
            coords,
            cells,
            atom_types,
            atomic,
            fparam=fparam,
            aparam=aparam,
            **kwargs,
        )
        energy = results["energy_redu"].reshape(nframes, 1)
        force = results["energy_derv_r"].reshape(nframes, natoms, 3)
        virial = results["energy_derv_c_redu"].reshape(nframes, 9)

        if atomic:
            if self.get_ntypes_spin() > 0:
                ntypes_real = self.get_ntypes() - self.get_ntypes_spin()
                natoms_real = sum(
                    [
                        np.count_nonzero(np.array(atom_types[0]) == ii)
                        for ii in range(ntypes_real)
                    ]
                )
            else:
                natoms_real = natoms
            atomic_energy = results["energy"].reshape(nframes, natoms_real, 1)
            atomic_virial = results["energy_derv_c"].reshape(nframes, natoms, 9)
            result = (
                energy,
                force,
                virial,
                atomic_energy,
                atomic_virial,
            )
        else:
            result = (
                energy,
                force,
                virial,
            )
        if self.deep_eval.get_has_spin():
            force_mag = results["energy_derv_r_mag"].reshape(nframes, natoms, 3)
            mask_mag = results["mask_mag"].reshape(nframes, natoms, 1)
            result = (*list(result), force_mag, mask_mag)
        if self.deep_eval.get_has_hessian():
            hessian = results["energy_derv_r_derv_r"].reshape(
                nframes, 3 * natoms, 3 * natoms
            )
            result = (*list(result), hessian)
        return result


__all__ = ["DeepPot"]
