import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from backend.services.evidence_chain import EvidenceChain
from backend.models.orm import Evidence

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def evidence_chain(mock_db_session):
    return EvidenceChain(db=mock_db_session)

@pytest.mark.asyncio
async def test_verify_integrity_empty(evidence_chain, mock_db_session):
    # Setup mock to return no blocks
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    threat_id = uuid.uuid4()
    result = await evidence_chain.verify_integrity(threat_id)

    assert result == {"valid": False, "reason": "Audit trail is empty"}
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_verify_integrity_valid_chain(evidence_chain, mock_db_session):
    threat_id = uuid.uuid4()
    ts1 = datetime.utcnow()
    ts2 = datetime.utcnow()

    # Create block 1
    block1 = Evidence(
        threat_id=threat_id,
        previous_hash="0" * 64,
        payload={"event": "1"},
        timestamp=ts1
    )
    block1.current_hash = evidence_chain._generate_hash(block1.previous_hash, block1.payload, block1.timestamp.isoformat())
    block1.digital_signature = evidence_chain._generate_signature(block1.current_hash)

    # Create block 2
    block2 = Evidence(
        threat_id=threat_id,
        previous_hash=block1.current_hash,
        payload={"event": "2"},
        timestamp=ts2
    )
    block2.current_hash = evidence_chain._generate_hash(block2.previous_hash, block2.payload, block2.timestamp.isoformat())
    block2.digital_signature = evidence_chain._generate_signature(block2.current_hash)

    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [block1, block2]
    mock_db_session.execute.return_value = mock_result

    result = await evidence_chain.verify_integrity(threat_id)

    assert result == {"valid": True, "blocks_checked": 2, "last_hash": block2.current_hash}

@pytest.mark.asyncio
async def test_verify_integrity_hash_mismatch(evidence_chain, mock_db_session):
    threat_id = uuid.uuid4()
    ts1 = datetime.utcnow()

    block1 = Evidence(
        threat_id=threat_id,
        previous_hash="0" * 64,
        payload={"event": "1"},
        timestamp=ts1
    )
    block1.current_hash = "invalid_hash"
    block1.digital_signature = evidence_chain._generate_signature(block1.current_hash)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [block1]
    mock_db_session.execute.return_value = mock_result

    result = await evidence_chain.verify_integrity(threat_id)

    assert result == {"valid": False, "reason": "Hash mismatch", "block_index": 0}

@pytest.mark.asyncio
async def test_verify_integrity_invalid_signature(evidence_chain, mock_db_session):
    threat_id = uuid.uuid4()
    ts1 = datetime.utcnow()

    block1 = Evidence(
        threat_id=threat_id,
        previous_hash="0" * 64,
        payload={"event": "1"},
        timestamp=ts1
    )
    block1.current_hash = evidence_chain._generate_hash(block1.previous_hash, block1.payload, block1.timestamp.isoformat())
    block1.digital_signature = "invalid_signature"

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [block1]
    mock_db_session.execute.return_value = mock_result

    result = await evidence_chain.verify_integrity(threat_id)

    assert result == {"valid": False, "reason": "Signature invalid", "block_index": 0}

@pytest.mark.asyncio
async def test_verify_integrity_broken_chain(evidence_chain, mock_db_session):
    threat_id = uuid.uuid4()
    ts1 = datetime.utcnow()
    ts2 = datetime.utcnow()

    block1 = Evidence(
        threat_id=threat_id,
        previous_hash="0" * 64,
        payload={"event": "1"},
        timestamp=ts1
    )
    block1.current_hash = evidence_chain._generate_hash(block1.previous_hash, block1.payload, block1.timestamp.isoformat())
    block1.digital_signature = evidence_chain._generate_signature(block1.current_hash)

    block2 = Evidence(
        threat_id=threat_id,
        previous_hash="wrong_previous_hash",
        payload={"event": "2"},
        timestamp=ts2
    )
    block2.current_hash = evidence_chain._generate_hash(block2.previous_hash, block2.payload, block2.timestamp.isoformat())
    block2.digital_signature = evidence_chain._generate_signature(block2.current_hash)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [block1, block2]
    mock_db_session.execute.return_value = mock_result

    result = await evidence_chain.verify_integrity(threat_id)

    assert result == {"valid": False, "reason": "Chain linkage broken", "block_index": 1}