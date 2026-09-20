import apiClient from './api';
import { ProductDto } from '../types';

export const productService = {
  getAllActiveProducts: (): Promise<ProductDto[]> =>
    apiClient.get('/products').then((res) => res.data),

  getProductById: (id: number): Promise<ProductDto> =>
    apiClient.get(`/products/${id}`).then((res) => res.data),
};
