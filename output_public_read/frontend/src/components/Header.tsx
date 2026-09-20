import React from 'react';
import { useAppContext } from '../contexts/AppContext';
import Navigation from './Navigation';

const Header: React.FC = () => {
  const { settings } = useAppContext();
  const siteTitle = settings['Site Title'] || 'Public Read CMS';
  const logo = settings['Site Logo'] || '';

  return (
    <header className="site-header">
      <div className="header-inner">
        {logo && (
          <img src={logo} alt={`${siteTitle} logo`} className="site-logo" />
        )}
        <h1 className="site-title">{siteTitle}</h1>
        <Navigation />
      </div>
    </header>
  );
};

export default Header;
