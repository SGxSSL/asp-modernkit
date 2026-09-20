import React from 'react';
import { pageService } from '../services/pageService';
import { useApi } from '../hooks/useApi';
import PageRenderer from '../components/PageRenderer';
import ModuleRenderer from '../components/ModuleRenderer';
import { moduleService } from '../services/moduleService';

const HomePage: React.FC = () => {
  const { data: page, loading, error } = useApi(
    () => pageService.getPageByFileName('default'),
    []
  );
  const { data: modules } = useApi(
    () => moduleService.getAllActiveModules(),
    []
  );

  if (loading) return <div className="loading">Loading homepage...</div>;
  if (error) return <div className="error">Error loading homepage: {error}</div>;
  if (!page) return <div className="not-found">Homepage not found.</div>;

  return (
    <main className="home-page">
      <ModuleRenderer modules={modules || []} location="header" />
      <PageRenderer page={page} />
      <ModuleRenderer modules={modules || []} location="main" />
      <ModuleRenderer modules={modules || []} location="footer" />
    </main>
  );
};

export default HomePage;
