import React from 'react';
import { pageService } from '../services/pageService';
import { useApi } from '../hooks/useApi';
import PageRenderer from '../components/PageRenderer';

const AboutPage: React.FC = () => {
  const { data: page, loading, error } = useApi(
    () => pageService.getPageByFileName('about'),
    []
  );

  if (loading) return <div className="loading">Loading about page...</div>;
  if (error) return <div className="error">Error loading page: {error}</div>;
  if (!page) return <div className="not-found">About page not found.</div>;

  return (
    <main className="about-page">
      <PageRenderer page={page} />
    </main>
  );
};

export default AboutPage;
