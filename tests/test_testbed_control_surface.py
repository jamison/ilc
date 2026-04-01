from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.testbed import render_testbed_configs


def _hosts_payload() -> dict[str, object]:
    return {
        'version': 'testbed_hosts_v0.1',
        'control_machine': {
            'name': 'ilc-node-1',
            'tailscale_name': 'imac',
            'tailscale_ip': '100.96.35.87',
            'repo_path': '/tmp/repo',
            'role': 'control_and_node',
        },
        'remote_hosts': [
            {
                'name': 'ilc-node-2',
                'tailscale_name': 'ilc-node-2',
                'tailscale_ip': '100.109.27.59',
                'ssh_host': 'ilc-node-2',
                'ssh_user': 'ilcops',
                'repo_path': '/opt/ilc/current',
                'venv_path': '/opt/ilc/venv',
                'config_path': '/etc/ilc',
                'systemd_unit': 'ilc-node-v1.service',
            },
            {
                'name': 'ilc-node-3',
                'tailscale_name': 'ilc-node-3',
                'tailscale_ip': '100.108.3.57',
                'ssh_host': 'ilc-node-3',
                'ssh_user': 'ilcops',
                'repo_path': '/opt/ilc/current',
                'venv_path': '/opt/ilc/venv',
                'config_path': '/etc/ilc',
                'systemd_unit': 'ilc-node-v1.service',
            },
        ],
    }


def test_render_testbed_configs_writes_expected_topology(tmp_path: Path) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'configs'

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    node2 = json.loads((output_root / 'ilc-node-2' / 'node_config.json').read_text(encoding='utf-8'))
    assert node2['node_id'] == 'node-2'
    assert node2['transport']['bind_host'] == '100.109.27.59'
    assert node2['transport']['bind_port'] == 19572
    assert node2['peers'] == [
        'https://100.96.35.87:19571',
        'https://100.108.3.57:19573',
    ]

    bundle_text = (output_root / 'ilc-node-1' / 'genesis_bundle.json').read_text(encoding='utf-8').strip()
    expected_sha = hashlib.sha256(bundle_text.encode('utf-8')).hexdigest()
    node3_ref = json.loads((output_root / 'ilc-node-3' / 'genesis_ref.json').read_text(encoding='utf-8'))
    assert node3_ref['genesis_bundle_sha256'] == expected_sha

    env_text = (output_root / 'ilc-node-1' / 'ilc-node-v1.env').read_text(encoding='utf-8')
    assert 'ILC_CONFIG_PATH=/etc/ilc/node_config.json' in env_text
    assert 'ILC_GENESIS_REF_PATH=/etc/ilc/genesis_ref.json' in env_text


def test_render_testbed_configs_requires_all_three_named_hosts(tmp_path: Path) -> None:
    payload = _hosts_payload()
    payload['remote_hosts'] = [payload['remote_hosts'][0]]
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(payload), encoding='utf-8')

    with pytest.raises(SystemExit, match='missing_hosts:ilc-node-3'):
        render_testbed_configs.render_configs(
            hosts_path=hosts_path,
            output_root=tmp_path / 'configs',
            network_id='testnet-0',
        )
