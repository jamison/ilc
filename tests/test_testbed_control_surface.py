from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.testbed import render_bootstrap_peers
from tools.testbed import render_bootstrap_distribution
from tools.testbed import render_diagnostics_manifest
from tools.testbed import render_rc_substrate_evidence
from tools.testbed import check_rc0_1_substrate_closure
from tools.testbed import apply_peer_promotion
from tools.testbed.peer_inventory import load_overrides, resolve_active_peer_map
from tools.testbed import render_testbed_configs
from tools.testbed import verify_bootstrap_peers
from tools.testbed import verify_bootstrap_distribution
from tools import check_rc0_1_release_gate


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


def test_render_and_verify_bootstrap_peers_match_local_configs(tmp_path: Path) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'configs'
    bootstrap_path = tmp_path / 'bootstrap_peers.json'

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    cert_fixture = Path('tests/fixtures/phase_572_three_machine_smoke/cert.pem')
    for host_name in ('ilc-node-1', 'ilc-node-2', 'ilc-node-3'):
        shutil.copy(cert_fixture, output_root / host_name / 'cert.pem')

    entries = render_bootstrap_peers.render_bootstrap_peers(
        hosts_path=hosts_path,
        config_root=output_root,
        output_path=bootstrap_path,
    )

    assert len(entries) == 3
    assert bootstrap_path.exists()
    assert verify_bootstrap_peers.verify_bootstrap_peers(
        bootstrap_path=bootstrap_path,
        config_root=output_root,
    ) == []


def test_verify_bootstrap_peers_rejects_tampered_fingerprint(tmp_path: Path) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'configs'
    bootstrap_path = tmp_path / 'bootstrap_peers.json'

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    cert_fixture = Path('tests/fixtures/phase_572_three_machine_smoke/cert.pem')
    for host_name in ('ilc-node-1', 'ilc-node-2', 'ilc-node-3'):
        shutil.copy(cert_fixture, output_root / host_name / 'cert.pem')

    entries = render_bootstrap_peers.render_bootstrap_peers(
        hosts_path=hosts_path,
        config_root=output_root,
        output_path=bootstrap_path,
    )
    entries[0]['tls_fingerprint'] = 'sha256:deadbeef'
    bootstrap_path.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')

    assert verify_bootstrap_peers.verify_bootstrap_peers(
        bootstrap_path=bootstrap_path,
        config_root=output_root,
    ) == ['bootstrap_tls_fingerprint_mismatch:ilc-node-1']


def test_apply_peer_promotion_uses_bootstrap_and_overrides(tmp_path: Path) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'configs'
    bootstrap_path = tmp_path / 'bootstrap_peers.json'
    overrides_path = tmp_path / 'peer_overrides.json'

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    cert_fixture = Path('tests/fixtures/phase_572_three_machine_smoke/cert.pem')
    for host_name in ('ilc-node-1', 'ilc-node-2', 'ilc-node-3'):
        shutil.copy(cert_fixture, output_root / host_name / 'cert.pem')

    render_bootstrap_peers.render_bootstrap_peers(
        hosts_path=hosts_path,
        config_root=output_root,
        output_path=bootstrap_path,
    )
    overrides_path.write_text(
        json.dumps(
            {
                'pin_node_ids': ['node-3'],
                'deny_endpoints': [],
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    assert apply_peer_promotion.apply_peer_promotion(
        bootstrap_path=bootstrap_path,
        overrides_path=overrides_path,
        config_root=output_root,
    ) == []

    node2 = json.loads((output_root / 'ilc-node-2' / 'node_config.json').read_text(encoding='utf-8'))
    assert node2['peers'] == [
        'https://100.108.3.57:19573',
        'https://100.96.35.87:19571',
    ]


def test_verify_bootstrap_peers_rejects_stale_inventory(tmp_path: Path) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'configs'
    bootstrap_path = tmp_path / 'bootstrap_peers.json'

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    cert_fixture = Path('tests/fixtures/phase_572_three_machine_smoke/cert.pem')
    for host_name in ('ilc-node-1', 'ilc-node-2', 'ilc-node-3'):
        shutil.copy(cert_fixture, output_root / host_name / 'cert.pem')

    entries = render_bootstrap_peers.render_bootstrap_peers(
        hosts_path=hosts_path,
        config_root=output_root,
        output_path=bootstrap_path,
    )
    entries[0]['last_verified_at'] = '2000-01-01T00:00:00Z'
    bootstrap_path.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')

    assert verify_bootstrap_peers.verify_bootstrap_peers(
        bootstrap_path=bootstrap_path,
        config_root=output_root,
        max_age_hours=24,
    ) == ['bootstrap_last_verified_stale:node-1']


def test_peer_inventory_resolution_stays_bootstrap_authoritative() -> None:
    bootstrap_entries = [
        {'node_id': 'node-1', 'endpoint': 'https://one', 'status': 'approved'},
        {'node_id': 'node-2', 'endpoint': 'https://two', 'status': 'approved'},
        {'node_id': 'node-3', 'endpoint': 'https://three', 'status': 'approved'},
    ]
    overrides = load_overrides(None)
    peer_map, errors = resolve_active_peer_map(bootstrap_entries, overrides)

    assert errors == []
    assert peer_map['node-1'] == ['https://three', 'https://two']
    assert 'https://candidate-only' not in peer_map['node-1']


def test_render_diagnostics_manifest_writes_self_describing_bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'diagnostics'
    home_dir = output_root / 'ilc-node-1'
    node2_dir = output_root / 'ilc-node-2'
    node3_dir = output_root / 'ilc-node-3'
    for host_dir in (home_dir, node2_dir, node3_dir):
        host_dir.mkdir(parents=True)
        (host_dir / 'hostname.txt').write_text(f'{host_dir.name}\n', encoding='utf-8')
    (home_dir / 'bootstrap_peers.json').write_text('[]\n', encoding='utf-8')
    (home_dir / 'home_node.log').write_text('home_node_started:1234\nthree_node_exchange_ok\n', encoding='utf-8')
    (node2_dir / 'journal_tail.txt').write_text('remote_smoke_ok:ilc-node-2:service\n', encoding='utf-8')

    monkeypatch.setattr(render_diagnostics_manifest, '_git_head', lambda _: 'deadbeef')
    manifest = render_diagnostics_manifest.render_manifest(output_root=output_root, hosts_path=hosts_path)

    manifest_path = output_root / 'manifest.json'
    assert manifest_path.exists()
    assert manifest['repo_head'] == 'deadbeef'
    assert manifest['hosts']['ilc-node-1']['artifact_count'] >= 3
    assert 'home_node_started:1234' in manifest['hosts']['ilc-node-1']['marker_summary']


def test_render_and_verify_bootstrap_distribution_match_curated_inventory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(_hosts_payload()), encoding='utf-8')
    output_root = tmp_path / 'configs'
    bootstrap_path = tmp_path / 'bootstrap_peers.json'
    distribution_path = tmp_path / 'bootstrap_distribution.json'
    overrides_path = tmp_path / 'peer_overrides.json'
    overrides_path.write_text(json.dumps({'version': 'peer_overrides_v0.1'}, indent=2) + '\n', encoding='utf-8')

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    cert_fixture = Path('tests/fixtures/phase_572_three_machine_smoke/cert.pem')
    for host_name in ('ilc-node-1', 'ilc-node-2', 'ilc-node-3'):
        shutil.copy(cert_fixture, output_root / host_name / 'cert.pem')

    render_bootstrap_peers.render_bootstrap_peers(
        hosts_path=hosts_path,
        config_root=output_root,
        output_path=bootstrap_path,
    )
    monkeypatch.setattr(render_bootstrap_distribution, '_git_head', lambda _: 'deadbeef')
    payload = render_bootstrap_distribution.render_distribution(
        bootstrap_path=bootstrap_path,
        hosts_path=hosts_path,
        overrides_path=overrides_path,
        output_path=distribution_path,
    )

    assert payload['repo_head'] == 'deadbeef'
    assert payload['approved_peer_count'] == 3
    assert verify_bootstrap_distribution.verify_distribution(
        distribution_path=distribution_path,
        bootstrap_path=bootstrap_path,
    ) == []


def test_verify_bootstrap_distribution_rejects_tampered_sha(tmp_path: Path) -> None:
    bootstrap_path = tmp_path / 'bootstrap_peers.json'
    distribution_path = tmp_path / 'bootstrap_distribution.json'
    bootstrap_entries = [{'node_id': 'node-1', 'endpoint': 'https://one', 'status': 'approved'}]
    bootstrap_path.write_text(json.dumps(bootstrap_entries, indent=2) + '\n', encoding='utf-8')
    distribution_path.write_text(
        json.dumps(
            {
                'version': 'testbed_bootstrap_distribution_v0.1',
                'entries': bootstrap_entries,
                'bootstrap_sha256': 'deadbeef',
                'approved_peer_count': 1,
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    assert verify_bootstrap_distribution.verify_distribution(
        distribution_path=distribution_path,
        bootstrap_path=bootstrap_path,
    ) == ['bootstrap_distribution_sha_mismatch']


def test_render_rc_substrate_evidence_writes_manifest_and_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    diagnostics_manifest_path = tmp_path / 'diagnostics_manifest.json'
    install_manifest_path = tmp_path / 'install_manifest.json'
    scenario_manifest_path = tmp_path / 'scenario_manifest.json'
    scenario_replay_manifest_path = tmp_path / 'scenario_replay_manifest.json'
    bootstrap_distribution_path = tmp_path / 'bootstrap_distribution.json'
    steps_dir = tmp_path / 'steps'
    steps_dir.mkdir()
    (steps_dir / 'three_node_exchange.log').write_text('three_node_exchange_ok\n', encoding='utf-8')
    (steps_dir / 'negative_path_drills.log').write_text('negative_path_drill_ok\n', encoding='utf-8')

    diagnostics_manifest_path.write_text(
        json.dumps({'hosts': {'ilc-node-1': {'artifact_count': 1}}}, indent=2) + '\n',
        encoding='utf-8',
    )
    install_manifest_path.write_text(
        json.dumps({'results': [{'host': 'ilc-node-1', 'status': 'ok'}]}, indent=2) + '\n',
        encoding='utf-8',
    )
    scenario_manifest_path.write_text(
        json.dumps(
            {
                'panel_passed': True,
                'submission_count': 7,
                'panel_verdict_token': 'panel_quorum_passed',
                'agreement_score': 0.875,
                'ecu_claim_count': 6,
                'reward_total': 5.81,
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    scenario_replay_manifest_path.write_text(
        json.dumps(
            {
                'replay_payload': {
                    'panel_result_matches': True,
                    'ecu_claims_match': True,
                    'panel_verdict_token': 'panel_quorum_passed',
                }
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    bootstrap_distribution_path.write_text(
        json.dumps({'approved_peer_count': 3}, indent=2) + '\n',
        encoding='utf-8',
    )

    monkeypatch.setattr(render_rc_substrate_evidence, '_git_head', lambda _: 'deadbeef')
    output_root = tmp_path / 'evidence'
    manifest = render_rc_substrate_evidence.render_evidence(
        output_root=output_root,
        bootstrap_distribution_path=bootstrap_distribution_path,
        diagnostics_manifest_path=diagnostics_manifest_path,
        install_proof_manifest_path=install_manifest_path,
        scenario_manifest_path=scenario_manifest_path,
        scenario_replay_manifest_path=scenario_replay_manifest_path,
        steps_dir=steps_dir,
    )

    assert manifest['repo_head'] == 'deadbeef'
    assert manifest['closure_rows']['install_shape'] == 'satisfied_for_testbed'
    assert manifest['closure_rows']['three_node_seven_agent_path'] == 'satisfied_for_testbed'
    assert manifest['closure_rows']['three_node_seven_agent_replay'] == 'satisfied_for_testbed'
    assert (output_root / 'manifest.json').exists()
    assert (output_root / 'summary.md').exists()


def test_check_rc0_1_substrate_closure_accepts_satisfied_evidence(tmp_path: Path) -> None:
    evidence_path = tmp_path / 'evidence.json'
    evidence_path.write_text(
        json.dumps(
            {
                'closure_rows': {
                    'install_shape': 'satisfied_for_testbed',
                    'bootstrap_distribution': 'satisfied_for_testbed',
                    'diagnostics': 'satisfied_for_testbed',
                    'three_node_seven_agent_path': 'satisfied_for_testbed',
                    'three_node_seven_agent_replay': 'satisfied_for_testbed',
                    'release_evidence': 'satisfied_for_testbed',
                },
                'scenario_summary': {'panel_verdict_token': 'panel_quorum_passed'},
                'scenario_replay_summary': {
                    'panel_result_matches': True,
                    'ecu_claims_match': True,
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    verdict, failures = check_rc0_1_substrate_closure.check_evidence(evidence_path)
    assert verdict == 'pass'
    assert failures == []


def test_check_rc0_1_release_gate_accepts_consistent_bundle_and_evidence(tmp_path: Path) -> None:
    archive_path = tmp_path / 'bundle.tar.gz'
    archive_path.write_bytes(b'rc-bundle')
    bundle_manifest_path = tmp_path / 'bundle_manifest.json'
    evidence_manifest_path = tmp_path / 'evidence_manifest.json'
    checklist_path = tmp_path / 'checklist.md'

    bundle_manifest_path.write_text(
        json.dumps(
            {
                'archive_path': str(archive_path),
                'archive_sha256': hashlib.sha256(b'rc-bundle').hexdigest(),
                'repo_head': 'deadbeef',
                'guidance_files': [str(tmp_path / name) for name in sorted(check_rc0_1_release_gate.REQUIRED_GUIDANCE)],
                'installer_files': [str(tmp_path / name) for name in sorted(check_rc0_1_release_gate.REQUIRED_INSTALLERS)],
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    evidence_manifest_path.write_text(
        json.dumps(
            {
                'repo_head': 'deadbeef',
                'closure_rows': {
                    'install_shape': 'satisfied_for_testbed',
                    'bootstrap_distribution': 'satisfied_for_testbed',
                    'diagnostics': 'satisfied_for_testbed',
                    'three_node_seven_agent_path': 'satisfied_for_testbed',
                    'three_node_seven_agent_replay': 'satisfied_for_testbed',
                    'release_evidence': 'satisfied_for_testbed',
                },
                'scenario_summary': {'panel_verdict_token': 'panel_quorum_passed'},
                'scenario_replay_summary': {
                    'panel_result_matches': True,
                    'ecu_claims_match': True,
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    checklist_path.write_text(
        '\n'.join(
            [
                '| Area | Requirement | Minimum evidence | Current pre-RC status |',
                '|---|---|---|---|',
                '| Install shape | x | y | satisfied_for_testbed |',
                '| Release evidence | x | y | satisfied_for_testbed |',
            ]
        ) + '\n',
        encoding='utf-8',
    )
    proof_manifest_path = tmp_path / 'proof_manifest.json'
    proof_manifest_path.write_text(
        json.dumps(
            {
                'results': [
                    {'host': 'ilc-node-1', 'status': 'ok'},
                    {'host': 'ilc-node-2', 'status': 'ok'},
                ]
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    verdict, failures = check_rc0_1_release_gate.check_release_gate(
        bundle_manifest_path=bundle_manifest_path,
        evidence_manifest_path=evidence_manifest_path,
        checklist_path=checklist_path,
    )
    assert verdict == 'pass'
    assert failures == []

    proof_payload = json.loads(proof_manifest_path.read_text(encoding='utf-8'))
    assert all(item['status'] == 'ok' for item in proof_payload['results'])


def test_bundle_installer_scripts_are_runnable_from_copied_bundle_layout(tmp_path: Path) -> None:
    installer_root = tmp_path / 'installer'
    installer_root.mkdir()
    for name in ('rc_bundle_runtime.py', 'rc_install_bundle_node.py', 'rc_update_bundle_node.py'):
        shutil.copy2(Path('tools') / name, installer_root / name)

    install_result = subprocess.run(
        ['python3', str(installer_root / 'rc_install_bundle_node.py'), '--help'],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(tmp_path),
    )
    update_result = subprocess.run(
        ['python3', str(installer_root / 'rc_update_bundle_node.py'), '--help'],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(tmp_path),
    )

    assert install_result.returncode == 0, install_result.stderr
    assert update_result.returncode == 0, update_result.stderr
