from __future__ import annotations

from unittest.mock import patch

from ilc_core.network.d2d import centrality_delta_gossip_runtime, gossip, gossip_transport, interface


def _base_headers() -> dict[str, str]:
    return gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )


def test_validate_gossip_headers_rejects_non_integer_epoch_with_structured_token() -> None:
    for invalid_epoch in ('not_a_number', '7.5', ''):
        headers = _base_headers()
        headers['ILC-Epoch'] = invalid_epoch
        try:
            gossip_transport.validate_gossip_headers(headers)
        except ValueError as exc:
            assert str(exc) == 'epoch_must_be_integer'
        else:
            raise AssertionError(f'expected ValueError for invalid epoch {invalid_epoch!r}')


def test_validate_gossip_headers_rejects_negative_epoch_with_structured_token() -> None:
    headers = _base_headers()
    headers['ILC-Epoch'] = '-999999'
    try:
        gossip_transport.validate_gossip_headers(headers)
    except ValueError as exc:
        assert str(exc) == 'epoch_must_be_non_negative'
    else:
        raise AssertionError('expected ValueError for negative epoch header')


def test_canonical_forbidden_match_tracks_exported_forbidden_keys() -> None:
    for key in gossip_transport.FORBIDDEN_HEADER_KEYS:
        assert gossip_transport._canonical_forbidden_match(key) is True
        assert gossip_transport._canonical_forbidden_match(key.lower()) is True


def test_gossip_transport_runtime_errors_from_channel_validator_are_not_masked() -> None:
    with patch(
        'ilc_core.network.d2d.gossip_transport.validate_gossip_channel',
        side_effect=RuntimeError('boom'),
    ):
        try:
            gossip_transport._validated_channel('cid:9f7a8c42bb11ddee99aa22cc33ff44aa')
        except RuntimeError as exc:
            assert str(exc) == 'boom'
        else:
            raise AssertionError('expected RuntimeError to propagate from gossip_transport')


def test_centrality_runtime_errors_from_channel_validator_are_not_masked() -> None:
    with patch(
        'ilc_core.network.d2d.centrality_delta_gossip_runtime.validate_gossip_channel',
        side_effect=RuntimeError('boom'),
    ):
        try:
            centrality_delta_gossip_runtime._validate_channel('cid:9f7a8c42bb11ddee99aa22cc33ff44aa')
        except RuntimeError as exc:
            assert str(exc) == 'boom'
        else:
            raise AssertionError('expected RuntimeError to propagate from centrality runtime')


def test_gossip_module_reuses_interface_canonical_header_alias() -> None:
    assert gossip._canonical_header_alias is interface._canonical_header_alias
