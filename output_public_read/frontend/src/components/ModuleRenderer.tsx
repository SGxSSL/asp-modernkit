import React from 'react';
import { ModuleDto } from '../types';

interface ModuleRendererProps {
  modules: ModuleDto[];
  location: string;
}

const ModuleRenderer: React.FC<ModuleRendererProps> = ({ modules, location }) => {
  const locationModules = modules
    .filter((m) => m.location === location && m.active && !m.disabled)
    .sort((a, b) => a.sortOrder - b.sortOrder);

  if (locationModules.length === 0) return null;

  return (
    <div className="module-container" data-location={location}>
      {locationModules.map((module) => (
        <div
          key={module.id}
          className={`module module-${module.id}`}
          style={{
            id: module.styleId || undefined,
            className: module.styleClass || undefined,
            style: module.styleInline ? { cssText: module.styleInline } : undefined,
          }}
        >
          <div className="module-wrapper">
            <h3>{module.name}</h3>
            {module.description && <p>{module.description}</p>}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ModuleRenderer;
