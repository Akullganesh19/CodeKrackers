import hashlib
import hmac
import json
import uuid
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..models.orm import Evidence
from ..models.orm import Threat
from ..models.orm import FIR
from ..models.orm import User

class EvidenceChain:
    """
    Cryptographic ledger logic for maintaining a tamper-proof chain of custody
    for forensic evidence related to Vishing and Smishing threats.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        # Secret key used for signing blocks to ensure authenticity. 
        self.secret_key = os.getenv("SECRET_KEY", "your-super-secret-key-for-vsdp-platform").encode()

    def _generate_hash(self, previous_hash: str, payload: dict, timestamp: str) -> str:
        """
        Computes SHA-256 hash of the block data (linkage + content + time).
        """
        payload_str = json.dumps(payload, sort_keys=True)
        block_string = f"{previous_hash}{payload_str}{timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def _generate_signature(self, current_hash: str) -> str:
        """
        Signs the block hash using HMAC-SHA256 to prove provenance.
        """
        return hmac.new(self.secret_key, current_hash.encode(), hashlib.sha256).hexdigest()

    async def create_genesis_block(self, threat_id: uuid.UUID) -> Evidence:
        """
        Initializes the cryptographic chain for a newly detected threat.
        """
        timestamp = datetime.utcnow().isoformat()
        previous_hash = "0" * 64
        payload = {"event": "GENESIS_THREAT_DETECTION", "threat_id": str(threat_id)}
        
        current_hash = self._generate_hash(previous_hash, payload, timestamp)
        signature = self._generate_signature(current_hash)
        
        genesis_block = Evidence(
            threat_id=threat_id,
            previous_hash=previous_hash,
            current_hash=current_hash,
            payload=payload,
            digital_signature=signature,
            block_type='threat_detected',
            timestamp=datetime.fromisoformat(timestamp)
        )
        
        self.db.add(genesis_block)
        await self.db.commit()
        await self.db.refresh(genesis_block)
        return genesis_block

    async def add_block(self, threat_id: uuid.UUID, block_type: str, payload: dict) -> Evidence:
        """
        Appends a new forensic event to the chain, linking it cryptographically 
        to the previous state.
        """
        result = await self.db.execute(
            select(Evidence)
            .where(Evidence.threat_id == threat_id)
            .order_by(desc(Evidence.timestamp))
        )
        last_block = result.scalars().first()
        
        if not last_block:
            last_block = await self.create_genesis_block(threat_id)
            
        previous_hash = last_block.current_hash
        timestamp = datetime.utcnow().isoformat()
        
        current_hash = self._generate_hash(previous_hash, payload, timestamp)
        signature = self._generate_signature(current_hash)
        
        new_block = Evidence(
            threat_id=threat_id,
            previous_hash=previous_hash,
            current_hash=current_hash,
            payload=payload,
            digital_signature=signature,
            block_type=block_type,
            timestamp=datetime.fromisoformat(timestamp)
        )
        
        self.db.add(new_block)
        await self.db.commit()
        await self.db.refresh(new_block)
        return new_block

    async def verify_integrity(self, threat_id: uuid.UUID) -> dict:
        """
        Validates the entire chain of custody for a specific case by 
        re-calculating all hashes and verifying signatures and links.
        """
        result = await self.db.execute(
            select(Evidence)
            .where(Evidence.threat_id == threat_id)
            .order_by(Evidence.timestamp)
        )
        blocks = result.scalars().all()
        
        if not blocks:
            return {"valid": False, "reason": "Audit trail is empty"}
            
        for i, block in enumerate(blocks):
            expected_hash = self._generate_hash(
                block.previous_hash, 
                block.payload, 
                block.timestamp.isoformat()
            )
            if block.current_hash != expected_hash:
                return {"valid": False, "reason": "Hash mismatch", "block_index": i}
                
            expected_sig = self._generate_signature(block.current_hash)
            if block.digital_signature != expected_sig:
                return {"valid": False, "reason": "Signature invalid", "block_index": i}
                
            if i > 0 and block.previous_hash != blocks[i-1].current_hash:
                return {"valid": False, "reason": "Chain linkage broken", "block_index": i}
                    
        return {"valid": True, "blocks_checked": len(blocks), "last_hash": blocks[-1].current_hash}

    async def package_evidence(self, threat_id: uuid.UUID) -> dict:
        """
        Compiles a comprehensive forensic report containing the threat details,
        complainant info, FIR details, and the full blockchain audit trail.
        """
        # 1. Verify integrity of the chain before packaging
        verification = await self.verify_integrity(threat_id)

        # 2. Fetch threat and associated user details
        threat_result = await self.db.execute(
            select(Threat, User)
            .join(User, Threat.user_id == User.id)
            .where(Threat.id == threat_id)
        )
        data = threat_result.first()
        if not data:
            raise ValueError(f"Forensic report failed: Threat {threat_id} not found.")
        
        threat, user = data

        # 3. Fetch FIR if it has been generated for this threat
        fir_result = await self.db.execute(select(FIR).where(FIR.threat_id == threat_id))
        fir = fir_result.scalar_one_or_none()

        # 4. Fetch all blocks in the evidence chain
        blocks_result = await self.db.execute(
            select(Evidence)
            .where(Evidence.threat_id == threat_id)
            .order_by(Evidence.timestamp)
        )
        blocks = blocks_result.scalars().all()

        return {
            "threat_id": str(threat_id),
            "verification_status": verification,
            "complainant": {"name": user.full_name, "email": user.email, "phone": user.phone},
            "incident": {c.name: getattr(threat, c.name) for c in threat.__table__.columns},
            "fir_filing": {c.name: getattr(fir, c.name) for c in fir.__table__.columns} if fir else None,
            "blockchain_audit_trail": [
                {
                    c.name: getattr(b, c.name)
                    for c in b.__table__.columns
                }
                for b in blocks
            ]
        }