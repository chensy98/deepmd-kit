# SPDX-License-Identifier: LGPL-3.0-or-later
from importlib.util import (
    find_spec,
)
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
)

from deepmd.backend.backend import (
    Backend,
)

if TYPE_CHECKING:
    from argparse import (
        Namespace,
    )

    from deepmd.infer.deep_eval import (
        DeepEvalBackend,
    )
    from deepmd.utils.neighbor_stat import (
        NeighborStat,
    )


@Backend.register("pt")
@Backend.register("pytorch")
class PyTorchBackend(Backend):
    """PyTorch backend."""

    name = "PyTorch"
    """The formal name of the backend."""
    features: ClassVar[Backend.Feature] = (
        Backend.Feature.ENTRY_POINT
        | Backend.Feature.DEEP_EVAL
        | Backend.Feature.NEIGHBOR_STAT
        | Backend.Feature.IO
    )
    """The features of the backend."""
    suffixes: ClassVar[list[str]] = [".pth", ".pt"]
    """The suffixes of the backend."""

    def is_available(self) -> bool:
        """Check if the backend is available.

        Returns
        -------
        bool
            Whether the backend is available.
        """
        return find_spec("torch") is not None

    @property
    def entry_point_hook(self) -> Callable[["Namespace"], None]:
        """The entry point hook of the backend.

        Returns
        -------
        Callable[[Namespace], None]
            The entry point hook of the backend.
        """
        from deepmd.pt.entrypoints.main import main as deepmd_main

        return deepmd_main

    @property
    def deep_eval(self) -> type["DeepEvalBackend"]:
        """The Deep Eval backend of the backend.

        Returns
        -------
        type[DeepEvalBackend]
            The Deep Eval backend of the backend.
        """
        from deepmd.pt.infer.deep_eval import DeepEval as DeepEvalPT

        return DeepEvalPT

    @property
    def neighbor_stat(self) -> type["NeighborStat"]:
        """The neighbor statistics of the backend.

        Returns
        -------
        type[NeighborStat]
            The neighbor statistics of the backend.
        """
        from deepmd.pt.utils.neighbor_stat import (
            NeighborStat,
        )

        return NeighborStat

    @property
    def serialize_hook(self) -> Callable[[str], dict]:
        """The serialize hook to convert the model file to a dictionary.

        Returns
        -------
        Callable[[str], dict]
            The serialize hook of the backend.
        """
        from deepmd.pt.utils.serialization import (
            serialize_from_file,
        )

        return serialize_from_file

    @property
    def deserialize_hook(self) -> Callable[[str, dict], None]:
        """The deserialize hook to convert the dictionary to a model file.

        Returns
        -------
        Callable[[str, dict], None]
            The deserialize hook of the backend.
        """
        from deepmd.pt.utils.serialization import (
            deserialize_to_file,
        )

        return deserialize_to_file
