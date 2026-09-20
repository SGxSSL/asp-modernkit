import React from 'react';
import { pageService } from '../services/pageService';
import { useApi } from '../hooks/useApi';
import PageRenderer from '../components/PageRenderer';

const ContactPage: React.FC = () => {
  const { data: page, loading, error } = useApi(
    () => pageService.getPageByFileName('contact'),
    []
  );

  if (loading) return <div className="loading">Loading contact page...</div>;
  if (error) return <div className="error">Error loading page: {error}</div>;
  if (!page) return <div className="not-found">Contact page not found.</div>;

  return (
    <main className="contact-page">
      <PageRenderer page={page} />
    </main>
  );
};

export default ContactPage;
