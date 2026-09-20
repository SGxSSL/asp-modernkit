import React from 'react';
import { ProductDto } from '../types';
import { formatDate } from '../utils/helpers';

interface ProductDetailProps {
  product: ProductDto;
}

const ProductDetail: React.FC<ProductDetailProps> = ({ product }) => {
  return (
    <article className="product-detail" itemScope itemType="https://schema.org/Product">
      <h1 itemProp="name">{product.productName}</h1>
      {product.image1 && (
        <img src={product.image1} alt={product.productName} className="product-detail-image" />
      )}
      <div className="product-info">
        <p className="product-brand" itemProp="brand">{product.brand}</p>
        <p className="product-category">Category: {product.category}</p>
        <p className="product-line">{product.productLine}</p>
        <p className="product-price" itemProp="offers" itemScope itemType="https://schema.org/Offer">
          <span itemProp="price">${product.retailPrice.toFixed(2)}</span>
          <meta itemProp="priceCurrency" content="USD" />
        </p>
        {product.shortDescription && (
          <p className="product-short-description">{product.shortDescription}</p>
        )}
        {product.longDescription && (
          <div
            className="product-long-description"
            dangerouslySetInnerHTML={{ __html: product.longDescription }}
          />
        )}
        {product.options && (
          <p className="product-options">Options: {product.options}</p>
        )}
        <p className="product-date">Published: {formatDate(product.timestamp)}</p>
      </div>
    </article>
  );
};

export default ProductDetail;
