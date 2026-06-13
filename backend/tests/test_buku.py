"""Book catalog read tests (CAT-01, CAT-02).

These tests are expected to FAIL (RED) initially because the
buku router and schemas do not exist yet. Plan 02-01 implements
the read endpoints to turn them GREEN.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.buku import Buku
from app.models.salinan_buku import SalinanBuku
from app.models.enums import KondisiBuku, StatusSalinan


def _register_and_login(client: TestClient, email: str = "test@example.com") -> str:
    """Helper: register a mahasiswa and return a Bearer token."""
    client.post(
        "/api/autentikasi/registrasi",
        json={
            "nama": "Test User",
            "email": email,
            "kata_sandi": "password123",
        },
    )
    resp = client.post(
        "/api/autentikasi/masuk",
        json={"email": email, "kata_sandi": "password123"},
    )
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_list_buku(client: TestClient, db_session: Session) -> None:
    """GET /api/buku returns all books with derived availability flag."""
    token = _register_and_login(client)

    # Seed 2 books with copies directly
    buku1 = Buku(
        judul="Buku Satu",
        penulis="Penulis Satu",
        isbn="9781234567890",
        kategori="Fiksi",
        tahun_terbit=2020,
    )
    buku2 = Buku(
        judul="Buku Dua",
        penulis="Penulis Dua",
        isbn="9780987654321",
        kategori="Non-Fiksi",
        tahun_terbit=2021,
    )
    db_session.add_all([buku1, buku2])
    db_session.flush()

    salinan = SalinanBuku(
        id_buku=buku1.id,
        lokasi_rak="A-1",
        kondisi=KondisiBuku.bagus,
        status_ketersediaan=StatusSalinan.tersedia,
    )
    db_session.add(salinan)
    db_session.commit()

    response = client.get(
        "/api/buku", headers=_auth_header(token)
    )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert "items" in data, f"Response missing 'items': {data}"
    assert len(data["items"]) == 2, (
        f"Expected 2 items, got {len(data['items'])}: {data}"
    )
    # Check tersedia flag
    for item in data["items"]:
        assert "tersedia" in item, f"Item missing 'tersedia': {item}"
        assert isinstance(item["tersedia"], bool), (
            f"tersedia should be bool, got {type(item['tersedia'])}"
        )
    # Buku Satu has a tersedia copy
    satu = [b for b in data["items"] if b["judul"] == "Buku Satu"][0]
    assert satu["tersedia"] is True, f"Buku Satu should be tersedia: {satu}"

    # Buku Dua has no copies
    dua = [b for b in data["items"] if b["judul"] == "Buku Dua"][0]
    assert dua["tersedia"] is False, f"Buku Dua should not be tersedia: {dua}"


def test_search_buku(client: TestClient, db_session: Session) -> None:
    """GET /api/buku?kata_kunci=... matches judul, penulis, or isbn."""
    token = _register_and_login(client)

    buku = Buku(
        judul="Sapiens: Riwayat Singkat",
        penulis="Yuval Noah Harari",
        isbn="9786020641395",
        kategori="Non-Fiksi",
        tahun_terbit=2018,
    )
    db_session.add(buku)
    db_session.commit()

    # Search by judul substring (case-insensitive)
    resp = client.get(
        "/api/buku?kata_kunci=sapiens", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()
    assert len(data["items"]) == 1, f"Expected 1 result for 'sapiens': {data}"
    assert data["items"][0]["judul"] == buku.judul

    # Search by penulis substring
    resp = client.get(
        "/api/buku?kata_kunci=harari", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    assert len(resp.json()["items"]) == 1

    # Search by isbn
    resp = client.get(
        "/api/buku?kata_kunci=9786020641395", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    assert len(resp.json()["items"]) == 1

    # No match
    resp = client.get(
        "/api/buku?kata_kunci=zzzzzzz", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    assert len(resp.json()["items"]) == 0


def test_filter_kategori(client: TestClient, db_session: Session) -> None:
    """GET /api/buku?kategori=... filters by category (multi-select OR)."""
    token = _register_and_login(client)

    buku1 = Buku(
        judul="Fiksi Book",
        penulis="Author A",
        isbn="9781111111111",
        kategori="Fiksi",
        tahun_terbit=2020,
    )
    buku2 = Buku(
        judul="Non-Fiksi Book",
        penulis="Author B",
        isbn="9782222222222",
        kategori="Non-Fiksi",
        tahun_terbit=2020,
    )
    buku3 = Buku(
        judul="Referensi Book",
        penulis="Author C",
        isbn="9783333333333",
        kategori="Referensi",
        tahun_terbit=2020,
    )
    db_session.add_all([buku1, buku2, buku3])
    db_session.commit()

    # Single category
    resp = client.get(
        "/api/buku?kategori=Fiksi", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    assert len(resp.json()["items"]) == 1
    assert resp.json()["items"][0]["kategori"] == "Fiksi"

    # Multi-category (OR)
    resp = client.get(
        "/api/buku?kategori=Fiksi&kategori=Non-Fiksi",
        headers=_auth_header(token),
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    items = resp.json()["items"]
    assert len(items) == 2, f"Expected 2 items, got {len(items)}: {items}"
    kategoris = {item["kategori"] for item in items}
    assert kategoris == {"Fiksi", "Non-Fiksi"}, f"Unexpected categories: {kategoris}"


def test_kategori_endpoint(client: TestClient, db_session: Session) -> None:
    """GET /api/buku/kategori returns sorted distinct categories."""
    token = _register_and_login(client)

    buku1 = Buku(
        judul="B Z",
        penulis="A",
        isbn="9784444444444",
        kategori="Referensi",
        tahun_terbit=2020,
    )
    buku2 = Buku(
        judul="A A",
        penulis="B",
        isbn="9785555555555",
        kategori="Fiksi",
        tahun_terbit=2020,
    )
    db_session.add_all([buku1, buku2])
    db_session.commit()

    resp = client.get(
        "/api/buku/kategori", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert data == ["Fiksi", "Referensi"], f"Unexpected categories: {data}"


def test_detail_buku(client: TestClient, db_session: Session) -> None:
    """GET /api/buku/{id} returns buku with salinan list."""
    token = _register_and_login(client)

    buku = Buku(
        judul="Cantik Itu Luka",
        penulis="Eka Kurniawan",
        isbn="9789793062880",
        kategori="Fiksi",
        tahun_terbit=2002,
    )
    db_session.add(buku)
    db_session.flush()

    salinan1 = SalinanBuku(
        id_buku=buku.id,
        lokasi_rak="B-12",
        kondisi=KondisiBuku.bagus,
        status_ketersediaan=StatusSalinan.tersedia,
    )
    salinan2 = SalinanBuku(
        id_buku=buku.id,
        lokasi_rak="C-3",
        kondisi=KondisiBuku.rusak_ringan,
        status_ketersediaan=StatusSalinan.dipinjam,
    )
    db_session.add_all([salinan1, salinan2])
    db_session.commit()

    resp = client.get(
        f"/api/buku/{buku.id}", headers=_auth_header(token)
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()
    assert data["judul"] == "Cantik Itu Luka"
    assert data["tersedia"] is True  # at least one tersedia copy
    assert "salinan" in data, f"Missing 'salinan': {data}"
    assert len(data["salinan"]) == 2, (
        f"Expected 2 salinan, got {len(data['salinan'])}"
    )
    # Check salinan fields
    for salinan in data["salinan"]:
        assert "lokasi_rak" in salinan
        assert "kondisi" in salinan
        assert "status_ketersediaan" in salinan


def test_detail_buku_404(client: TestClient, db_session: Session) -> None:
    """GET /api/buku/{id} with unknown id returns 404."""
    token = _register_and_login(client)
    unknown_id = uuid.uuid4()
    resp = client.get(
        f"/api/buku/{unknown_id}", headers=_auth_header(token)
    )
    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


def test_list_buku_unauthorized(client: TestClient) -> None:
    """GET /api/buku without auth returns 401."""
    resp = client.get("/api/buku")
    assert resp.status_code == 401, (
        f"Expected 401, got {resp.status_code}: {resp.text}"
    )
