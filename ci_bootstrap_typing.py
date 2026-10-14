"""Temporary exact-source migration; removed after the CI bootstrap."""

from pathlib import Path


def replace_once(text, before, after):
    if after in text:
        return text
    if text.count(before) != 1:
        raise RuntimeError(
            f"Source changed; refusing ambiguous replacement: {before!r}"
        )
    return text.replace(before, after, 1)


edits = {
    "pymyenergi/connection.py": [
        (
            "        self.auth = httpx.DigestAuth(self.username, self.password)",
            "        if self.username is None or self.password is None:\n"
            '            raise TypeError("Hub serial number and API key must be provided")\n'
            "        self.auth = httpx.DigestAuth(self.username, self.password)",
        ),
    ],
    "pymyenergi/base_device.py": [
        (
            "from datetime import timezone\n",
            "from datetime import timezone\nfrom typing import Dict\n",
        ),
        (
            "        self.ct_groups = {}",
            "        self.ct_groups: Dict[str, float] = {}",
        ),
    ],
    "pymyenergi/zappi.py": [
        (
            "from pymyenergi.connection import Connection\n",
            "from typing import Any\nfrom typing import Dict\n\nfrom pymyenergi.connection import Connection\n",
        ),
        (
            "        self.boost_data = {}",
            "        self.boost_data: Dict[str, Any] = {}",
        ),
    ],
    "pymyenergi/libbi.py": [
        (
            "from pymyenergi.connection import Connection\n",
            "from typing import Any\nfrom typing import Dict\n\nfrom pymyenergi.connection import Connection\n",
        ),
        (
            "        self._extra_data = {}",
            "        self._extra_data: Dict[str, Any] = {}",
        ),
    ],
    "pymyenergi/client.py": [
        (
            "from datetime import timezone\n",
            "from datetime import timezone\nfrom typing import Any\nfrom typing import Dict\nfrom typing import List\nfrom typing import Union\n",
        ),
        (
            "from .eddi import Eddi\n",
            "from .base_device import BaseDevice\nfrom .eddi import Eddi\n",
        ),
        (
            "        self.devices = {}",
            "        self.devices: Dict[Union[int, str], BaseDevice] = {}",
        ),
        ("        self._data = []", "        self._data: List[Dict[str, Any]] = []"),
        ("        self._totals = {}", "        self._totals: Dict[str, float] = {}"),
        (
            "        self._history_totals = {}",
            "        self._history_totals: Dict[str, float] = {}",
        ),
    ],
}
for name, replacements in edits.items():
    path = Path(name)
    data = path.read_text(encoding="utf-8")
    for old, new in replacements:
        # Only the constructor is changed when a name is also reset elsewhere.
        if name.endswith("client.py") and old == "        self._totals = {}":
            if new not in data:
                data = data.replace(old, new, 1)
        else:
            data = replace_once(data, old, new)
    if name.endswith("base_device.py"):
        setter = (
            "    @data.setter\n"
            "    def data(self, value):\n"
            '        """Set all device data"""\n'
            "        self._data = value\n"
            "        self.refresh_ct_groups()\n\n"
        )
        anchor = "    def refresh_ct_groups(self):\n"
        if data.count(setter) != 1 or data.count(anchor) != 1:
            raise RuntimeError("Unexpected BaseDevice property layout")
        data = data.replace(setter, "", 1).replace(anchor, setter + anchor, 1)
    path.write_text(data, encoding="utf-8")
