import React from 'react';
import { Link } from 'react-router-dom';
import { ProductDto } from '../types';
import { formatRelativeDate } from '../utils/helpers';

interface ProductListProps {
  products: ProductDto[];
}

const ProductList: React.FC<ProductListProps> = ({ products }) => {
  return (
    <section className="product-list" aria-label="Products">
      <h2>Products</h2>
      <div className="products-grid">
        {products.map((product) => (
          <article key={product.key} className="product-card">
            <Link to={`/products/${product.key}`}>
              {product.image1 && (
                <img src={product.image1} alt={product.productName} className="product-image" />
              )}
              <h3>{product.productName}</h3>
              <p className="product-brand">{product.brand}</p>
              <p className="product-category">{product.category}</p>
              <p className="product-price">${product.retailPrice.toFixed(2)}</p>
              {product.recommended && <span className="badge recommended">Recommended</span>}
              <p className="product-date">{formatRelativeDate(product.timestamp)}</p>
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
};

export default ProductList;
