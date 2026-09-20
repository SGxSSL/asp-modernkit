import React from 'react';
import { testimonialService } from '../services/testimonialService';
import { useApi } from '../hooks/useApi';
import TestimonialList from '../components/TestimonialList';

const TestimonialsPage: React.FC = () => {
  const { data: testimonials, loading, error } = useApi(
    () => testimonialService.getAllActiveTestimonials(),
    []
  );

  if (loading) return <div className="loading">Loading testimonials...</div>;
  if (error) return <div className="error">Error loading testimonials: {error}</div>;
  if (!testimonials) return <div className="no-testimonials">No testimonials available.</div>;

  return (
    <main className="testimonials-page">
      <h1>Testimonials</h1>
      <TestimonialList testimonials={testimonials} />
    </main>
  );
};

export default TestimonialsPage;
