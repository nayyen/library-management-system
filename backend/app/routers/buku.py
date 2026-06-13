"""Book catalog router — read endpoints (CAT-01, CAT-02)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.buku import Buku
from app.models.salinan_buku import SalinanBuku
from app.models.enums import StatusSalinan
from app.schemas.buku import (
    BukuCreate,
    BukuUpdate,
    BukuOut,
    BukuListItem,
    BukuListOut,
    BukuDetailOut,
    SalinanBukuCreate,
    SalinanBukuOut,
)

router = APIRouter(prefix="/api/buku", tags=["buku"])


@router.get("", response_model=BukuListOut)
def daftar_buku(
    kata_kunci: str | None = None,
    kategori: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> BukuListOut:
    """List all books with optional search and category filter.

    - kata_kunci: case-insensitive search across judul, penulis, isbn
    - kategori: multi-select OR filter (repeat param: ?kategori=A&kategori=B)
    """
    query = db.query(Buku)

    if kata_kunci:
        like = f"%{kata_kunci}%"
        query = query.filter(
            or_(
                Buku.judul.ilike(like),
                Buku.penulis.ilike(like),
                Buku.isbn.ilike(like),
            )
        )

    if kategori:
        query = query.filter(Buku.kategori.in_(kategori))

    buku_list = query.all()

    # Build list items with derived availability
    items = []
    for buku in buku_list:
        tersedia = (
            db.query(SalinanBuku)
            .filter(
                SalinanBuku.id_buku == buku.id,
                SalinanBuku.status_ketersediaan == StatusSalinan.tersedia,
            )
            .count()
            > 0
        )
        items.append(
            BukuListItem(
                id=str(buku.id),
                judul=buku.judul,
                penulis=buku.penulis,
                isbn=buku.isbn,
                kategori=buku.kategori,
                tahun_terbit=buku.tahun_terbit,
                tersedia=tersedia,
            )
        )

    return BukuListOut(items=items, total=len(items))


@router.get("/kategori", response_model=list[str])
def daftar_kategori(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> list[str]:
    """Return distinct kategori values sorted alphabetically."""
    rows = db.query(Buku.kategori).distinct().order_by(Buku.kategori).all()
    return [r[0] for r in rows]


@router.get("/{id_buku}", response_model=BukuDetailOut)
def detail_buku(
    id_buku: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> BukuDetailOut:
    """Return a single book with its full salinan_buku list."""
    buku = db.query(Buku).filter(Buku.id == id_buku).first()
    if not buku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buku tidak ditemukan.",
        )

    salinan_list = (
        db.query(SalinanBuku)
        .filter(SalinanBuku.id_buku == id_buku)
        .all()
    )

    tersedia = any(
        s.status_ketersediaan == StatusSalinan.tersedia for s in salinan_list
    )

    return BukuDetailOut(
        id=str(buku.id),
        judul=buku.judul,
        penulis=buku.penulis,
        isbn=buku.isbn,
        kategori=buku.kategori,
        tahun_terbit=buku.tahun_terbit,
        tersedia=tersedia,
        salinan=[
            SalinanBukuOut(
                id=str(s.id),
                lokasi_rak=s.lokasi_rak,
                kondisi=s.kondisi.value,
                status_ketersediaan=s.status_ketersediaan.value,
            )
            for s in salinan_list
        ],
    )
