# Architectural Specification — `admin_crud`

## 1. Slice Scope

### Legacy-to-new mapping

| Legacy endpoint | New responsibility |
|---|---|
| `public/admin/login.asp` | Authenticate administrator and establish server-side session |
| `public/admin/admin_home.asp` | Admin dashboard/read model |
| `public/admin/unavailable.asp` | Maintenance/offline status and React route |
| `public/admin/pages/pages.asp` | Page collection/list |
| `public/admin/pages/pages_add.asp` | Create page and initial content |
| `public/admin/pages/pages_edit.asp` | Load and submit page edit form |
| `public/admin/pages/pages_view.asp` | Read page list/detail and delete page |

### In scope

- Administrator authentication.
- Admin dashboard.
- Site availability/maintenance state.
- Page listing, creation, retrieval, update, and deletion.
- Page metadata, hierarchy, publication state, and page content.
- Audit logging for administrative changes.
- React TypeScript administrative UI.

### Explicitly out of scope

- User CRUD.
- Settings CRUD.
- Product, testimonial, and form-field administration.
- Module administration.
- Public page rendering implementation.
- File-manager functionality.
- Migration of legacy sessions or encrypted login cookies.

---

## 2. Domain Model

### 2.1 Core aggregates

### `UserRole`

Mapped from `tblUserRoles`.

| Property | Type | Notes |
|---|---:|---|
| `Id` | `int` | Database identity |
| `Name` | `string` | `Guest`, `Registered`, `Editor`, `Manager`, `Administrator` |
| `Description` | `string?` | |
| `Level` | `int` | Legacy levels: 0, 20, 30, 50, 100 |

Rules:

- `Name` and `Level` are unique.
- Authorization uses the role ID or canonical role name, not an unvalidated integer supplied by the client.
- The new implementation should use `USER_ADMINISTRATOR = 100`; legacy code contains an inconsistent administrator check based on `>= 50`.

---

### `AdminUser`

Mapped from `tblUsers`.

| Property | Legacy field | New representation |
|---|---|---|
| `Id` | `id` | Internal identity |
| `ExternalUserId` | `UserID` | Unique login identifier |
| `PasswordHash` | `Password` | Never copy plaintext; store Argon2id/bcrypt hash |
| `LastLoginAt` | `LastLogin` | Nullable UTC timestamp |
| `IsDisabled` | `Disabled` | Boolean |
| `Description` | `Description` | |
| `FirstName` | `FirstName` | |
| `SecondName` | `SecondName` | |
| `Email` | `Email` | |
| `Phone` | `Phone` | |
| `Address1` | `Address1` | |
| `Address2` | `Address2` | |
| `City` | `City` | |
| `State` | `State` | |
| `PostalCode` | `PostalCode` | |
| `Country` | `Country` | |
| `RoleId` | `Role` | FK to `UserRole` |

Important security finding:

- The legacy application compares submitted passwords directly with `tblUsers.Password`.
- Those values are plaintext.
- They must not be migrated into the new password-hash column.
- Affected users should be required to reset credentials after migration.

---

### `Page`

Mapped from `tblPages`.

| Property | Legacy field | Notes |
|---|---|---|
| `Id` | `PageID` | Identity |
| `Name` | `PageName` | Human-readable page name |
| `Title` | `PageTitle` | Browser/search title |
| `FilePath` | `PageFileName` | Canonical virtual path, for example `/services/contact` |
| `HoverText` | `PageLinkHoverText` | |
| `Description` | `PageDescription` | Metadata |
| `Keywords` | `PageKeywords` | Metadata |
| `IsActive` | `Active` | Public visibility |
| `IsInMainMenu` | `MainMenu` | Main-navigation visibility |
| `MenuIndex` | `MenuIndex` | Ordering; nullable if unspecified |
| `ParentPageId` | `ParentPage` | Optional self-reference |
| `Style` | `Style` | Should be restricted to an allowlist |
| `CreatedAt` | `CreateDate` | UTC |
| `UpdatedAt` | derived | Normally latest content revision time |
| `Version` | new | Optimistic-concurrency token |

Relationships:

```text
Page 1 ── * PageContent
Page 0..1 ── * child Page
```

Invariants:

- `FilePath` is unique and normalized.
- Path values cannot contain `..`, drive prefixes, or absolute filesystem paths.
- `ParentPageId` cannot reference the same page.
- Parent relationships cannot form cycles.
- `MenuIndex` must be non-negative when used.
- Inactive pages must not be included in public navigation.
- `Style` must belong to the configured stylesheet allowlist.
- Page creation and initial content creation must commit atomically.
- Page deletion must remove page metadata and content atomically.

---

### `PageContent`

Mapped from `tblPageContent`.

| Property | Legacy field | Notes |
|---|---|---|
| `Id` | `ContentID` | Identity |
| `PageId` | `PageID` | FK to `tblPages` |
| `Content` | `PageContent` | Sanitized HTML |
| `ModifiedAt` | `ModifiedDate` | UTC timestamp |

The legacy application appends a new content row on every update and selects the latest row by `ContentID`. The new model preserves that behavior as an append-only revision history.

`Page` exposes:

```text
LatestContentId
LatestContent
LatestContentModifiedAt
```

A page update therefore:

1. Validates the new content.
2. Inserts a new `PageContent` revision.
3. Makes that revision the page’s latest content.
4. Writes an audit event.
5. Commits as one transaction.

---

### `SiteSetting`

Mapped from `tblGlobalSettings`.

| Property | Legacy field |
|---|---|
| `Id` | `SettingId` |
| `Category` | `SettingCategory` |
| `Name` | `SettingName` |
| `Value` | `SettingValue` |
| `ValueType` | `ValueType` |
| `ValidationRule` | `ValidationRule` |
| `Description` | `SettingDescription` |
| `SortOrder` | `SortOrder` |
| `CreatedAt` | `CreationDate` |
| `UpdatedAt` | `ModifiedDate` |

Rules:

- Use a composite unique key such as `(Category, Name)`.
- Preserve compatibility with lookups by `SettingName` where required.
- Values must be parsed according to `ValueType`.
- Setting values must not be executed as code.
- Settings should be cached and invalidated after administrative changes.

This slice only reads settings. Settings CRUD belongs to a later slice.

---

### `AdminAuditEvent`

Mapped conceptually from `tblLog`.

Recommended canonical model:

| Property | Notes |
|---|---|
| `Id` | Identity |
| `OccurredAt` | UTC timestamp |
| `ActorUserId` | Nullable for system events |
| `Action` | `PAGE_CREATED`, `PAGE_UPDATED`, `PAGE_DELETED`, etc. |
| `EntityType` | `Page`, `User`, `Setting` |
| `EntityId` | Affected entity identifier |
| `Result` | Success/failure |
| `DetailsJson` | Structured, redacted metadata |
| `CorrelationId` | Request correlation identifier |

The existing `tblLog` has only `Description` and `Date`; the target schema should add actor, action, entity, and structured-detail fields or introduce a dedicated audit table.

Audit events must not contain:

- Passwords.
- Session values.
- Full page content.
- Sensitive request headers.
- Raw validation payloads.

---

### Derived domain objects

#### `AdminSession`

Not mapped directly to a table.

- Server-side opaque session.
- Bound to an authenticated user.
- Stored in SQL Server or a distributed cache.
- Represented to the browser only by an HTTP-only cookie.

#### `SiteAvailability`

Derived from deployment/configuration state:

```text
IsOffline
MaintenanceMessage
```

The availability endpoint must remain reachable when the site is offline and before authentication middleware runs.

---

### 2.2 Schema inventory and slice relevance

| Table | Canonical entity | Relevance |
|---|---|---|
| `tblForms` | `FormField` | Out of scope |
| `tblGlobalSettings` | `SiteSetting` | Auth/dashboard dependency; read-only in this slice |
| `tblLog` | `AdminAuditEvent` | Administrative audit logging |
| `tblModules` | `ModuleInstance` | Shared CMS dependency; out of scope |
| `tblModuleTypes` | `ModuleType` | Shared CMS dependency; out of scope |
| `tblPageContent` | `PageContent` | Core |
| `tblPages` | `Page` | Core |
| `tblProducts` | `Product` | Out of scope |
| `tblTestimonials` | `Testimonial` | Out of scope |
| `tblUserRoles` | `UserRole` | Core authentication dependency |
| `tblUsers` | `AdminUser` | Core authentication dependency |

No slice code accesses `tblForms`, `tblProducts`, or `tblTestimonials`.

---

### 2.3 Data-integrity improvements required during migration

The supplied Access DDL has no declared foreign keys or most uniqueness constraints. The target schema should add:

- FK from `tblUsers.Role` to `tblUserRoles`.
- FK from `tblPageContent.PageID` to `tblPages.PageID`.
- Self-FK from `tblPages.ParentPage` to `tblPages.PageID`.
- Unique index on `tblUsers.UserID`.
- Unique index on `tblPages.FilePath`.
- Unique index on `tblPages.Name`, if legacy behavior requires unique page names.
- Unique index on settings `(Category, Name)`.
- Unique index on role `Level` and `Name`.
- Indexes for:
  - `tblPages.IsActive`
  - `tblPages.IsInMainMenu`
  - `tblPages.ParentPageId`
  - `tblPages.MenuIndex`
  - `tblPageContent.PageId`
  - audit `OccurredAt`

Type normalization:

| Legacy type | Target type |
|---|---|
| `INTEGER` flags | `bit`/`bool` |
| `TEXT` | `nvarchar` or `nvarchar(max)` for content |
| `DATE/TIMESTAMP` text | `datetime2` UTC |
| Price integers | Retain integer minor-unit semantics |
| Identity columns | SQL Server `IDENTITY` |
| Concurrency | New `rowversion` column |

---

## 3. Backend and Frontend Architecture

### 3.1 Runtime shape

```text
React TypeScript SPA
        |
        | same-origin /api/v1
        v
ASP.NET 10 modular monolith / BFF
        |
        | application services
        v
EF Core 10 data access
        |
        v
SQL Server
```

The .NET application should host:

- Versioned REST APIs.
- React static assets.
- OpenAPI documentation.
- Authentication and authorization middleware.
- Request validation and problem-details handling.

Suggested module boundaries:

```text
AdminApi/
  Modules/
    AdminAuth/
    Pages/
    Settings/
    Audit/
  Shared/
    Authorization/
    Errors/
    Security/
    Observability/
```

Page functionality should be split into:

- `PageQueryService` — list/detail projections.
- `PageCommandService` — create/update/delete transactions.
- `PageSlugGenerator` — canonical path generation.
- `PageContentSanitizer` — server-side HTML allowlist.
- `PageNavigationValidator` — parent/cycle checks.
- `PageCacheInvalidator` — cache updates after commits.

### 3.2 Authorization matrix

| Capability | Required role |
|---|---|
| Login | Public |
| Availability status | Public |
| CSRF token | Authenticated |
| Dashboard | `MANAGER` or `ADMIN` |
| List pages | `EDITOR`, `MANAGER`, or `ADMIN` |
| Read page | `EDITOR`, `MANAGER`, or `ADMIN` |
| Edit/update page | `MANAGER` or `ADMIN` |
| Create page | `ADMIN` |
| Delete page | `ADMIN` |
| Logout | Authenticated |

Authorization must be enforced server-side. React role checks are only for navigation and UX.

### 3.3 API behavior

- Use versioned routes under `/api/v1`.
- Use RFC 7807-style problem details.
- Return correlation IDs on errors.
- Use server-side pagination and filtering.
- Use optimistic concurrency with `If-Match`.
- Return:
  - `401` for unauthenticated requests.
  - `403` for insufficient role.
  - `404` for missing resources.
  - `409` for unique-name/path conflicts.
  - `412` for stale page versions.
  - `422` for validation failures.
- Never expose SQL errors or filesystem details.
- Do not expose legacy server name, IP address, or runtime details on the dashboard.

### 3.4 React TypeScript composition

Suggested routes:

```text
/admin/login
/admin
/admin/pages
/admin/pages/new
/admin/pages/:pageId/edit
/admin/unavailable
```

Recommended libraries:

- React Router or TanStack Router.
- React Query for server state.
- React Hook Form plus Zod for form validation.
- OpenAPI-generated TypeScript types, preferably through NSwag.
- TipTap/ProseMirror or an equivalent editor with legacy HTML import/export.

Recommended state boundaries:

- Server state: React Query.
- Form state: local component state.
- URL state: filters, sorting, and selected page ID.
- Authentication state: resolved from the server session; do not store access tokens in `localStorage`.

---

## 4. OpenAPI Specification Draft

This draft assumes the BFF/cookie-session architecture described above.

```yaml
openapi: 3.1.0
info:
  title: ASP VBScript CMS Administrative API
  version: 1.0.0-draft
  description: >
    REST API replacing the legacy admin login, dashboard, maintenance,
    and static-page CRUD endpoints.

servers:
  - url: /api/v1

security:
  - cookieAuth: []

tags:
  - name: Admin Authentication
  - name: Admin Dashboard
  - name: Site Status
  - name: Pages

paths:
  /admin/auth/login:
    post:
      operationId: loginAdmin
      summary: Authenticate an administrator
      security: []
      x-required-roles: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: Authentication succeeded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'

  /admin/auth/logout:
    post:
      operationId: logoutAdmin
      summary: End the current administrator session
      x-required-roles: [EDITOR, MANAGER, ADMIN]
      parameters:
        - $ref: '#/components/parameters/CsrfToken'
      responses:
        '204':
          description: Session ended
        '401':
          $ref: '#/components/responses/Unauthorized'

  /admin/csrf:
    get:
      operationId: getCsrfToken
      summary: Retrieve the current CSRF token
      x-required-roles: [EDITOR, MANAGER, ADMIN]
      responses:
        '200':
          description: CSRF token returned in a response header
          headers:
            X-CSRF-Token:
              required: true
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
                required: [csrfToken]
                properties:
                  csrfToken:
                    type: string

  /admin/status:
    get:
      operationId: getAdminStatus
      summary: Return public maintenance and service status
      description: Must remain available while the site is offline.
      security: []
      x-required-roles: []
      responses:
        '200':
          description: Current availability status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatusResponse'

  /admin/dashboard:
    get:
      operationId: getAdminDashboard
      summary: Return administrative dashboard data
      x-required-roles: [MANAGER, ADMIN]
      responses:
        '200':
          description: Dashboard read model
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DashboardResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

  /admin/pages:
    get:
      operationId: listPages
      summary: List pages
      x-required-roles: [EDITOR, MANAGER, ADMIN]
      parameters:
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/PageSize'
        - name: active
          in: query
          schema:
            type: boolean
        - name: mainMenu
          in: query
          schema:
            type: boolean
        - name: includeInactive
          in: query
          schema:
            type: boolean
            default: false
        - name: parentPageId
          in: query
          schema:
            type: integer
            nullable: true
        - name: q
          in: query
          schema:
            type: string
            maxLength: 100
        - name: sort
          in: query
          schema:
            type: string
            enum: [name, title, filePath, menuIndex, updatedAt]
            default: updatedAt
        - name: direction
          in: query
          schema:
            type: string
            enum: [asc, desc]
            default: desc
      responses:
        '200':
          description: Paginated page list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PageListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

    post:
      operationId: createPage
      summary: Create a page and its initial content
      x-required-roles: [ADMIN]
      parameters:
        - $ref: '#/components/parameters/CsrfToken'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PageCreateRequest'
      responses:
        '201':
          description: Page created
          headers:
            Location:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Page'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '409':
          $ref: '#/components/responses/Conflict'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'

  /admin/pages/options:
    get:
      operationId: getPageOptions
      summary: Return parent-page and stylesheet options for forms
      x-required-roles: [EDITOR, MANAGER, ADMIN]
      responses:
        '200':
          description: Page form options
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PageOptionSet'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

  /admin/pages/{id}:
    parameters:
      - $ref: '#/components/parameters/PageId'

    get:
      operationId: getPage
      summary: Retrieve a page including its latest content
      x-required-roles: [EDITOR, MANAGER, ADMIN]
      responses:
        '200':
          description: Page details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Page'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '404':
          $ref: '#/components/responses/NotFound'

    patch:
      operationId: updatePage
      summary: Update page metadata, visibility, hierarchy, or content
      x-required-roles: [MANAGER, ADMIN]
      parameters:
        - $ref: '#/components/parameters/CsrfToken'
        - $ref: '#/components/parameters/IfMatch'
      requestBody:
        required: true
        description: At least one property must be supplied.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PageUpdateRequest'
      responses:
        '200':
          description: Page updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Page'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '404':
          $ref: '#/components/responses/NotFound'
        '409':
          $ref: '#/components/responses/Conflict'
        '412':
          $ref: '#/components/responses/PreconditionFailed'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'

    delete:
      operationId: deletePage
      summary: Permanently delete a page and its content
      description: Deletion is transactional and audit logged.
      x-required-roles: [ADMIN]
      parameters:
        - $ref: '#/components/parameters/CsrfToken'
        - $ref: '#/components/parameters/IfMatch'
      responses:
        '204':
          description: Page deleted
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '404':
          $ref: '#/components/responses/NotFound'
        '412':
          $ref: '#/components/responses/PreconditionFailed'

components:
  securitySchemes:
    cookieAuth:
      type: apiKey
      in: cookie
      name: cms_admin_session
      description: HTTP-only, Secure, SameSite=Strict administrator session cookie

  parameters:
    PageId:
      name: id
      in: path
      required: true
      schema:
        type: integer
        minimum: 1

    Page:
      name: page
      in: query
      schema:
        type: integer
        minimum: 1
        default: 1

    PageSize:
      name: pageSize
      in: query
      schema:
        type: integer
        minimum: 1
        maximum: 200
        default: 50

    CsrfToken:
      name: X-CSRF-Token
      in: header
      required: true
      schema:
        type: string

    IfMatch:
      name: If-Match
      in: header
      required: true
      description: Current page version returned by the last read operation.
      schema:
        type: integer
        minimum: 1

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ApiProblem'

    Forbidden:
      description: Insufficient role
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ApiProblem'

    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ApiProblem'

    Conflict:
      description: Unique-name or path conflict
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ApiProblem'

    PreconditionFailed:
      description: Stale optimistic-concurrency version
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ApiProblem'

    UnprocessableEntity:
      description: Validation failure
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ApiProblem'

  schemas:
    LoginRequest:
      type: object
      additionalProperties: false
      required: [userId, password]
      properties:
        userId:
          type: string
          maxLength: 255
        password:
          type: string
          format: password
          minLength: 1
          maxLength: 256

    LoginResponse:
      type: object
      additionalProperties: false
      required: [user]
      properties:
        user:
          $ref: '#/components/schemas/AdminUser'

    AdminUser:
      type: object
      additionalProperties: false
      required: [id, userId, fullName, roles]
      properties:
        id:
          type: integer
        userId:
          type: string
        fullName:
          type: string
        roles:
          type: array
          items:
            type: string
            enum: [GUEST, REGISTERED, EDITOR, MANAGER, ADMIN]

    StatusResponse:
      type: object
      additionalProperties: false
      required: [available, siteOffline, maintenanceMessage]
      properties:
        available:
          type: boolean
        siteOffline:
          type: boolean
        maintenanceMessage:
          type: string
        serviceVersion:
          type: string

    DashboardResponse:
      type: object
      additionalProperties: false
      required: [user, counts, recentAuditEvents]
      properties:
        user:
          $ref: '#/components/schemas/AdminUser'
        counts:
          $ref: '#/components/schemas/PageCounts'
        recentAuditEvents:
          type: array
          items:
            $ref: '#/components/schemas/AuditEventSummary'

    PageCounts:
      type: object
      additionalProperties: true
      properties:
        total:
          type: integer
        active:
          type: integer
        inactive:
          type: integer
        inMainMenu:
          type: integer

    AuditEventSummary:
      type: object
      additionalProperties: false
      required: [id, occurredAt, action, entityType, result]
      properties:
        id:
          type: integer
        occurredAt:
          type: string
          format: date-time
        actorUserId:
          type: integer
          nullable: true
        action:
          type: string
        entityType:
          type: string
        entityId:
          type: integer
          nullable: true
        result:
          type: string
          enum: [SUCCESS, FAILURE]

    PageOption:
      type: object
      additionalProperties: false
      required: [id, label]
      properties:
        id:
          type: integer
        label:
          type: string

    PageOptionSet:
      type: object
      additionalProperties: false
      required: [parents, styles, defaults]
      properties:
        parents:
          type: array
          items:
            $ref: '#/components/schemas/PageOption'
        styles:
          type: array
          items:
            type: string
        defaults:
          type: object
          properties:
            active:
              type: boolean
            mainMenu:
              type: boolean
            style:
              type: string
              default: main

    PageCreateRequest:
      type: object
      additionalProperties: false
      required: [pageName, pageTitle, pageContent]
      properties:
        pageName:
          type: string
          minLength: 1
          maxLength: 120
        pageTitle:
          type: string
          minLength: 1
          maxLength: 120
        pageContent:
          type: string
          minLength: 1
          maxLength: 1000000
        pageFileName:
          type: string
          description: >
            Optional normalized virtual path. If omitted, generated from pageName.
        hoverText:
          type: string
          maxLength: 255
        description:
          type: string
          maxLength: 250
        keywords:
          type: string
          maxLength: 500
        style:
          type: string
          maxLength: 100
          default: main
        parentPageId:
          type: integer
          nullable: true
        menuIndex:
          type: integer
          nullable: true
          minimum: 0
        active:
          type: boolean
          default: true
        mainMenu:
          type: boolean
          default: false

    PageUpdateRequest:
      type: object
      additionalProperties: false
      properties:
        pageName:
          type: string
          minLength: 1
          maxLength: 120
        pageTitle:
          type: string
          minLength: 1
          maxLength: 120
        pageContent:
          type: string
          minLength: 1
          maxLength: 1000000
        pageFileName:
          type: string
        hoverText:
          type: string
          maxLength: 255
        description:
          type: string
          maxLength: 250
        keywords:
          type: string
          maxLength: 500
        style:
          type: string
          maxLength: 100
        parentPageId:
          type: integer
          nullable: true
        menuIndex:
          type: integer
          nullable: true
          minimum: 0
        active:
          type: boolean
        mainMenu:
          type: boolean

    Page:
      type: object
      additionalProperties: false
      required:
        - id
        - name
        - title
        - filePath
        - active
        - mainMenu
        - parentPageId
        - menuIndex
        - createdAt
        - updatedAt
        - content
        - contentModifiedAt
        - version
      properties:
        id:
          type: integer
        name:
          type: string
        title:
          type: string
        filePath:
          type: string
        hoverText:
          type: string
        description:
          type: string
        keywords:
          type: string
        style:
          type: string
        active:
          type: boolean
        mainMenu:
          type: boolean
        menuIndex:
          type: integer
          nullable: true
        parentPageId:
          type: integer
          nullable: true
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
        content:
          type: string
        contentId:
          type: integer
          nullable: true
        contentModifiedAt:
          type: string
          format: date-time
          nullable: true
        version:
          type: integer
          minimum: 1

    PageListResponse:
      type: object
      additionalProperties: false
      required: [items, pagination]
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/Page'
        pagination:
          $ref: '#/components/schemas/PaginationMeta'

    PaginationMeta:
      type: object
      additionalProperties: false
      required: [page, pageSize, totalItems, totalPages]
      properties:
        page:
          type: integer
        pageSize:
          type: integer
        totalItems:
          type: integer
        totalPages:
          type: integer

    ValidationError:
      type: object
      additionalProperties: false
      required: [field, message]
      properties:
        field:
          type: string
        message:
          type: string

    ApiProblem:
      type: object
      additionalProperties: false
      required: [type, title, status, code, correlationId]
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
          minimum: 400
          maximum: 599
        code:
          type: string
        message:
          type: string
        correlationId:
          type: string
        details:
          type: array
          items:
            $ref: '#/components/schemas/ValidationError'
```

---

## 5. Architecture Decision Records

### ADR-001 — Use a modular .NET 10 monolith with a React BFF

**Status:** Proposed

**Context**

The legacy application combines routing, authorization, database access, form handling, file operations, and HTML rendering in included ASP files. A big-bang rewrite would create excessive cutover risk.

**Decision**

- Host the REST API and React application in one ASP.NET 10 deployment.
- Use same-origin `/api/v1` requests.
- Organize the backend into independently testable administrative modules.
- Keep the database-access and application-service layers separate from endpoint code.
- Generate React TypeScript types from the OpenAPI contract.

**Consequences**

- Benefits:
  - No initial CORS/token-boundary complexity.
  - Shared validation and error handling.
  - Simpler deployment and rollback.
  - Clear module boundaries without premature distributed-systems complexity.
- Costs:
  - Modules must enforce ownership boundaries manually.
  - The application can grow unless module boundaries and API contracts are maintained.

**Alternatives rejected**

- Microservices for this slice: excessive operational complexity.
- Direct in-place replacement of ASP files: preserves legacy coupling and risk.
- Separate frontend API domain from the start: unnecessary for the initial migration.

---

### ADR-002 — Migrate using a strangler facade rather than a big-bang replacement

**Status:** Proposed

**Context**

The legacy pages are interwoven with bootstrap, settings, user, module, and filesystem behavior. Replacing everything simultaneously would make rollback and comparison difficult.

**Decision**

Use a reverse-proxy strangler pattern:

1. Keep legacy ASP endpoints available.
2. Add new `/api/v1/admin/...` routes beside them.
3. Route new React pages to the .NET application.
4. Gradually move individual capabilities.
5. Return `410 Gone` or redirect old endpoints after retirement.

Recommended phases:

1. Baseline schema, data, and physical-file inventory.
2. Build and test the new API contract.
3. Migrate non-sensitive reference data.
4. Run the new application in read-only mode.
5. Compare page counts, metadata, hierarchy, and latest content.
6. Enable page writes behind a feature flag.
7. Cut the React page routes to the new backend.
8. Make legacy ASP pages read-only.
9. Retire legacy page handlers.

**Consequences**

- Parallel operation is possible without two writers.
- Rollback is straightforward before writes begin.
- After write cutover, rollback requires disabling new writes and reconciling changes.
- Legacy session state and form state are not migrated.

**Alternatives rejected**

- Big-bang cutover: too risky.
- Dual-write to both databases: high split-brain and consistency risk.
- Direct in-place rewrite: does not reduce coupling.

---

### ADR-003 — Use SQL Server and EF Core with explicit schema migrations

**Status:** Proposed

**Context**

The legacy application uses Jet/ACE OLE DB, runtime ADOX metadata inspection, string-built SQL, and an embedded database file. These mechanisms are unsuitable for the target application.

**Decision**

- Move the canonical database to SQL Server.
- Use EF Core 10 for persistence.
- Replace dynamic SQL generation with parameterized queries and explicit mappings.
- Preserve legacy table names initially through EF mappings or compatibility views.
- Add foreign keys, uniqueness constraints, indexes, UTC timestamps, and `rowversion` values.
- Do not use runtime schema introspection.

**Migration rules**

- Migrate pages, page-content revisions, settings, roles, and audit-compatible data.
- Exclude plaintext passwords.
- Normalize booleans and timestamps.
- Resolve duplicate paths, orphan content, parent cycles, and duplicate settings before cutover.
- Parse `tblModules.PageIDs` into a normalized page-module association during the broader migration.

**Consequences**

- Requires a database migration and staging rehearsal.
- Provides transactional integrity, indexing, backups, and better operational tooling.
- Removes dependence on Access provider limitations and Jet engine behavior.

---

### ADR-004 — Replace the legacy RC4/session mechanism with OIDC-backed BFF authentication

**Status:** Proposed

**Context**

The legacy login:

- Uses a hardcoded RC4 passphrase.
- Stores encrypted user data in session/cookie state.
- Trusts `HTTP_REFERER` for login flow validation.
- Uses date-based session checks.
- Stores plaintext passwords.

**Decision**

- Use OIDC/OAuth 2.0 with authorization code and PKCE.
- Prefer an organizational or managed identity provider.
- Keep the admin UI and API same-origin through the ASP.NET BFF.
- Store server-side opaque sessions.
- Issue an HTTP-only, Secure, SameSite=Strict session cookie.
- Require a CSRF token for state-changing requests.
- Use Argon2id or bcrypt for local password hashes.
- Force password reset for users whose legacy passwords are plaintext.
- Do not migrate legacy session cookies or `CustomMessage` state.

**Consequences**

- Users must authenticate again after cutover.
- Password recovery and account lockout require proper identity workflows.
- The legacy RC4 implementation is not reused.
- Login failures use generic messages and rate limiting.
- Target-page redirection should use a signed, short-lived, single-use redirect parameter rather than an unvalidated query value.

**Alternatives rejected**

- Replacing RC4 with another home-grown cipher: inadequate.
- Storing JWTs in `localStorage`: increases token-theft risk.
- Trusting `Referer`: unreliable and insecure.

---

### ADR-005 — Make database content the canonical page model and remove physical page files

**Status:** Proposed

**Context**

Legacy page creation writes a physical `404.asp` placeholder and page updates move files through `FileSystemObject`. This creates dual storage, path-security concerns, and deployment-portability problems.

**Decision**

- Treat `Page` and `PageContent` as the canonical content model.
- Generate a normalized virtual `FilePath` from `PageName`.
- Resolve public pages by database path.
- Stop creating or moving physical ASP page files from the admin API.
- Keep existing physical files as a read-only compatibility artifact during migration.
- After cutover, missing database pages return a controlled 404 or redirect to the homepage.

**Consequences**

- Eliminates filesystem writes from page CRUD.
- Removes executable legacy page-file behavior.
- Improves deployment portability.
- Requires a physical-file inventory and compatibility check before retirement.
- Existing links must be tested because nested paths and default-page behavior may change.

---

### ADR-006 — Enforce transactional page commands, optimistic concurrency, and audit logging

**Status:** Proposed

**Context**

Legacy page create/update/delete operations use multiple unguarded database commands. Delete can leave inconsistent state, and there is no reliable concurrency control or administrative audit trail.

**Decision**

- Put each page command in one database transaction.
- Add `rowversion` to `tblPages`.
- Require `If-Match` for update and delete operations.
- Return `412 Precondition Failed` on stale versions.
- Append page-content revisions rather than overwriting history.
- Write audit events inside the same transaction.
- Invalidate page/settings caches only after commit.

**Command behavior**

Create:

```text
validate -> insert Page -> insert PageContent -> write audit -> commit
```

Update:

```text
validate -> check version -> insert content revision -> update metadata -> audit -> commit
```

Delete:

```text
check version -> delete content revisions -> delete Page -> audit -> commit
```

**Consequences**

- Prevents partially created or partially deleted pages.
- Detects concurrent editors.
- Provides accountability for administrative changes.
- Requires audit retention and redaction policies.

---

### ADR-007 — Sanitize page HTML on both write and read paths

**Status:** Proposed

**Context**

The legacy application stores HTML in `tblPageContent`, uses ad hoc tag normalization, and exposes content through generated HTML. The new architecture must preserve legacy content while reducing XSS risk.

**Decision**

- Define a server-side HTML allowlist based on observed legacy content.
- Reject or remove disallowed tags, scripts, event handlers, dangerous URLs, and unsafe attributes.
- Treat client-side sanitization as a UX enhancement only.
- Preserve supported token replacement, such as `{SITEURL}`, as literal server-side resolution.
- Never execute stored ASP directives or filesystem references from page content.

**Consequences**

- Existing content may be normalized during migration or first render.
- Editors need compatibility testing for legacy HTML.
- The allowlist should be reviewed as new content patterns are discovered.

---

## 6. Migration and Cutover Runbook

### Phase 1 — Baseline

- Take a full database and filesystem backup.
- Profile:
  - Duplicate page names and paths.
  - Orphaned content rows.
  - Parent cycles.
  - Duplicate settings.
  - Missing or invalid roles.
  - Physical files without database records.
- Record legacy counts and checksums.
- Freeze schema changes during migration validation.

### Phase 2 — Data migration

- Migrate roles and non-sensitive user profile data.
- Exclude plaintext passwords.
- Migrate settings with typed values.
- Migrate pages and all page-content revisions.
- Normalize dates to UTC.
- Add target constraints and indexes.
- Generate canonical slugs and resolve conflicts.

### Phase 3 — Read-only parallel run

- Run the .NET application against a migrated copy or read-only source.
- Compare:
  - Page counts.
  - Latest content.
  - Metadata.
  - Parent hierarchy.
  - Main-menu ordering.
  - Active/inactive state.
- Verify administrator authorization rules.

### Phase 4 — Write cutover

- Enable page writes through a feature flag.
- Make legacy page handlers read-only.
- Confirm audit events and cache invalidation.
- Run create/update/delete smoke tests.
- Monitor errors, latency, and data reconciliation.

### Phase 5 — UI cutover

- Route React admin pages to the new APIs.
- Replace query-string form state with REST resources and URL parameters.
- Deprecate legacy page handlers.
- Keep legacy authentication available only until the authentication cutover.

### Phase 6 — Retirement

- Redirect or return `410 Gone` for retired ASP endpoints.
- Remove legacy page handlers after all routes are verified.
- Retain backups according to retention policy.
- Review audit logs and access patterns.

---

## 7. Slice Acceptance Criteria

The `admin_crud` slice is complete when:

- Login, dashboard, status, and page CRUD APIs are available under `/api/v1`.
- OpenAPI documentation is published and consumed by the React client.
- Role checks match the authorization matrix.
- Page create/update/delete operations are atomic.
- Page updates use optimistic concurrency.
- Page deletion removes metadata and content together.
- No admin page operation writes physical page files.
- All administrative mutations produce redacted audit events.
- Legacy plaintext passwords are not migrated.
- All users are forced through credential reset or supported identity migration.
- The maintenance page remains reachable while the site is offline.
- HTML content is sanitized server-side.
- API errors use problem details and correlation IDs.
- Legacy and new page data reconcile before write cutover.
- Rollback is possible by disabling new writes or returning the proxy to the legacy application.