import apiClient from './api';
import { TestimonialDto } from '../types';

export const testimonialService = {
  getAllActiveTestimonials: (): Promise<TestimonialDto[]> =>
    apiClient.get('/testimonials').then((res) => res.data),
};
