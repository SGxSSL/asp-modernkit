import React from 'react';
import { productService } from '../services/productService';
import { useApi } from '../hooks/useApi';
import ProductList from '../components/ProductList';

const ProductsPage: React.FC = () => {
  const { data: products, loading, error } = useApi(
    () => productService.getAllActiveProducts(),
    []
  );

  if (loading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">Error loading products: {error}</div>;
  if (!products) return <div className="no-products">No products available.</div>;

  return (
    <main className="products-page">
      <h1>Products</h1>
      <ProductList products={products} />
    </main>
  );
};

export default ProductsPage;
