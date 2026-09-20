import React from 'react';
import { TestimonialDto } from '../types';
import { formatDate } from '../utils/helpers';

interface TestimonialListProps {
  testimonials: TestimonialDto[];
}

const TestimonialList: React.FC<TestimonialListProps> = ({ testimonials }) => {
  return (
    <section className="testimonial-list" aria-label="Testimonials">
      <h2>Testimonials</h2>
      <div className="testimonials-grid">
        {testimonials.map((testimonial) => (
          <blockquote key={testimonial.id} className="testimonial-card">
            <p className="testimonial-comments">{testimonial.comments}</p>
            <footer className="testimonial-author">
              <cite>{testimonial.name}</cite>
              {testimonial.location && (
                <span className="testimonial-location">{testimonial.location}</span>
              )}
              {testimonial.showEmail && testimonial.email && (
                <a href={`mailto:${testimonial.email}`} className="testimonial-email">
                  {testimonial.email}
                </a>
              )}
              <time dateTime={testimonial.testimonialDate}>
                {formatDate(testimonial.testimonialDate)}
              </time>
            </footer>
          </blockquote>
        ))}
      </div>
    </section>
  );
};

export default TestimonialList;
