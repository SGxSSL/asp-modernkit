# Admin CRUD Slice — Granular File-by-File Task List

This task list covers the **admin_crud** slice: administrator authentication, dashboard, page CRUD, maintenance state, and audit logging — implemented as a .NET 10 Web API backend with a React + TypeScript SPA frontend.

---

## Phase 1: Solution & Project Scaffolding

### Root
- [ ] Create `AdminCrud.sln` — solution file referencing backend and test projects
- [ ] Create `.gitignore` — ignore `bin/`, `obj/`, `node_modules/`, `dist/`, `appsettings.Local.json`

### Backend Project
- [ ] Create `backend/backend.csproj` — .NET 10 Web API; packages: `Microsoft.EntityFrameworkCore.SqlServer`, `Microsoft.EntityFrameworkCore.Design`, `Microsoft.AspNetCore.Authentication.JwtBearer`, `Microsoft.AspNetCore.OpenApi`, `Swashbuckle.AspNetCore`
- [ ] Create `backend/appsettings.json` — connection string, JWT settings (issuer, audience, key, expiry), `Maintenance:IsEnabled=false`
- [ ] Create `backend/appsettings.Development.json` — relaxed HTTPS settings, detailed EF logging
- [ ] Create `backend/Program.cs` — registers DbContext, services, controllers, JWT auth, Swagger, middleware pipeline
- [ ] Create `backend/Properties/launchSettings.json` — dev profile with port `5001` (HTTPS) and `5000` (HTTP)

### Frontend Project
- [ ] Create `frontend/package.json` — React 18, TypeScript 5, Vite 5, React Router 6, Axios, React Hook Form, Zod
- [ ] Create `frontend/tsconfig.json` — strict TypeScript config with `jsx: react-jsx`, path aliases (`@/`)
- [ ] Create `frontend/tsconfig.node.json` — for Vite config file
- [ ] Create `frontend/vite.config.ts` — React plugin, dev server proxy `/api` → `https://localhost:5001`
- [ ] Create `frontend/index.html` — root HTML with `<div id="root">`
- [ ] Create `frontend/.env.development` — `VITE_API_BASE_URL=/api`

---

## Phase 2: Backend — Domain Entities

- [ ] Create `backend/Domain/Entities/UserRole.cs` — `Id`, `Name` (e.g., "Administrator"), `Level` (int)
- [ ] Create `backend/Domain/Entities/AdminUser.cs` — `Id`, `Username`, `PasswordHash`, `FullName`, `Email`, `RoleId`, `MustChangePassword`, `IsActive`, `LastLoginAt`
- [ ] Create `backend/Domain/Entities/Page.cs` — `Id`, `PageName`, `PageTitle`, `PageFileName` (URL slug), `PageLinkHoverText`, `PageDescription`, `PageKeywords`, `Style`, `MenuIndex`, `ParentPageId` (self-ref FK), `MainMenu` (bool), `Active` (bool), `CreatedAt`, `UpdatedAt`
- [ ] Create `backend/Domain/Entities/PageContent.cs` — `Id`, `PageId` (FK), `Content` (HTML string), `UpdatedAt`
- [ ] Create `backend/Domain/Entities/AuditLog.cs` — `Id`, `AdminUserId`, `Action` (e.g., "CREATE_PAGE"), `EntityType`, `EntityId`, `Details` (JSON), `IpAddress`, `CreatedAt`
- [ ] Create `backend/Domain/Enums/UserRoleLevel.cs` — enum with `Administrator = 1000`, `Editor = 500`, `Viewer = 100`

---

## Phase 3: Backend — Data Layer

- [ ] Create `backend/Data/AppDbContext.cs` — `DbSet<AdminUser>`, `DbSet<UserRole>`, `DbSet<Page>`, `DbSet<PageContent>`, `DbSet<AuditLog>`; override `SaveChangesAsync` to stamp `UpdatedAt`
- [ ] Create `backend/Data/Configurations/UserRoleConfiguration.cs` — unique index on `Name`, seed roles
- [ ] Create `backend/Data/Configurations/AdminUserConfiguration.cs` — unique index on `Username`, max length constraints
- [ ] Create `backend/Data/Configurations/PageConfiguration.cs` — self-referencing FK, cascade delete behavior, indexes on `ParentPageId`, `Active`, `MenuIndex`
- [ ] Create `backend/Data/Configurations/PageContentConfiguration.cs` — one-to-one with `Page`, max length for `Content` (nvarchar max)
- [ ] Create `backend/Data/Configurations/AuditLogConfiguration.cs` — indexes on `AdminUserId`, `CreatedAt`, `EntityType`
- [ ] Create `backend/Data/SeedData/SeedData.cs` — seeds roles, default admin user (`admin` / `ChangeMe!123` with hashed password, `MustChangePassword=true`), sample home page

---

## Phase 4: Backend — Contracts / DTOs

### Auth
- [ ] Create `backend/Contracts/DTOs/Auth/LoginRequest.cs` — `Username`, `Password`
- [ ] Create `backend/Contracts/DTOs/Auth/LoginResponse.cs` — `Token`, `ExpiresAt`, `MustChangePassword`, `User`
- [ ] Create `backend/Contracts/DTOs/Auth/CurrentUserDto.cs` — `Id`, `Username`, `FullName`, `Role`, `RoleLevel`

### Pages
- [ ] Create `backend/Contracts/DTOs/Pages/PageSummaryDto.cs` — `Id`, `PageName`, `PageTitle`, `PageFileName`, `Active`, `MainMenu`, `MenuIndex`, `ParentPageId`, `UpdatedAt`
- [ ] Create `backend/Contracts/DTOs/Pages/PageDetailDto.cs` — summary fields + `PageContent`, `PageKeywords`, `PageDescription`, `PageLinkHoverText`, `Style`
- [ ] Create `backend/Contracts/DTOs/Pages/PageTreeNodeDto.cs` — `Id`, `PageName`, `Children` (recursive)
- [ ] Create `backend/Contracts/DTOs/Pages/CreatePageRequest.cs` — form fields + validation attributes
- [ ] Create `backend/Contracts/DTOs/Pages/UpdatePageRequest.cs` — same as create + `Id`
- [ ] Create `backend/Contracts/DTOs/Pages/PageContentDto.cs` — `PageId`, `Content` (HTML)

### Dashboard
- [ ] Create `backend/Contracts/DTOs/Dashboard/DashboardStatsDto.cs` — `TotalPages`, `ActivePages`, `InactivePages`, `TotalUsers`, `RecentPages` (list of `PageSummaryDto`), `LastAuditEntries`

### Maintenance
- [ ] Create `backend/Contracts/DTOs/Maintenance/MaintenanceStatusDto.cs` — `IsEnabled`, `Message`
- [ ] Create `backend/Contracts/DTOs/Maintenance/UpdateMaintenanceRequest.cs` — `IsEnabled`, `Message`

---

## Phase 5: Backend — Services

### Auth
- [ ] Create `backend/Services/IAuthService.cs` — `LoginAsync`, `LogoutAsync`, `GetCurrentUserAsync`
- [ ] Create `backend/Services/AuthService.cs` — validates credentials, checks `MustChangePassword`, updates `LastLoginAt`, returns JWT

### Pages
- [ ] Create `backend/Services/IPageService.cs` — `GetAllAsync`, `GetByIdAsync`, `GetTreeAsync`, `CreateAsync`, `UpdateAsync`, `DeleteAsync`, `GetContentAsync`, `UpdateContentAsync`
- [ ] Create `backend/Services/PageService.cs` — CRUD with slug generation from `PageName`, parent validation, menu index reordering, audit logging, content upsert

### Dashboard
- [ ] Create `backend/Services/IDashboardService.cs` — `GetStatsAsync`
- [ ] Create `backend/Services/DashboardService.cs` — aggregates page counts, recent pages, recent audit entries

### Maintenance
- [ ] Create `backend/Services/IMaintenanceService.cs` — `GetStatusAsync`, `SetStatusAsync`
- [ ] Create `backend/Services/MaintenanceService.cs` — reads/writes maintenance flag (DB-backed)

### Audit
- [ ] Create `backend/Services/IAuditService.cs` — `LogAsync`, `GetRecentAsync`
- [ ] Create `backend/Services/AuditService.cs` — writes audit entries with current user, IP, entity info

---

## Phase 6: Backend — Infrastructure

- [ ] Create `backend/Infrastructure/Auth/JwtSettings.cs` — strongly-typed config class (`Issuer`, `Audience`, `Key`, `ExpiryMinutes`)
- [ ] Create `backend/Infrastructure/Auth/JwtTokenGenerator.cs` — generates JWT with claims (sub, name, role, level)
- [ ] Create `backend/Infrastructure/Auth/PasswordHasher.cs` — Argon2id hashing wrapper (or `PasswordHasher<T>` from `Microsoft.AspNetCore.Identity`)
- [ ] Create `backend/Infrastructure/Middleware/ExceptionHandlingMiddleware.cs` — global try/catch, maps exceptions to `ProblemDetails`
- [ ] Create `backend/Infrastructure/Middleware/JwtMiddleware.cs` — validates JWT from `Authorization` header or `httpOnly` cookie
- [ ] Create `backend/Infrastructure/Persistence/DbInitializer.cs` — applies migrations, calls `SeedData`

---

## Phase 7: Backend — Controllers

- [ ] Create `backend/Controllers/AuthController.cs` — `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- [ ] Create `backend/Controllers/PagesController.cs` — `GET /api/pages`, `GET /api/pages/tree`, `GET /api/pages/{id}`, `POST /api/pages`, `PUT /api/pages/{id}`, `DELETE /api/pages/{id}`, `GET /api/pages/{id}/content`, `PUT /api/pages/{id}/content`
- [ ] Create `backend/Controllers/DashboardController.cs` — `GET /api/dashboard/stats`
- [ ] Create `backend/Controllers/MaintenanceController.cs` — `GET /api/maintenance`, `PUT /api/maintenance`
- [ ] Create `backend/Controllers/AuditLogsController.cs` — `GET /api/auditlogs?limit=50`

---

## Phase 8: Frontend — Scaffolding & API Client

### Core
- [ ] Create `frontend/src/main.tsx` — React root, BrowserRouter, AuthProvider
- [ ] Create `frontend/src/App.tsx` — route definitions, lazy loading
- [ ] Create `frontend/src/vite-en.d.ts` — Vite type references
- [ ] Create `frontend/src/styles/globals.css` — CSS reset, design tokens (CSS variables), base layout styles

### Types
- [ ] Create `frontend/src/types/auth.ts` — `LoginRequest`, `LoginResponse`, `CurrentUser`
- [ ] Create `frontend/src/types/page.ts` — `PageSummary`, `PageDetail`, `PageTreeNode`, `CreatePageRequest`, `UpdatePageRequest`
- [ ] Create `frontend/src/types/dashboard.ts` — `DashboardStats`
- [ ] Create `frontend/src/types/maintenance.ts` — `MaintenanceStatus`, `UpdateMaintenanceRequest`

### API Client
- [ ] Create `frontend/src/api/client.ts` — Axios instance with base URL, `withCredentials: true`, response interceptor for 401 → redirect to `/login`
- [ ] Create `frontend/src/api/auth.ts` — `login()`, `logout()`, `getCurrentUser()`
- [ ] Create `frontend/src/api/pages.ts` — `getPages()`, `getPage(id)`, `createPage()`, `updatePage()`, `deletePage()`, `getPageTree()`, `getPageContent(id)`, `updatePageContent(id, content)`
- [ ] Create `frontend/src/api/dashboard.ts` — `getDashboardStats()`
- [ ] Create `frontend/src/api/maintenance.ts` — `getMaintenanceStatus()`, `updateMaintenanceStatus()`

---

## Phase 9: Frontend — Auth & Routing

- [ ] Create `frontend/src/context/AuthContext.tsx` — context provider holding `user`, `loading`, `login()`, `logout()`; on mount calls `getCurrentUser()`
- [ ] Create `frontend/src/router/index.tsx` — route table with:
  - `/login` → `LoginPage` (public)
  - `/` → `AdminLayout` (protected)
    - `/` → `DashboardPage`
    - `/pages` → `PageListPage`
    - `/pages/new` → `PageCreatePage`
    - `/pages/:id/edit` → `PageEditPage`
    - `/maintenance` → `MaintenancePage`
  - `/unavailable` → `UnavailablePage` (public, shown when maintenance mode is on)
  - `*` → `NotFoundPage`
- [ ] Create `frontend/src/components/ProtectedRoute.tsx` — checks `user` from `AuthContext`, redirects to `/login` if unauthenticated

---

## Phase 10: Frontend — UI Components

### Primitives
- [ ] Create `frontend/src/components/ui/Button.tsx` — variants (primary, secondary, danger), loading state
- [ ] Create `frontend/src/components/ui/Input.tsx` — labeled text input with error display
- [ ] Create `frontend/src/components/ui/TextArea.tsx` — labeled textarea
- [ ] Create `frontend/src/components/ui/Checkbox.tsx` — labeled checkbox
- [ ] Create `frontend/src/components/ui/Select.tsx` — labeled select with options
- [ ] Create `frontend/src/components/ui/Alert.tsx` — success/error/info alert banners
- [ ] Create `frontend/src/components/ui/Modal.tsx` — accessible modal dialog for delete confirmation

### Layout
- [ ] Create `frontend/src/components/layout/AdminLayout.tsx` — grid layout with header, sidebar, main content area
- [ ] Create `frontend/src/components/layout/Header.tsx` — app title, user dropdown (profile, logout)
- [ ] Create `frontend/src/components/layout/Sidebar.tsx` — nav links: Dashboard, Pages, Maintenance; highlights active route

### Page-Specific
- [ ] Create `frontend/src/components/pages/PageForm.tsx` — form with fields: PageName, PageTitle, PageFileName, PageLinkHoverText, PageDescription, PageKeywords, Style, ParentPage (tree select), MenuIndex, MainMenu, Active; validation via Zod
- [ ] Create `frontend/src/components/pages/PageTree.tsx` — recursive tree component for parent selection and menu ordering
- [ ] Create `frontend/src/components/pages/PageContentEditor.tsx` — textarea with HTML content, preview toggle, save button

---

## Phase 11: Frontend — Pages/Views

- [ ] Create `frontend/src/pages/LoginPage.tsx` — username/password form, error display, redirects to `/` on success; shows "change password" prompt if `MustChangePassword`
- [ ] Create `frontend/src/pages/DashboardPage.tsx` — renders `DashboardStats`: page counts, recent pages table, recent audit entries
- [ ] Create `frontend/src/pages/PageListPage.tsx` — table of pages with columns (Name, FileName, Active, Menu, Updated), actions (Edit, Delete), "New Page" button
- [ ] Create `frontend/src/pages/PageCreatePage.tsx` — renders `PageForm`; on submit calls `createPage()`, navigates to edit page
- [ ] Create `frontend/src/pages/PageEditPage.tsx` — loads page by ID, renders `PageForm` + `PageContentEditor`; handles save, delete, content update
- [ ] Create `frontend/src/pages/MaintenancePage.tsx` — toggle for maintenance mode, message editor, save button
- [ ] Create `frontend/src/pages/UnavailablePage.tsx` — simple "Site is under maintenance" page with configured message
- [ ] Create `frontend/src/pages/NotFoundPage.tsx` — 404 page with link back to dashboard

---

## Phase 12: Database Migration & Seeding

- [ ] Create `backend/Data/Migrations/InitialCreate.cs` — generated via `dotnet ef migrations add InitialCreate`
- [ ] Apply migration to local database — `dotnet ef database update`
- [ ] Seed data: roles (Administrator, Editor), admin user with Argon2id-hashed password, sample home page with content
- [ ] Verify seed admin user has `MustChangePassword = true`

---

## Phase 13: Security Hardening

- [ ] Implement password hashing — Argon2id via `PasswordHasher` (never store plaintext)
- [ ] Force password change — backend rejects non-password endpoints when `MustChangePassword=true`; frontend shows change-password form
- [ ] JWT in httpOnly cookie — set `HttpOnly`, `Secure`, `SameSite=Strict` cookie on login; CSRF token for state-changing requests
- [ ] Authorization policies — `[Authorize(Policy = "AdminOnly")]` on page create/update/delete; `[Authorize]` on read endpoints
- [ ] Input validation — DataAnnotations on DTOs + FluentValidation for complex rules (e.g., unique PageName)
- [ ] SQL injection prevention — all queries via EF Core LINQ (no raw SQL string concatenation)
- [ ] XSS prevention — React escapes output by default; `PageContentEditor` preview uses `dangerouslySetInnerHTML` only after sanitization with DOMPurify
- [ ] Rate limiting — `Microsoft.AspNetCore.RateLimiting` on `/api/auth/login` (e.g., 5 attempts / 15 min)
- [ ] Audit logging on all mutations — log admin user, action, entity, IP, timestamp

---

## Phase 14: Testing

### Backend Unit Tests
- [ ] Create `backend.Tests/backend.Tests.csproj` — xUnit, Moq, FluentAssertions
- [ ] Create `backend.Tests/Services/AuthServiceTests.cs` — login success/failure, password hashing, `MustChangePassword` flow
- [ ] Create `backend.Tests/Services/PageServiceTests.cs` — CRUD, slug generation, parent validation, menu index reordering
- [ ] Create `backend.Tests/Services/MaintenanceServiceTests.cs` — status get/set
- [ ] Create `backend.Tests/Controllers/PagesControllerTests.cs` — HTTP status codes, authorization

### Frontend Tests
- [ ] Create `frontend/src/__tests__/LoginPage.test.tsx` — renders, submits, shows error
- [ ] Create `frontend/src/__tests__/PageForm.test.tsx` — validation, submit payload
- [ ] Create `frontend/src/__tests__/PageListPage.test.tsx` — renders pages, delete confirmation

---

## Phase 15: Integration & Verification

- [ ] Create `frontend/src/api/mockHandlers.ts` — MSW handlers for API mocking (if used in tests)
- [ ] Manual smoke test: login → change password → create page → edit page → add content → delete page
- [ ] Verify maintenance mode: enable → confirm `/unavailable` shows → disable
- [ ] Verify audit log entries appear on dashboard after CRUD operations
- [ ] Run `dotnet build` and `npm run build` — confirm zero errors
- [ ] Update `README.md` — setup instructions, default credentials, architecture overview

---

## Out of Scope (per slice definition)
- User CRUD (admin user management)
- Settings CRUD
- Product/testimonial/form-field administration
- Module administration
- Public site rendering
- File-manager / physical file creation
- Migration of legacy sessions or encrypted cookies