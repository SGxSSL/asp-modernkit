import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { productService } from '../services/productService';
import { useApi } from '../hooks/useApi';
import ProductDetail from '../components/ProductDetail';

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const productId = parseInt(id || '0', 10);
  const { data: product, loading, error } = useApi(
    () => productService.getProductById(productId),
    [productId]
  );

  if (loading) return <div className="loading">Loading product details...</div>;
  if (error) return <div className="error">Error loading product: {error}</div>;
  if (!product) return <div className="not-found">Product not found.</div>;

  return (
    <main className="product-detail-page">
      <Link to="/products" className="back-link">&larr; Back to Products</Link>
      <ProductDetail product={product} />
    </main>
  );
};

export default ProductDetailPage;
