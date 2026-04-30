"""KPAX token ledger — v0 centralized accounting.

Ken 2026-04-17 晚 platform 定位修订（PRD §13.4 §13.5）:
  - 命名从 `wallet_id` 升级为 `wallet_address`，为 v2 去中心化迁移打基础
    （v0 中心化，格式不强制；v1 EVM 兼容；v2 链上钱包）。
  - Event 分层：每条 LedgerEntry 标 `event_type` ∈ {kpax_token_delta, llm_cost_usd}。
      · kpax_token_delta —— 平台代币变化（v0 主产品免费所以扣款少）
      · llm_cost_usd     —— 本次请求实际烧的 LLM API 成本，USD * 10000（定点整数）
    v0 主产品免费 → 用户 kpax_token_delta 几乎不扣；但 llm_cost_usd 每次都记，
    平台自己承担 LLM 成本，用于审计 / 未来 BYOM 对账 / 商业模式验证。

Earlier Ken 2026-04-15 硬规则 #4 仍然成立:
  付费 = 代币。消耗 token 用 / 分享赚 token / Solana + Base 双链买入。
  v0 中心化记账，预留合约接口。后面上链。

This module is the **only** place KPAX touches balance/charge/reward.
v0 storage is an in-memory dict with an append-only jsonl audit log —
crash-safe enough for dev, not for production. Swap the backing store
via `LedgerStorage` when we wire real wallets.
"""

from __future__ import annotations

import json
import os
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# PRD §13.4: opaque string, format-loose in v0 (guest UUID), tightened in v1
# (0x-prefixed EVM address), real wallet in v2. The old `WalletId` alias is
# intentionally NOT kept — forcing callers to spell out `wallet_address` keeps
# the deprecated name from leaking back in during future refactors.
WalletAddress = str

Reason = Literal[
    "topup",           # admin or dex purchase credits wallet
    "reward_share",    # user shared, earned tokens
    "reward_bonus",    # system-granted (signup, referral target)
    "charge_analyze",  # user ran an analyze request
    "refund",          # analyze failed, refund
    "llm_cost",        # PRD §13.5: record LLM API cost in USD (platform-side audit)
]

EventType = Literal[
    "kpax_token_delta",  # platform token movement (balance ledger)
    "llm_cost_usd",      # LLM API spend, in USD * 10000 (fixed-point, no float rounding)
]

# Convert USD → fixed-point integer (1 unit = $0.0001). Stored this way so the
# audit log stays integer-clean even when we aggregate across thousands of rows.
USD_FIXED_POINT_SCALE: int = 10_000


@dataclass
class LedgerEntry:
    ts: float
    wallet_address: WalletAddress
    delta: int           # positive = credit, negative = debit; in platform tokens or USD*10000 depending on event_type
    balance_after: int   # platform-token balance snapshot (unused / 0 for llm_cost_usd rows)
    reason: Reason
    event_type: EventType = "kpax_token_delta"
    request_hash: str | None = None
    note: str = ""


@dataclass
class Wallet:
    wallet_address: WalletAddress
    balance: int = 0
    created_at: float = field(default_factory=time.time)


# ── storage abstraction ────────────────────────────────────────

class LedgerStorage(ABC):
    """Abstract storage for wallets + audit log.

    v0 implementation is in-memory + jsonl. Swap for Postgres/SQLite
    in v0.1 without touching `TokenLedger` or callers.
    """

    @abstractmethod
    def get_wallet(self, wallet_address: WalletAddress) -> Wallet | None: ...

    @abstractmethod
    def put_wallet(self, wallet: Wallet) -> None: ...

    @abstractmethod
    def append_entry(self, entry: LedgerEntry) -> None: ...

    @abstractmethod
    def entries_for(self, wallet_address: WalletAddress, limit: int = 100) -> list[LedgerEntry]: ...


class InMemoryJsonlStorage(LedgerStorage):
    """Dev storage: dict in RAM + append-only jsonl audit on disk."""

    def __init__(self, jsonl_path: str | Path | None = None) -> None:
        self._wallets: dict[WalletAddress, Wallet] = {}
        self._entries: list[LedgerEntry] = []
        self._lock = threading.Lock()
        self._jsonl_path = Path(jsonl_path) if jsonl_path else None
        if self._jsonl_path is not None:
            self._jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            self._replay_from_disk()

    def _replay_from_disk(self) -> None:
        if not self._jsonl_path or not self._jsonl_path.exists():
            return
        with self._jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Backward-compat: legacy rows may still carry `wallet_id`
                wallet_address = rec.get("wallet_address") or rec.get("wallet_id")
                if not wallet_address:
                    continue
                entry = LedgerEntry(
                    ts=rec["ts"],
                    wallet_address=wallet_address,
                    delta=rec["delta"],
                    balance_after=rec["balance_after"],
                    reason=rec["reason"],
                    event_type=rec.get("event_type", "kpax_token_delta"),
                    request_hash=rec.get("request_hash"),
                    note=rec.get("note", ""),
                )
                self._entries.append(entry)
                if entry.event_type == "kpax_token_delta":
                    w = self._wallets.setdefault(
                        entry.wallet_address, Wallet(entry.wallet_address)
                    )
                    w.balance = entry.balance_after

    def get_wallet(self, wallet_address: WalletAddress) -> Wallet | None:
        with self._lock:
            return self._wallets.get(wallet_address)

    def put_wallet(self, wallet: Wallet) -> None:
        with self._lock:
            self._wallets[wallet.wallet_address] = wallet

    def append_entry(self, entry: LedgerEntry) -> None:
        with self._lock:
            self._entries.append(entry)
            if self._jsonl_path is not None:
                with self._jsonl_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")

    def entries_for(self, wallet_address: WalletAddress, limit: int = 100) -> list[LedgerEntry]:
        with self._lock:
            hits = [e for e in self._entries if e.wallet_address == wallet_address]
            return hits[-limit:]


# ── chain adapter interface (stub for Solana / Base) ──────────

class ChainAdapter(ABC):
    """Future hook for on-chain wallet verification + topup.

    v0 KPAX does not call this. When Solana/Base go live, each chain
    gets a concrete subclass, and `TokenLedger` routes by wallet_address
    prefix. Not implemented yet on purpose — just frozen shape.
    """

    chain_name: str

    @abstractmethod
    async def verify_wallet(self, wallet_address: WalletAddress, signature: str) -> bool: ...

    @abstractmethod
    async def on_chain_balance(self, wallet_address: WalletAddress) -> int: ...

    @abstractmethod
    async def mint_reward(self, wallet_address: WalletAddress, amount: int, memo: str) -> str: ...


# ── core ledger ────────────────────────────────────────────────

class InsufficientBalance(Exception):
    pass


class TokenLedger:
    """Centralized v0 token accounting.

    All balance changes go through `charge` / `reward` / `topup` /
    `refund`. Each call appends one immutable `LedgerEntry` and updates
    the wallet balance atomically under a single storage lock.

    PRD §13.5 event layering:
      - kpax_token_delta events (charge / reward / topup / refund) move
        the wallet balance and are what users see
      - llm_cost_usd events (record_llm_cost) track platform-side LLM
        API spend; they do NOT touch the wallet balance in v0 (free main
        product) — they are kept strictly for platform-side audit.
    """

    # v0 pricing — tune as dry run data comes in
    COST_PER_DEPTH: dict[str, int] = {
        "quick": 10,
        "standard": 25,
        "deep": 60,
    }
    REWARD_SHARE: int = 20       # user shares a report, gets 20
    GUEST_STARTING_BALANCE: int = 50   # new guest wallet seeded with 50

    def __init__(self, storage: LedgerStorage | None = None) -> None:
        self._storage = storage or InMemoryJsonlStorage(
            jsonl_path=os.getenv("KPAX_LEDGER_JSONL", "kpax_data/ledger.jsonl")
        )
        # RLock (reentrant): charge / refund / record_llm_cost all grab the
        # lock then call get_or_create_wallet which also grabs it. Plain
        # threading.Lock deadlocks on the nested acquisition.
        self._lock = threading.RLock()

    # balance ops --------------------------------------------------

    def get_or_create_wallet(self, wallet_address: WalletAddress) -> Wallet:
        with self._lock:
            wallet = self._storage.get_wallet(wallet_address)
            if wallet is not None:
                return wallet
            wallet = Wallet(wallet_address=wallet_address, balance=0)
            self._storage.put_wallet(wallet)
            # seed guest wallet
            if wallet_address.startswith("guest_"):
                self._apply(wallet, +self.GUEST_STARTING_BALANCE, "reward_bonus", note="guest seed")
            return wallet

    def balance(self, wallet_address: WalletAddress) -> int:
        wallet = self.get_or_create_wallet(wallet_address)
        return wallet.balance

    def quote_charge(self, depth: str) -> int:
        if depth not in self.COST_PER_DEPTH:
            raise ValueError(f"unknown depth: {depth}")
        return self.COST_PER_DEPTH[depth]

    def charge(
        self,
        wallet_address: WalletAddress,
        depth: str,
        request_hash: str,
    ) -> LedgerEntry:
        cost = self.quote_charge(depth)
        with self._lock:
            wallet = self.get_or_create_wallet(wallet_address)
            if wallet.balance < cost:
                raise InsufficientBalance(
                    f"wallet {wallet_address} balance {wallet.balance} < cost {cost}"
                )
            return self._apply(wallet, -cost, "charge_analyze", request_hash=request_hash)

    def refund(self, wallet_address: WalletAddress, amount: int, request_hash: str) -> LedgerEntry:
        with self._lock:
            wallet = self.get_or_create_wallet(wallet_address)
            return self._apply(wallet, +amount, "refund", request_hash=request_hash)

    def reward_share(self, wallet_address: WalletAddress, note: str = "") -> LedgerEntry:
        with self._lock:
            wallet = self.get_or_create_wallet(wallet_address)
            return self._apply(wallet, +self.REWARD_SHARE, "reward_share", note=note)

    def topup(self, wallet_address: WalletAddress, amount: int, note: str = "") -> LedgerEntry:
        if amount <= 0:
            raise ValueError("topup amount must be positive")
        with self._lock:
            wallet = self.get_or_create_wallet(wallet_address)
            return self._apply(wallet, +amount, "topup", note=note)

    def record_llm_cost(
        self,
        wallet_address: WalletAddress,
        cost_usd: float,
        request_hash: str,
        note: str = "",
    ) -> LedgerEntry:
        """Platform-side audit of actual LLM API spend (PRD §13.5).

        v0 main product is free so the wallet balance is NOT debited. The
        entry is an append-only audit row only. v1 BYOM flips this to "paid
        from user's API key, not the platform"; v2 on-chain records both.
        """
        delta_fp = int(round(cost_usd * USD_FIXED_POINT_SCALE))
        with self._lock:
            wallet = self.get_or_create_wallet(wallet_address)
            entry = LedgerEntry(
                ts=time.time(),
                wallet_address=wallet.wallet_address,
                delta=-delta_fp,             # negative because cost is outflow from platform
                balance_after=wallet.balance,  # wallet balance unchanged for llm_cost_usd
                reason="llm_cost",
                event_type="llm_cost_usd",
                request_hash=request_hash,
                note=note,
            )
            self._storage.append_entry(entry)
            return entry

    def history(self, wallet_address: WalletAddress, limit: int = 100) -> list[LedgerEntry]:
        return self._storage.entries_for(wallet_address, limit=limit)

    # internal -----------------------------------------------------

    def _apply(
        self,
        wallet: Wallet,
        delta: int,
        reason: Reason,
        request_hash: str | None = None,
        note: str = "",
    ) -> LedgerEntry:
        wallet.balance += delta
        self._storage.put_wallet(wallet)
        entry = LedgerEntry(
            ts=time.time(),
            wallet_address=wallet.wallet_address,
            delta=delta,
            balance_after=wallet.balance,
            reason=reason,
            event_type="kpax_token_delta",
            request_hash=request_hash,
            note=note,
        )
        self._storage.append_entry(entry)
        return entry
