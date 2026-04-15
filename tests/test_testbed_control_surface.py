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
from tools import check_rc0_1_economic_state
from tools import check_rc0_1_release_gate
from tools import check_rc0_1_release_claim
from tools import prove_rc0_1_economic_state
from tools import render_rc0_1_readiness_delta
from tools import run_rc0_1_release_candidate
from tools import run_rc0_1_release_gate
from tools.testbed import run_rc0_1_substrate_closure


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


def _five_node_hosts_payload() -> dict[str, object]:
    payload = _hosts_payload()
    payload['remote_hosts'] = [
        {
            'name': 'ilc-node-2-machine',
            'tailscale_name': 'ilc-node-2',
            'tailscale_ip': '100.109.27.59',
            'ssh_host': 'ilc-node-2',
            'ssh_user': 'ilcops',
            'repo_path': '/opt/ilc/current',
            'venv_path': '/opt/ilc/venv',
            'systemd_unit': 'ilc-node-v1.service',
            'node_instances': [
                {
                    'name': 'ilc-node-2',
                    'config_path': '/etc/ilc',
                    'launch_mode': 'systemd',
                },
                {
                    'name': 'ilc-node-4',
                    'config_path': '/tmp/ilc-node-4',
                    'launch_mode': 'manual',
                },
            ],
        },
        {
            'name': 'ilc-node-3-machine',
            'tailscale_name': 'ilc-node-3',
            'tailscale_ip': '100.108.3.57',
            'ssh_host': 'ilc-node-3',
            'ssh_user': 'ilcops',
            'repo_path': '/opt/ilc/current',
            'venv_path': '/opt/ilc/venv',
            'systemd_unit': 'ilc-node-v1.service',
            'node_instances': [
                {
                    'name': 'ilc-node-3',
                    'config_path': '/etc/ilc',
                    'launch_mode': 'systemd',
                },
                {
                    'name': 'ilc-node-5',
                    'config_path': '/tmp/ilc-node-5',
                    'launch_mode': 'manual',
                },
            ],
        },
    ]
    return payload


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


def test_render_testbed_configs_supports_nested_five_node_inventory(tmp_path: Path) -> None:
    payload = _five_node_hosts_payload()
    hosts_path = tmp_path / 'hosts.json'
    hosts_path.write_text(json.dumps(payload), encoding='utf-8')
    output_root = tmp_path / 'configs'

    render_testbed_configs.render_configs(
        hosts_path=hosts_path,
        output_root=output_root,
        network_id='testnet-0',
    )

    node4 = json.loads((output_root / 'ilc-node-4' / 'node_config.json').read_text(encoding='utf-8'))
    node5 = json.loads((output_root / 'ilc-node-5' / 'node_config.json').read_text(encoding='utf-8'))
    node4_env = (output_root / 'ilc-node-4' / 'ilc-node-v1.env').read_text(encoding='utf-8')

    assert node4['node_id'] == 'node-4'
    assert node4['transport']['bind_port'] == 19574
    assert len(node4['peers']) == 4
    assert node5['node_id'] == 'node-5'
    assert node5['transport']['bind_port'] == 19575
    assert 'ILC_CONFIG_PATH=/tmp/ilc-node-4/node_config.json' in node4_env


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
        hosts_path=hosts_path,
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
        hosts_path=hosts_path,
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
        hosts_path=hosts_path,
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


def test_home_node_launcher_uses_detached_background_start() -> None:
    script = Path('tools/testbed/home_node_common.sh').read_text(encoding='utf-8')

    assert 'nohup python3 "$TESTBED_DIR/tools/run_ilc_node_service_v1.py" start \\' in script
    assert '>"$HOME_LOG" 2>&1 </dev/null &' in script
    assert 'printf \'%s\\n\' "$!" > "$HOME_PID"' in script


def test_negative_path_drills_use_repo_python_when_available() -> None:
    common_script = Path('tools/testbed/common.sh').read_text(encoding='utf-8')
    drill_script = Path('tools/testbed/run_negative_path_drills.sh').read_text(encoding='utf-8')

    assert 'local_python_bin()' in common_script
    assert 'PRIMARY_REMOTE_HOST="$(resolve_hosts | head -n 1)"' in drill_script
    assert 'LOCAL_PYTHON="$(local_python_bin)"' in drill_script
    assert '"$LOCAL_PYTHON" "$TESTBED_DIR/tools/testbed/verify_bootstrap_peers.py"' in drill_script


def test_remote_control_surface_supports_manual_launch_mode() -> None:
    common_script = Path('tools/testbed/common.sh').read_text(encoding='utf-8')
    start_script = Path('tools/testbed/start_nodes.sh').read_text(encoding='utf-8')
    stop_script = Path('tools/testbed/stop_nodes.sh').read_text(encoding='utf-8')
    restart_script = Path('tools/testbed/restart_nodes.sh').read_text(encoding='utf-8')
    remote_smoke_script = Path('tools/testbed/run_remote_smoke.sh').read_text(encoding='utf-8')

    assert 'start_manual_remote_node()' in common_script
    assert 'stop_manual_remote_node()' in common_script
    assert 'wait_for_manual_remote_ready()' in common_script
    assert 'start_manual_remote_node "$host"' in start_script
    assert 'stop_manual_remote_node "$host"' in stop_script
    assert 'stop_manual_remote_node "$host"' in restart_script
    assert 'launch_mode="$(host_field "$host" launch_mode)"' in remote_smoke_script


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
    economic_manifest_path = tmp_path / 'economic_manifest.json'
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
    economic_manifest_path.write_text(
        json.dumps(
            {
                'summary': {
                    'distribution_check_ok': True,
                    'wallet_count': 8,
                    'reward_total': 5.81,
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
        economic_manifest_path=economic_manifest_path,
        steps_dir=steps_dir,
    )

    assert manifest['repo_head'] == 'deadbeef'
    assert manifest['closure_rows']['install_shape'] == 'satisfied_for_testbed'
    assert manifest['closure_rows']['three_node_seven_agent_path'] == 'satisfied_for_testbed'
    assert manifest['closure_rows']['three_node_seven_agent_replay'] == 'satisfied_for_testbed'
    assert manifest['closure_rows']['economic_cycle_projection'] == 'satisfied_for_testbed'
    assert manifest['economic_summary']['wallet_count'] == 8
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
                    'economic_cycle_projection': 'satisfied_for_testbed',
                    'release_evidence': 'satisfied_for_testbed',
                },
                'scenario_summary': {'panel_verdict_token': 'panel_quorum_passed'},
                'scenario_replay_summary': {
                    'panel_result_matches': True,
                    'ecu_claims_match': True,
                },
                'economic_summary': {'distribution_check_ok': True, 'wallet_count': 8},
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
                    'economic_cycle_projection': 'satisfied_for_testbed',
                    'release_evidence': 'satisfied_for_testbed',
                },
                'scenario_summary': {'panel_verdict_token': 'panel_quorum_passed'},
                'scenario_replay_summary': {
                    'panel_result_matches': True,
                    'ecu_claims_match': True,
                },
                'economic_summary': {'distribution_check_ok': True, 'wallet_count': 8},
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
    economic_manifest_path = tmp_path / 'economic_manifest.json'
    economic_manifest_path.write_text(
        json.dumps(
            {
                'summary': {
                    'task_id': 'task:test:economic-cycle',
                    'node_count': 7,
                    'wallet_count': 8,
                    'reward_total': 5.0,
                    'distribution_check_ok': True,
                },
                'settlement_manifest': {
                    'settlement_status': 'applied',
                    'epoch_id': 'rc0_1::task:test:economic-cycle::epoch::12',
                },
                'wallet_manifest': {
                    'latest_epoch_id': 'rc0_1::task:test:economic-cycle::epoch::12',
                },
                'runtime_store': {
                    'store_kind': 'lmdb_public_runtime_v0.1',
                    'graph_store_root': str(tmp_path),
                    'wallet_store_root': str(tmp_path),
                    'ledger_store_root': str(tmp_path),
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    economic_proof_manifest_path = tmp_path / 'economic_proof_manifest.json'
    economic_proof_manifest_path.write_text(
        json.dumps(
            {
                'comparison': {
                    'nodes_match': True,
                    'links_match': True,
                    'wallets_match': True,
                    'ledger_match': True,
                    'quorum_match': True,
                },
                'invariant_summary': {
                    'rewarded_wallet_count': 6,
                    'epoch_record_count': 1,
                    'runtime_store': {'store_kind': 'lmdb_public_runtime_v0.1'},
                },
                'negative_path_verdict': 'pass',
                'replay_verdict': 'pass',
                'replay_settlement_status': 'idempotent_replay',
                'query_payloads': {
                    name: {'ok': True}
                    for name in (
                        'summary',
                        'store_summary',
                        'quorum_record',
                        'wallet_export',
                        'graph_summary',
                        'graph_links',
                        'ledger_summary',
                        'wallet_status',
                        'wallet_history',
                        'graph_node',
                    )
                },
                'query_timings_ms': {
                    name: 1.0
                    for name in (
                        'summary',
                        'store_summary',
                        'quorum_record',
                        'wallet_export',
                        'graph_summary',
                        'graph_links',
                        'ledger_summary',
                        'wallet_status',
                        'wallet_history',
                        'graph_node',
                    )
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    verdict, failures = check_rc0_1_release_gate.check_release_gate(
        bundle_manifest_path=bundle_manifest_path,
        evidence_manifest_path=evidence_manifest_path,
        checklist_path=checklist_path,
        economic_manifest_path=economic_manifest_path,
        economic_proof_manifest_path=economic_proof_manifest_path,
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


def _write_release_candidate_fixture(tmp_path: Path) -> tuple[Path, Path]:
    candidate_manifest_path = tmp_path / 'candidate_manifest.json'
    closure_manifest_path = tmp_path / 'closure_manifest.json'
    release_manifest_path = tmp_path / 'release_manifest.json'
    evidence_manifest_path = tmp_path / 'evidence_manifest.json'
    bundle_manifest_path = tmp_path / 'bundle_manifest.json'
    proof_manifest_path = tmp_path / 'bundle_install_proof_manifest.json'
    economic_manifest_path = tmp_path / 'economic_manifest.json'
    economic_proof_manifest_path = tmp_path / 'economic_proof_manifest.json'
    bundle_archive_path = tmp_path / 'bundle.tar.gz'
    bundle_archive_path.write_bytes(b'rc-bundle')

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
                    'economic_cycle_projection': 'satisfied_for_testbed',
                    'release_evidence': 'satisfied_for_testbed',
                },
                'scenario_summary': {'panel_verdict_token': 'panel_quorum_passed'},
                'scenario_replay_summary': {
                    'panel_result_matches': True,
                    'ecu_claims_match': True,
                },
                'economic_summary': {'distribution_check_ok': True, 'wallet_count': 8},
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    economic_manifest_path.write_text(
        json.dumps(
            {
                'summary': {
                    'task_id': 'task:test:economic-cycle',
                    'node_count': 7,
                    'wallet_count': 8,
                    'reward_total': 5.0,
                    'distribution_check_ok': True,
                },
                'settlement_manifest': {
                    'settlement_status': 'applied',
                    'epoch_id': 'rc0_1::task:test:economic-cycle::epoch::12',
                },
                'wallet_manifest': {
                    'latest_epoch_id': 'rc0_1::task:test:economic-cycle::epoch::12',
                },
                'runtime_store': {
                    'store_kind': 'lmdb_public_runtime_v0.1',
                    'graph_store_root': str(tmp_path),
                    'wallet_store_root': str(tmp_path),
                    'ledger_store_root': str(tmp_path),
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    economic_proof_manifest_path.write_text(
        json.dumps(
            {
                'comparison': {
                    'nodes_match': True,
                    'links_match': True,
                    'wallets_match': True,
                    'ledger_match': True,
                    'quorum_match': True,
                },
                'invariant_summary': {
                    'rewarded_wallet_count': 6,
                    'epoch_record_count': 1,
                    'runtime_store': {'store_kind': 'lmdb_public_runtime_v0.1'},
                },
                'negative_path_verdict': 'pass',
                'replay_verdict': 'pass',
                'replay_settlement_status': 'idempotent_replay',
                'query_payloads': {
                    name: {'ok': True}
                    for name in (
                        'summary',
                        'store_summary',
                        'quorum_record',
                        'wallet_export',
                        'graph_summary',
                        'graph_links',
                        'ledger_summary',
                        'wallet_status',
                        'wallet_history',
                        'graph_node',
                    )
                },
                'query_timings_ms': {
                    name: 1.0
                    for name in (
                        'summary',
                        'store_summary',
                        'quorum_record',
                        'wallet_export',
                        'graph_summary',
                        'graph_links',
                        'ledger_summary',
                        'wallet_status',
                        'wallet_history',
                        'graph_node',
                    )
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    bundle_manifest_path.write_text(
        json.dumps(
            {
                'archive_path': str(bundle_archive_path),
                'archive_sha256': hashlib.sha256(b'rc-bundle').hexdigest(),
                'repo_head': 'deadbeef',
                'guidance_files': [],
                'installer_files': [],
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    proof_manifest_path.write_text(
        json.dumps(
            {
                'results': [
                    {'host': 'ilc-node-1', 'status': 'ok'},
                    {'host': 'ilc-node-2', 'status': 'ok'},
                    {'host': 'ilc-node-3', 'status': 'ok'},
                ]
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    closure_manifest_path.write_text(
        json.dumps(
            {
                'evidence_manifest_path': str(evidence_manifest_path),
                'verdict_stdout': 'rc0_1_substrate_verdict=pass',
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    release_manifest_path.write_text(
        json.dumps(
            {
                'bundle_manifest_path': str(bundle_manifest_path),
                'bundle_install_proof_manifest_path': str(proof_manifest_path),
                'economic_proof_manifest_path': str(economic_proof_manifest_path),
                'release_verdict_stdout': 'rc0_1_release_verdict=pass',
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    candidate_manifest_path.write_text(
        json.dumps(
            {
                'closure_manifest_path': str(closure_manifest_path),
                'release_manifest_path': str(release_manifest_path),
                'economic_manifest_path': str(economic_manifest_path),
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    return candidate_manifest_path, bundle_manifest_path


def test_render_rc0_1_readiness_delta_accepts_passing_candidate(tmp_path: Path) -> None:
    candidate_manifest_path, _ = _write_release_candidate_fixture(tmp_path)

    manifest = render_rc0_1_readiness_delta.render_readiness_delta(
        candidate_manifest_path=candidate_manifest_path,
    )

    assert manifest['release_candidate_ready'] is True
    assert manifest['closure_pass'] is True
    assert manifest['release_pass'] is True
    assert manifest['scenario_replay_pass'] is True
    assert manifest['bundle_install_proof_pass'] is True
    assert manifest['economic_proof_pass'] is True
    assert manifest['economic_negative_path_pass'] is True
    assert manifest['economic_replay_pass'] is True
    assert manifest['economic_claim_summary']['runtime_store_kind'] == 'lmdb_public_runtime_v0.1'
    assert manifest['economic_claim_summary']['settlement_status'] == 'applied'
    assert manifest['economic_claim_summary']['negative_path_verdict'] == 'pass'
    assert manifest['economic_claim_summary']['replay_verdict'] == 'pass'
    assert manifest['repo_head'] == 'deadbeef'


def test_render_rc0_1_readiness_delta_includes_optional_economic_summary(tmp_path: Path) -> None:
    candidate_manifest_path, _ = _write_release_candidate_fixture(tmp_path)
    candidate_manifest = json.loads(candidate_manifest_path.read_text(encoding='utf-8'))
    economic_manifest_path = tmp_path / 'economic_manifest.json'
    economic_manifest_path.write_text(
        json.dumps(
            {
                'summary': {
                    'task_id': 'task:test:economic-cycle',
                    'node_count': 7,
                    'wallet_count': 8,
                    'reward_total': 5.0,
                    'distribution_check_ok': True,
                },
                'settlement_manifest': {
                    'settlement_status': 'applied',
                    'epoch_id': 'rc0_1::task:test:economic-cycle::epoch::12',
                },
                'wallet_manifest': {
                    'latest_epoch_id': 'rc0_1::task:test:economic-cycle::epoch::12',
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    candidate_manifest['economic_manifest_path'] = str(economic_manifest_path)
    candidate_manifest_path.write_text(json.dumps(candidate_manifest, indent=2) + '\n', encoding='utf-8')

    manifest = render_rc0_1_readiness_delta.render_readiness_delta(
        candidate_manifest_path=candidate_manifest_path,
    )

    assert manifest['economic_state_present'] is True
    assert manifest['economic_manifest_path'] == str(economic_manifest_path)
    assert manifest['economic_summary']['wallet_count'] == 8
    assert manifest['economic_claim_summary']['settlement_status'] == 'applied'
    assert manifest['economic_negative_path_pass'] is True
    assert manifest['economic_replay_pass'] is True


def test_check_rc0_1_release_claim_accepts_consistent_claim(tmp_path: Path) -> None:
    candidate_manifest_path, bundle_manifest_path = _write_release_candidate_fixture(tmp_path)
    delta_manifest_path = tmp_path / 'readiness_delta.json'
    release_notes_input_path = tmp_path / 'release_notes_input.md'
    release_notes_input_path.write_text('# notes\n', encoding='utf-8')

    delta_manifest = render_rc0_1_readiness_delta.render_readiness_delta(
        candidate_manifest_path=candidate_manifest_path,
    )
    delta_manifest_path.write_text(json.dumps(delta_manifest, indent=2) + '\n', encoding='utf-8')

    claim_manifest_path = tmp_path / 'claim_manifest.json'
    claim_manifest_path.write_text(
        json.dumps(
            {
                'candidate_manifest_path': str(candidate_manifest_path),
                'closure_manifest_path': delta_manifest['closure_manifest_path'],
                'release_manifest_path': delta_manifest['release_manifest_path'],
                'evidence_manifest_path': delta_manifest['evidence_manifest_path'],
                'bundle_manifest_path': str(bundle_manifest_path),
                'bundle_install_proof_manifest_path': delta_manifest['bundle_install_proof_manifest_path'],
                'economic_proof_manifest_path': delta_manifest['economic_proof_manifest_path'],
                'economic_claim_summary': delta_manifest['economic_claim_summary'],
                'release_notes_input_path': str(release_notes_input_path),
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    verdict, failures = check_rc0_1_release_claim.check_release_claim(
        claim_manifest_path=claim_manifest_path,
        delta_manifest_path=delta_manifest_path,
    )

    assert verdict == 'pass'
    assert failures == []


def test_release_gate_rejects_failed_economic_proof(tmp_path: Path) -> None:
    archive_path = tmp_path / 'bundle.tar.gz'
    archive_path.write_bytes(b'rc-bundle')
    bundle_manifest_path = tmp_path / 'bundle_manifest.json'
    evidence_manifest_path = tmp_path / 'evidence_manifest.json'
    checklist_path = tmp_path / 'checklist.md'
    economic_manifest_path = tmp_path / 'economic_manifest.json'
    economic_proof_manifest_path = tmp_path / 'economic_proof_manifest.json'

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
                    'economic_cycle_projection': 'satisfied_for_testbed',
                    'release_evidence': 'satisfied_for_testbed',
                },
                'scenario_summary': {'panel_verdict_token': 'panel_quorum_passed'},
                'scenario_replay_summary': {'panel_result_matches': True, 'ecu_claims_match': True},
                'economic_summary': {'distribution_check_ok': True, 'wallet_count': 8},
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
    economic_manifest_path.write_text(
        json.dumps(
            {
                'summary': {'distribution_check_ok': True, 'wallet_count': 8, 'reward_total': 5.0},
                'runtime_store': {
                    'store_kind': 'lmdb_public_runtime_v0.1',
                    'graph_store_root': str(tmp_path),
                    'wallet_store_root': str(tmp_path),
                    'ledger_store_root': str(tmp_path),
                },
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    economic_proof_manifest_path.write_text(
        json.dumps(
            {
                'comparison': {'nodes_match': True, 'links_match': False},
                'invariant_summary': {'runtime_store': {'store_kind': 'lmdb_public_runtime_v0.1'}},
                'negative_path_verdict': 'pass',
                'replay_verdict': 'pass',
                'replay_settlement_status': 'idempotent_replay',
                'query_payloads': {'summary': {'ok': True}},
                'query_timings_ms': {'summary': 1.0},
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    verdict, failures = check_rc0_1_release_gate.check_release_gate(
        bundle_manifest_path=bundle_manifest_path,
        evidence_manifest_path=evidence_manifest_path,
        checklist_path=checklist_path,
        economic_manifest_path=economic_manifest_path,
        economic_proof_manifest_path=economic_proof_manifest_path,
    )

    assert verdict == 'fail'
    assert 'economic_proof_comparison_failed' in failures


def test_release_candidate_manifest_records_optional_economic_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def _fake_run(command: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command[1] == 'tools/testbed/run_rc0_1_substrate_closure.py':
            closure_root = Path(command[3])
            closure_root.mkdir(parents=True, exist_ok=True)
            (closure_root / 'scenario' / 'economic-state').mkdir(parents=True, exist_ok=True)
            (closure_root / 'scenario' / 'economic-state' / 'manifest.json').write_text(
                json.dumps({'summary': {'distribution_check_ok': True, 'wallet_count': 8}}, indent=2) + '\n',
                encoding='utf-8',
            )
            (closure_root / 'closure_manifest.json').write_text(
                json.dumps(
                    {
                        'economic_manifest_path': str(closure_root / 'scenario' / 'economic-state' / 'manifest.json'),
                    },
                    indent=2,
                ) + '\n',
                encoding='utf-8',
            )
        return subprocess.CompletedProcess(command, 0, stdout='{"marker":"ok"}', stderr='')

    monkeypatch.setattr(run_rc0_1_release_candidate, '_run', _fake_run)

    manifest = run_rc0_1_release_candidate.run_release_candidate(
        output_root=tmp_path / 'candidate',
        include_home_install_proof=True,
        emit_release_claim=True,
    )

    assert not any(command[1] == 'tools/run_rc0_1_economic_cycle.py' for command in calls)
    assert any(command[1] == 'tools/testbed/run_rc0_1_substrate_closure.py' for command in calls)
    assert manifest['economic_manifest_path'].endswith('economic-state/manifest.json')
    assert 'economic_stdout' in manifest
    assert manifest['release_claim_manifest_path'].endswith('claim/manifest.json')


def test_substrate_closure_skips_nested_diagnostics_in_recovery_and_negative_drills(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    commands: list[list[str]] = []

    def _fake_run_step(name: str, command: list[str], *, output_root: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if name == 'three_node_seven_agent':
            scenario_root = Path(command[command.index('--output-root') + 1])
            scenario_root.mkdir(parents=True, exist_ok=True)
            (scenario_root / 'economic-state').mkdir(parents=True, exist_ok=True)
            (scenario_root / 'scenario_manifest.json').write_text(
                json.dumps(
                    {
                        'economic_manifest_path': str(scenario_root / 'economic-state' / 'manifest.json'),
                    },
                    indent=2,
                ) + '\n',
                encoding='utf-8',
            )
            (scenario_root / 'economic-state' / 'manifest.json').write_text(
                json.dumps({'summary': {'distribution_check_ok': True}}, indent=2) + '\n',
                encoding='utf-8',
            )
        elif name == 'three_node_seven_agent_replay':
            replay_root = Path(command[command.index('--output-root') + 1])
            replay_root.mkdir(parents=True, exist_ok=True)
            (replay_root / 'replay_manifest.json').write_text('{}\n', encoding='utf-8')
        elif name == 'install_shape_proof':
            install_root = Path(command[command.index('--output-root') + 1])
            install_root.mkdir(parents=True, exist_ok=True)
            (install_root / 'manifest.json').write_text('{}\n', encoding='utf-8')
        elif name == 'collect_diagnostics':
            diagnostics_root = Path(env['TESTBED_DIAGNOSTICS_ROOT'])
            diagnostics_root.mkdir(parents=True, exist_ok=True)
            (diagnostics_root / 'manifest.json').write_text('{}\n', encoding='utf-8')
        elif name == 'render_evidence':
            evidence_root = Path(command[command.index('--output-root') + 1])
            evidence_root.mkdir(parents=True, exist_ok=True)
            (evidence_root / 'manifest.json').write_text('{}\n', encoding='utf-8')
        return subprocess.CompletedProcess(command, 0, stdout='ok', stderr='')

    monkeypatch.setattr(run_rc0_1_substrate_closure, '_run_step', _fake_run_step)

    manifest = run_rc0_1_substrate_closure.run_closure(
        output_root=tmp_path / 'closure',
        include_home_install_proof=True,
    )

    assert manifest['scenario_manifest_path'].endswith('scenario_manifest.json')
    recovery_command = next(command for command in commands if command[:2] == ['bash', 'tools/testbed/run_recovery_drills.sh'])
    negative_command = next(command for command in commands if command[:2] == ['bash', 'tools/testbed/run_negative_path_drills.sh'])
    assert recovery_command[-1] == '--skip-diagnostics'
    assert negative_command[-1] == '--skip-diagnostics'


def test_run_release_gate_uses_generated_economic_proof_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    evidence_root = tmp_path / 'evidence'
    evidence_root.mkdir()
    economic_manifest_path = tmp_path / 'economic' / 'manifest.json'
    economic_manifest_path.parent.mkdir(parents=True)
    economic_manifest_path.write_text(
        json.dumps(
            {
                'summary': {'distribution_check_ok': True},
                'runtime_store': {'store_kind': 'lmdb_public_runtime_v0.1'},
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    (evidence_root / 'manifest.json').write_text(
        json.dumps({'economic_manifest_path': str(economic_manifest_path)}, indent=2) + '\n',
        encoding='utf-8',
    )

    def _arg_value(command: list[str], flag: str) -> str:
        return command[command.index(flag) + 1]

    def _fake_run(command: list[str]) -> subprocess.CompletedProcess[str]:
        if command[1] == 'tools/package_rc0_1_bundle.py':
            bundle_output = Path(_arg_value(command, '--output-root'))
            bundle_output.mkdir(parents=True, exist_ok=True)
            bundle_manifest_path = bundle_output / 'manifest.json'
            bundle_manifest_path.write_text(
                json.dumps(
                    {
                        'archive_path': str(bundle_output / 'ilc_rc0_1_bundle.tar.gz'),
                        'archive_sha256': hashlib.sha256(b'rc-bundle').hexdigest(),
                        'repo_head': 'deadbeef',
                        'guidance_files': [],
                        'installer_files': [],
                        'manifest_path': str(bundle_manifest_path),
                    },
                    indent=2,
                ) + '\n',
                encoding='utf-8',
            )
            (bundle_output / 'ilc_rc0_1_bundle.tar.gz').write_bytes(b'rc-bundle')
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'marker': 'ok', 'manifest': {'manifest_path': str(bundle_manifest_path)}}),
                stderr='',
            )
        if command[1] == 'tools/prove_rc0_1_bundle_install.py':
            proof_output = Path(_arg_value(command, '--output-root'))
            proof_output.mkdir(parents=True, exist_ok=True)
            proof_manifest_path = proof_output / 'manifest.json'
            proof_manifest_path.write_text(json.dumps({'results': [{'host': 'ilc-node-1', 'status': 'ok'}]}, indent=2) + '\n', encoding='utf-8')
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'marker': 'ok', 'manifest': {'manifest_path': str(proof_manifest_path)}}),
                stderr='',
            )
        if command[1] == 'tools/run_rc0_1_economic_proof.py':
            proof_output = Path(_arg_value(command, '--output-root'))
            proof_output.mkdir(parents=True, exist_ok=True)
            proof_manifest_path = proof_output / 'manifest.json'
            proof_manifest_path.write_text(
                json.dumps(
                    {
                        'proof_runner_manifest_path': str(proof_manifest_path),
                        'comparison': {
                            'nodes_match': True,
                            'links_match': True,
                            'wallets_match': True,
                            'ledger_match': True,
                            'quorum_match': True,
                        },
                        'invariant_summary': {'runtime_store': {'store_kind': 'lmdb_public_runtime_v0.1'}},
                        'negative_path_verdict': 'pass',
                        'replay_verdict': 'pass',
                        'replay_settlement_status': 'idempotent_replay',
                        'query_payloads': {
                            name: {'ok': True}
                            for name in (
                                'summary',
                                'store_summary',
                                'quorum_record',
                                'wallet_export',
                                'graph_summary',
                                'graph_links',
                                'ledger_summary',
                                'wallet_status',
                                'wallet_history',
                                'graph_node',
                            )
                        },
                        'query_timings_ms': {
                            name: 1.0
                            for name in (
                                'summary',
                                'store_summary',
                                'quorum_record',
                                'wallet_export',
                                'graph_summary',
                                'graph_links',
                                'ledger_summary',
                                'wallet_status',
                                'wallet_history',
                                'graph_node',
                            )
                        },
                    },
                    indent=2,
                ) + '\n',
                encoding='utf-8',
            )
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'marker': 'ok', 'manifest': {'proof_runner_manifest_path': str(proof_manifest_path)}}),
                stderr='',
            )
        if command[1] == 'tools/check_rc0_1_release_gate.py':
            assert _arg_value(command, '--economic-proof-manifest').endswith('/economic-proof/manifest.json')
            return subprocess.CompletedProcess(command, 0, stdout='rc0_1_release_verdict=pass\n', stderr='')
        raise AssertionError(f'unexpected command: {command}')

    monkeypatch.setattr(run_rc0_1_release_gate, '_run', _fake_run)

    manifest = run_rc0_1_release_gate.run_release_gate(
        evidence_root=evidence_root,
        output_root=tmp_path / 'release',
    )

    assert manifest['economic_proof_manifest_path'].endswith('/economic-proof/manifest.json')
