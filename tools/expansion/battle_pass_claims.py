"""NARIS reference battle-pass claim ledger (SQLite, no reward fulfillment).

This is an engine-neutral prototype. The authoritative Unreal/game service must
verify XP awards and payment entitlements. Do not expose this as a public endpoint.
"""
import sqlite3


def ensure_claim_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS naris_pass_claims (
        player_id TEXT NOT NULL,
        season_id TEXT NOT NULL,
        tier INTEGER NOT NULL CHECK(tier BETWEEN 1 AND 100),
        track TEXT NOT NULL CHECK(track IN ('free','premium')),
        PRIMARY KEY(player_id,season_id,tier,track)
    )""")


def claim_reward(connection: sqlite3.Connection, player_id: str, season_id: str,
                 tier: int, track: str, earned_xp: int, premium_verified: bool) -> bool:
    """Return True exactly once for an eligible claim; NO inventory grant occurs."""
    if type(tier) is not int or not 1 <= tier <= 100:
        raise ValueError("invalid tier")
    if track not in ("free", "premium"):
        raise ValueError("invalid track")
    if not player_id or not season_id or not season_id.isascii() or len(season_id) > 64:
        raise ValueError("invalid player or season")
    if type(earned_xp) is not int or earned_xp < 0:
        raise ValueError("invalid earned XP")
    if type(premium_verified) is not bool:
        raise ValueError("premium_verified must be authoritative bool")
    unlocked_tier = min(100, 1 + earned_xp // 1000)
    if tier > unlocked_tier or (track == "premium" and not premium_verified):
        return False
    ensure_claim_schema(connection)
    # Caller supplies the durable, authoritative database. Unique key protects
    # against duplicate claims, including process restarts.
    cursor = connection.execute(
        """INSERT OR IGNORE INTO naris_pass_claims
           (player_id,season_id,tier,track) VALUES(?,?,?,?)""",
        (player_id,season_id,tier,track))
    connection.commit()
    return cursor.rowcount == 1


def claims_for_player(connection: sqlite3.Connection, player_id: str, season_id: str):
    ensure_claim_schema(connection)
    return [tuple(row) for row in connection.execute(
        """SELECT tier,track FROM naris_pass_claims
           WHERE player_id=? AND season_id=? ORDER BY tier,track""",
        (player_id,season_id))]
