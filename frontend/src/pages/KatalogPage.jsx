import { useState, useEffect, useCallback } from 'react';
import api from '../lib/api';
import SearchBar from '../components/SearchBar';
import CategoryFilterSidebar from '../components/CategoryFilterSidebar';
import BookCard from '../components/BookCard';
import EmptyState from '../components/EmptyState';

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
      {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
        <div key={i} className="animate-pulse">
          <div className="aspect-[3/4] bg-surface-container rounded-xl" />
          <div className="mt-3 space-y-2">
            <div className="h-4 bg-surface-container rounded w-3/4" />
            <div className="h-3 bg-surface-container rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function KatalogPage() {
  const [books, setBooks] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [kataKunci, setKataKunci] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);

  const fetchBooks = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (kataKunci) params.kata_kunci = kataKunci;
      if (selectedCategories.length > 0) {
        params.kategori = selectedCategories;
      }
      const res = await api.get('/buku', { params });
      setBooks(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError('Gagal memuat daftar buku. Silakan coba lagi.');
      setBooks([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [kataKunci, selectedCategories]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-headline-md font-headline-md text-primary">
          Katalog Buku
        </h1>
        <p className="text-body-md font-body-md text-outline mt-1">
          Telusuri koleksi buku perpustakaan.
        </p>
      </div>

      {/* Search bar */}
      <SearchBar value={kataKunci} onChange={setKataKunci} />

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filter sidebar */}
        <CategoryFilterSidebar
          selected={selectedCategories}
          onChange={setSelectedCategories}
        />

        {/* Book grid */}
        <div className="flex-1 min-w-0">
          {loading ? (
            <SkeletonGrid />
          ) : error ? (
            <EmptyState
              icon="error"
              title="Terjadi Kesalahan"
              message={error}
              actionLabel="Coba Lagi"
              onAction={fetchBooks}
            />
          ) : books.length === 0 ? (
            <EmptyState
              icon="search_off"
              title="Buku Tidak Ditemukan"
              message={
                kataKunci || selectedCategories.length > 0
                  ? 'Tidak ada buku yang sesuai dengan filter yang dipilih. Coba gunakan kata kunci lain atau hapus filter.'
                  : 'Belum ada buku dalam katalog.'
              }
              actionLabel={
                kataKunci || selectedCategories.length > 0
                  ? 'Hapus Semua Filter'
                  : undefined
              }
              onAction={() => {
                setKataKunci('');
                setSelectedCategories([]);
              }}
            />
          ) : (
            <>
              <p className="text-body-sm font-body-sm text-outline mb-4">
                Menampilkan {books.length} dari {total} buku
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
                {books.map((buku) => (
                  <BookCard key={buku.id} buku={buku} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
