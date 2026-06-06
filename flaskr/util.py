import re

from flaskr.db import Material


# Material Processing

def _normalize_material_id(name: str) -> str:
    base_id = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not base_id:
        base_id = 'material'
    candidate = base_id
    suffix = 1
    while Material.select().where(Material.id == candidate).exists():
        candidate = f"{base_id}-{suffix}"
        suffix += 1
    return candidate


def _ensure_default_materials() -> None:
    if Material.select().count() > 0:
        return

    defaults = [
        {
            'id': 'fabric-a',
            'name': 'Fabric A',
            'desc': 'Standard woven polyester blend. Mid-weight, low stretch. Suitable for general cutting operations.',
            'thickness': '1.2',
            'z_offset': '-0.50'
        },
        {
            'id': 'fabric-b',
            'name': 'Fabric B',
            'desc': 'Heavy-duty canvas. Dense weave, rigid structure. Requires slower feed rate and higher Z clearance.',
            'thickness': '2.8',
            'z_offset': '-1.20'
        },
        {
            'id': 'fabric-c',
            'name': 'Fabric C',
            'desc': 'Lightweight chiffon / silk blend. Delicate; use vacuum hold-down. Minimal Z pressure recommended.',
            'thickness': '0.4',
            'z_offset': '-0.15'
        }
    ]

    for material in defaults:
        Material.create(
            id=material['id'],
            name=material['name'],
            desc=material['desc'],
            thickness=material['thickness'],
            z_offset=material['z_offset']
        )