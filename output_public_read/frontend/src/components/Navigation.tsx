import React from 'react';
import { NavLink } from 'react-router-dom';
import { pageService } from '../services/pageService';
import { useAppContext } from '../contexts/AppContext';

const Navigation: React.FC = () => {
  const { settings } = useAppContext();
  const [pages, setPages] = React.useState<Array<{ pageFileName: string; pageName: string; pageLinkHoverText: string; mainMenu: boolean }>>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    pageService
      .getAllActivePages()
      .then((data) => {
        const menuPages = data.filter((p) => p.mainMenu).sort((a, b) => a.menuIndex - b.menuIndex);
        setPages(menuPages);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <nav className="navigation"><span>Loading navigation...</span></nav>;
  }

  return (
    <nav className="navigation" aria-label="Main navigation">
      <ul className="nav-menu">
        {pages.map((page) => (
          <li key={page.pageFileName}>
            <NavLink
              to={`/${page.pageFileName === 'default' ? '' : page.pageFileName}`}
              title={page.pageLinkHoverText || page.pageName}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {page.pageName}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navigation;
