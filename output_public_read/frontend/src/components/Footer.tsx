import React from 'react';
import { useAppContext } from '../contexts/AppContext';

const Footer: React.FC = () => {
  const { settings } = useAppContext();
  const companyName = settings['Company Name'] || 'CMS';
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <p className="copyright">
          &copy; {year} {companyName}. All rights reserved.
        </p>
        <p className="footer-powered">
          Powered by Public Read CMS
        </p>
      </div>
    </footer>
  );
};

export default Footer;
