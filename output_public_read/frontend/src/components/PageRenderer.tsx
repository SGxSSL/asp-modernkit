import React from 'react';
import { PageDto } from '../types';
import { sanitizeHtml } from '../utils/sanitizer';

interface PageRendererProps {
  page: PageDto;
}

const PageRenderer: React.FC<PageRendererProps> = ({ page }) => {
  return (
    <article className="page-content" itemScope itemType="https://schema.org/WebPage">
      <h1 itemProp="headline">{page.pageTitle || page.pageName}</h1>
      {page.pageDescription && (
        <meta itemProp="description" content={page.pageDescription} />
      )}
      <div
        className="page-body"
        dangerouslySetInnerHTML={{ __html: sanitizeHtml(page.content || '') }}
        itemProp="text"
      />
    </article>
  );
};

export default PageRenderer;
