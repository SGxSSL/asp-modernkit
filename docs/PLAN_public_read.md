

Here is the granular, file-by-file Task List for the `public_read` slice:

### Backend (.NET 10) Tasks

- [ ] **Data Access Layer**
  - [ ] Create `Data/AppDbContext.cs` - Entity Framework Core database context
  - [ ] Create `Data/Entities/PageEntity.cs` - Entity mapping for `tblPages` and `tblPageContent`
  - [ ] Create `Data/Entities/ProductEntity.cs` - Entity mapping for `tblProducts`
  - [ ] Create `Data/Entities/TestimonialEntity.cs` - Entity mapping for `tblTestimonials`
  - [ ] Create `Data/Entities/GlobalSettingEntity.cs` - Entity mapping for `tblGlobalSettings`
  - [ ] Create `Data/Entities/ModuleEntity.cs` - Entity mapping for `tblModules` and `tblModuleTypes`
  - [ ] Create `Data/Repositories/IPageRepository.cs` - Repository interface for page data access
  - [ ] Create `Data/Repositories/PageRepository.cs` - Repository implementation for page data access
  - [ ] Create `Data/Repositories/IProductRepository.cs` - Repository interface for product data access
  - [ ] Create `Data/Repositories/ProductRepository.cs` - Repository implementation for product data access
  - [ ] Create `Data/Repositories(ITestimonialRepository.cs` - Repository interface for testimonial data access
  - [ ] Create `Data/Repositories/TestimonialRepository.cs` - Repository implementation for testimonial data access
  - [ ] Create `Data/Repositories/IGlobalSettingRepository.cs` - Repository interface for global settings data access
  - [ ] Create `Data/Repositories/GlobalSettingRepository.cs` - Repository implementation for global settings data access
  - [ ] Create `Data/Repositories/IModuleRepository.cs` - Repository interface for module data access
  - [ ] Create `Data/Repositories/ModuleRepository.cs` - Repository implementation for module data access

- [ ] **DTOs (Data Transfer Objects)**
  - [ ] Create `Models/DTOs/PageDto.cs` - DTO for page data API responses
  - [ ] Create `Models/DTOs/ProductDto.cs` - DTO for product data API responses
  - [ ] Create `Models/DTOs/TestimonialDto.cs` - DTO for testimonial data API responses
  - [ ] Create `Models/DTOs/GlobalSettingDto.cs` - DTO for global settings API responses
  - [ ] Create `Models/DTOs/ModuleDto.cs` - DTO for module data API responses

- [ ] **API Controllers**
  - [ ] Create `Controllers/PagesController.cs` - Controller for page-related endpoints (`/api/public/pages`)
  - [ ] Create `Controllers/ProductsController.cs` - Controller for product-related endpoints (`/api/public/products`)
  - [ ] Create `Controllers/TestimonialsController.cs` - Controller for testimonial-related endpoints (`/api/public/testimonials`)
  - [ ] Create `Controllers/SettingsController.cs` - Controller for settings-related endpoints (`/api/public/settings`)
  - [ ] Create `Controllers/ModulesController.cs` - Controller for module-related endpoints (`/api/public/modules`)

- [ ] **Configuration & Startup**
  - [ ] Modify `Program.cs` - Configure Entity Framework Core, database context, repositories, CORS, and API routing
  - [ ] Create `appsettings.json` - Add database connection strings and application settings

### Frontend (React TS) Tasks

- [ ] **Project Setup**
  - [ ] Initialize React TypeScript project
  - [ ] Install dependencies (React Router, Axios, etc.)
  - [ ] Configure TypeScript paths and settings

- [ ] **API Service Layer**
  - [ ] Create `services/api.ts` - Configure Axios instance with base URL
  - [ ] Create `services/pageService.ts` - Functions to call page-related API endpoints
  - [ ] Create `services/productService.ts` - Functions to call product-related API endpoints
  - [ ] Create `services/testimonialService.ts` - Functions to call testimonial-related API endpoints
  - [ ] Create `services/settingsService.ts` - Functions to call settings-related API endpoints
  - [ ] Create `services/moduleService.ts` - Functions to call module-related API endpoints

- [ ] **React Components**
  - [ ] Create `components/PageRenderer.tsx` - Component to render page content safely
  - [ ] Create `components/ProductList.tsx` - Component to display list of products
  - [ ] Create `components/ProductDetail.tsx` - Component to display individual product details
  - [ ] Create `components/TestimonialList.tsx` - Component to display list of testimonials
  - [ ] Create `components/Navigation.tsx` - Component for main navigation menu
  - [ ] Create `components/Footer.tsx` - Component for site footer
  - [ ] Create `components/Header.tsx` - Component for site header
  - [ ] Create `components/ModuleRenderer.tsx` - Component to render modules dynamically

- [ ] **Pages**
  - [ ] Create `pages/HomePage.tsx` - Homepage component
  - [ ] Create `pages/AboutPage.tsx` - About page component
  - [ ] Create `pages/ContactPage.tsx` - Contact page component
  - [ ] Create `pages/ProductsPage.tsx` - Products listing page
  - [ ] Create `pages/ProductDetailPage.tsx` - Individual product detail page
  - [ ] Create `pages/TestimonialsPage.tsx` - Testimonials page
  - [ ] Create `pages/NotFound.tsx` - 404 error page component

- [ ] **Routing & State Management**
  - [ ] Create `App.tsx` - Main app component with routing configuration
  - [ ] Create `contexts/AppContext.tsx` - React context for global state (settings, etc.)
  - [ ] Create `hooks/useApi.ts` - Custom hook for API calls with loading/error states

- [ ] **Content Sanitization & Security**
  - [ ] Create `utils/sanitizer.ts` - HTML sanitization utility for safe content rendering
  - [ ] Create `utils/helpers.ts` - Helper functions for data formatting and manipulation

- [ ] **Static Assets & Styling**
  - [ ] Set up CSS/SASS compilation
  - [ ] Create `assets/` directory for images and static files
  - [ ] Create `styles/` directory for global stylesheets
  - [ ] Configure asset paths for CDN deployment

### Integration & Testing Tasks

- [ ] **API Integration**
  - [ ] Set up database migration for Entity Framework Core
  - [ ] Implement error handling and validation in API controllers
  - [ ] Add Swagger/OpenAPI documentation to the .NET API
  - [ ] Implement response caching for read-only endpoints

- [ ] **Frontend Integration**
  - [ ] Implement route-based code splitting
  - [ ] Add error boundaries for API failures
  - [ ] Implement loading states for async operations
  - [ ] Add SEO-friendly meta tags and semantic HTML

- [ ] **Deployment Configuration**
  - [ ] Configure API CORS for frontend domain
  - [ ] Set up static file serving for React build
  - [ ] Configure environment variables for different deployments
  - [ ] Create Docker container configuration (if needed)

This task list provides a comprehensive roadmap for implementing the `public_read` slice, covering all necessary backend API development, frontend component creation, and integration points required to modernize the Classic ASP application.