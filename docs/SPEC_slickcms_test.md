# Architectural Specification – Slice **slickcms_test**

> **Goal** – Modernise the legacy Classic ASP “slickcms_test” slice into a clean, maintainable .NET 10 (ASP.NET Core) back‑end exposing a versioned OpenAPI (Swagger) contract, while the front‑end will be rebuilt with React + TypeScript.  
> This document captures the **Domain Model**, a **draft OpenAPI contract** for the new APIs, and a set of **Architecture Decision Records (ADRs)** that justify the migration strategy and guide future work.

---

## 1. Overview  

| Aspect | Current (Classic ASP) | Target (Modern) |
|--------|----------------------|-----------------|
| **Runtime** | VBScript / ASP .NET Web Forms (no explicit DI) | ASP.NET Core 6/7/8 ( .NET 10 ) – modular, DI, async, middleware pipeline |
| **Data Access** | ADODB Recordset, inline SQL strings | EF Core (or Dapper) with strongly‑typed models, migrations |
| **Frontend** | Mixed HTML/ASP pages, limited separation | React + TypeScript SPA (calls the new REST APIs) |
| **Deployment** | Single monolithic IIS site | Containerised micro‑service (or single API app) behind reverse‑proxy / CDN |
| **Security** | Simple session cookies, limited auth | JWT‑based Bearer tokens, role‑based authorisation, HTTPS only |
| **Testing** | Manual / ad‑hoc | Automated unit / integration tests, CI/CD pipeline |

The slice contains a handful of data‑driven entities (Forms, Users, Products, etc.) and a set of “page‑level” endpoints (`slickcms/*`, `user/*`, `post/*`). The modern API will expose **CRUD** operations for each of those resources, plus a few auxiliary endpoints (e.g., pagination, statistics).

---

## 2. Domain Model  

The domain model mirrors the relational schema and the data‑access patterns used in the legacy code.  Each entity is a **first‑class aggregate root** in the API layer.

| Entity | Primary Key | Key Attributes (type) | Relationships / Notes |
|--------|-------------|-----------------------|-----------------------|
| **Form** (`tblForms`) | `FieldID` (int) | `FormID` (int) – optional FK to a parent Form, <br> `FieldName` (string), `FieldLabel` (string), `FieldType` (string), `FieldValue` (string), `FieldValidation` (string), `FieldDescription` (string), `CustomAttributes` (string), `FieldSortOrder` (int), `CreatedDate` (datetime), `ModifiedDate` (datetime) | One Form can own many `Field`s (1‑M). |
| **GlobalSetting** (`tblGlobalSettings`) | `SettingId` (int) | `SettingCategory` (string), `SettingName` (string), `SettingValue` (string), `ValueType` (string), `ValidationRule` (string), `SettingDescription` (string), `SortOrder` (int), `CreationDate` (datetime), `ModifiedDate` (datetime) | Stand‑alone key‑value store; used by the CMS for configuration. |
| **LogEntry** (`tblLog`) | `Id` (int) | `Description` (string), `Date` (datetime) | Auditing only – no business logic. |
| **Module** (`tblModules`) | `ID` (int) | `Active` (bool), `Name` (string), `Description` (string), `Type` (int), `StyleID` (string), `StyleClass` (string), `StyleInline` (string), `PageIDs` (string – CSV), `CustomSettings` (string), `SortOrder` (int), `Location` (string) | Belongs to a **ModuleType** (FK via `ModID`). |
| **ModuleType** (`tblModuleTypes`) | Composite (`Disabled`, `ModID`) | `ModName` (string), `ModHandler` (string), `ModDescription` (string) | One‑to‑many with `Modules` (`ModID`). |
| **PageContent** (`tblPageContent`) | `ContentID` (int) | `PageID` (int) – FK to `Pages`, `PageContent` (string), `ModifiedDate` (datetime) | One Page can have many `PageContent` rows (1‑M). |
| **Page** (`tblPages`) | `PageID` (int) | `Active` (bool), `PageName` (string), `PageFileName` (string), `PageLinkHoverText` (string), `PageDescription` (string), `PageKeywords` (string), `MainMenu` (bool), `PageTitle` (string), `MenuIndex` (int), `ParentPage` (int – FK to `Pages`), `Style` (string), `CreateDate` (datetime) | Hierarchical pages (self‑referencing via `ParentPage`). |
| **Product** (`tblProducts`) | `Key` (int) | `PID` (string), `Category` (string), `Brand` (string), `ProductLine` (string), `ProductName` (string), `Options` (string), `ShortDescription` (string), `LongDescription` (string), `RetailPrice` (int), `WholesalePrice` (int), `Image1` (string), `Image2` (string), `Active` (bool), `Recommended` (bool), `Timestamp` (datetime) | Typically displayed on product‑detail pages; no explicit FK in schema. |
| **Testimonial** (`tblTestimonials`) | `ID` (int) | `Active` (bool), `Name` (string), `Email` (string), `ShowEmail` (bool), `SortOrder` (int), `Comments` (string), `Location` (string), `TestimonialDate` (datetime), `Timestamp` (datetime) | Public‑facing content; may be filtered by `Active`. |
| **UserRole** (`tblUserRoles`) | `id` (int) | `Name` (string), `Description` (string), `Level` (int) | Role lookup for Users. |
| **User** (`tblUsers`) | `id` (int) | `UserID` (string) – business key, `Password` (string, hashed), `LastLogin` (datetime), `Disabled` (bool), `Description` (string), `FirstName` (string), `SecondName` (string), `Email` (string), `Phone` (string), `Address1` (string), `Address2` (string), `City` (string), `State` (string), `PostalCode` (string), `Country` (string), `Role` (int) – FK to `UserRoles` | Core security aggregate; `Role` points to `UserRoles`. |

### Key Relationships  

* **User → UserRole** – many‑to‑one (User has a Role).  
* **Page → PageContent** – one‑to‑many (a page can have many content blocks).  
* **Page → ParentPage** – self‑reference (nested pages).  
* **Form → Field** – one‑to‑many (form fields belong to a form).  
* **Module → ModuleType** – many‑to‑one (module type defines handler).  
* **Product** – no explicit FK; treated as a domain entity used by other parts of the CMS (e.g., product‑detail pages).  

All entities expose **CRUD** operations via the new API; the legacy code mostly performed **read‑only** queries (SELECT) and occasional **INSERT/UPDATE/DELETE** via stored procedures (`Admin_*`). The modern API will expose generic REST endpoints that map 1‑to‑1 to these operations.

---

## 3. Draft OpenAPI Specification (v3.0.0)

> **Base Path**: `/api/v1`  
> **Authentication** – JWT Bearer token (`Authorization: Bearer <token>`).  The API assumes the caller has already been authorised (role‑based).  
> **Responses** – JSON; errors follow a standard envelope (`code`, `message`, `details` optional).  

### 3.1 Common Components  

```yaml
components:
  schemas:
    PaginatedList:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/BaseEntity'
        total:
          type: integer
          description: Total count of items (including unseen pages)
        page:
          type: integer
          description: Current page number (1‑based)
        pageSize:
          type: integer
          description: Size of the page returned
      required:
        - items
        - total
        - page
        - pageSize

    BaseEntity:
      type: object
      abstract: true
      properties:
        id:
          type: integer
          format: int64
          description: Primary key.

    FormField:
      type: object
      properties:
        id:
          type: integer
        formId:
          type: integer
        fieldName:
          type: string
        fieldLabel:
          type: string
        fieldType:
          type: string
        fieldValue:
          type: string
        fieldValidation:
          type: string
        fieldDescription:
          type: string
        customAttributes:
          type: string
        fieldSortOrder:
          type: integer
        createdDate:
          type: string
          format: date-time
        modifiedDate:
          type: string
          format: date-time

    Form:
      allOf:
        - $ref: '#/components/schemas/BaseEntity'
        - type: object
          properties:
            formId:
              type: integer
            fields:
              type: array
              items:
                $ref: '#/components/schemas/FormField'
          required:
            - fields

    GlobalSetting:
      type: object
      properties:
        id:
          type: integer
        category:
          type: string
        name:
          type: string
        value:
          type: string
        valueType:
          type: string
        validationRule:
          type: string
        description:
          type: string
        sortOrder:
          type: integer
        createdDate:
          type: string
          format: date-time
        modifiedDate:
          type: string
          format: date-time

    LogEntry:
      type: object
      properties:
        id:
          type: integer
        description:
          type: string
        date:
          type: string
          format: date-time
      required:
        - id
        - description
        - date

    Module:
      type: object
      properties:
        id:
          type: integer
        active:
          type: boolean
        name:
          type: string
        description:
          type: string
        type:
          type: integer
        styleId:
          type: string
        styleClass:
          type: string
        styleInline:
          type: string
        pageIds:
          type: string   # CSV of page IDs
        customSettings:
          type: string
        sortOrder:
          type: integer
        location:
          type: string
      required:
        - id
        - active
        - name

    ModuleType:
      type: object
      properties:
        disabled:
          type: integer   # 0/1
        modId:
          type: integer
        modName:
          type: string
        modHandler:
          type: string
        modDescription:
          type: string
      required:
        - disabled
        - modId
        - modName

    PageContent:
      type: object
      properties:
        id:
          type: integer
        pageId:
          type: integer
        content:
          type: string
        modifiedDate:
          type: string
          format: date-time
      required:
        - id
        - pageId
        - content

    Page:
      type: object
      properties:
        id:
          type: integer
        active:
          type: boolean
        pageName:
          type: string
        pageFileName:
          type: string
        pageLinkHoverText:
          type: string
        pageDescription:
          type: string
        pageKeywords:
          type: string
        mainMenu:
          type: boolean
        pageTitle:
          type: string
        menuIndex:
          type: integer
        parentPage:
          type: integer   # nullable FK to Page.id
        style:
          type: string
        createDate:
          type: string
          format: date-time
      required:
        - id
        - active
        - pageName

    Product:
      type: object
      properties:
        key:
          type: integer
        pid:
          type: string
        category:
          type: string
        brand:
          type: string
        productLine:
          type: string
        productName:
          type: string
        options:
          type: string
        shortDescription:
          type: string
        longDescription:
          type: string
        retailPrice:
          type: integer
        wholesalePrice:
          type: integer
        image1:
          type: string
        image2:
          type: string
        active:
          type: boolean
        recommended:
          type: boolean
        timestamp:
          type: string
          format: date-time
      required:
        - key
        - pid
        - category
        - brand
        - productName
        - retailPrice
        - wholesalePrice

    Testimonial:
      type: object
      properties:
        id:
          type: integer
        active:
          type: boolean
        name:
          type: string
        email:
          type: string
        showEmail:
          type: boolean
        sortOrder:
          type: integer
        comments:
          type: string
        location:
          type: string
        testimonialDate:
          type: string
          format: date-time
        timestamp:
          type: string
          format: date-time
      required:
        - id
        - active
        - name
        - email

    UserRole:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
        level:
          type: integer
      required:
        - id
        - name

    User:
      type: object
      properties:
        id:
          type: integer
        userId:
          type: string
        password:
          type: string   # hashed
        lastLogin:
          type: string
          format: date-time
        disabled:
          type: boolean
        description:
          type: string
        firstName:
          type: string
        secondName:
          type: string
        email:
          type: string
        phone:
          type: string
        address1:
          type: string
        address2:
          type: string
        city:
          type: string
        state:
          type: string
        postalCode:
          type: string
        country:
          type: string
        roleId:
          type: integer   # FK to UserRole.id
        role:
          $ref: '#/components/schemas/UserRole'
      required:
        - id
        - userId
        - password
        - email
        - roleId
```

### 3.2 Endpoints  

> **Note** – The legacy URLs (`slickcms/*`, `user/*`, `post/*`) are mapped to logical resources.  The API design follows **RESTful** conventions and uses **JSON** payloads.

| HTTP Method | Path | Description | Request Body | Response |
|-------------|------|-------------|--------------|----------|
| `GET` | `/api/v1/forms` | List all forms (paginated) | – | `PaginatedList<Form>` |
| `POST` | `/api/v1/forms` | Create a new form (payload includes `formId` and `fields`) | `CreateFormRequest` | `201 Created` + `Form` |
| `GET` | `/api/v1/forms/{id}` | Retrieve a single form (including its fields) | – | `Form` |
| `PUT` | `/api/v1/forms/{id}` | Update an existing form (partial or full) | `UpdateFormRequest` | `200 OK` + `Form` |
| `DELETE` | `/api/v1/forms/{id}` | Delete a form (soft‑delete via flag if needed) | – | `204 No Content` |
| `GET` | `/api/v1/global-settings` | List all global settings (paginated) | – | `PaginatedList<GlobalSetting>` |
| `GET` | `/api/v1/global-settings/{id}` | Get a single setting | – | `GlobalSetting` |
| `GET` | `/api/v1/logs` | List log entries (optionally filter by date) | – | `PaginatedList<LogEntry>` |
| `GET` | `/api/v1/modules` | List active modules (paginated) | – | `PaginatedList<Module>` |
| `GET` | `/api/v1/modules/{id}` | Get a single module (including its type) | – | `Module` |
| `GET` | `/api/v1/modules/types` | List all module types (for dropdowns) | – | `List<ModuleType>` |
| `GET` | `/api/v1/pages` | List pages (active only by default) | – | `PaginatedList<Page>` |
| `GET` | `/api/v1/pages/{id}` | Get a page (including its content blocks) | – | `PageWithContent` (custom schema) |
| `GET` | `/api/v1/pages/children?parentId={id}` | Retrieve pages that have a given parent | – | `PaginatedList<Page>` |
| `GET` | `/api/v1/products` | List products (filter by `active`, `category`, etc.) | – | `PaginatedList<Product>` |
| `GET` | `/api/v1/products/{pid}` | Get a product by its business key (`pid`) | – | `Product` |
| `GET` | `/api/v1/testimonials` | List active testimonials (paginated) | – | `PaginatedList<Testimonial>` |
| `GET` | `/api/v1/testimonials/{id}` | Get a single testimonial | – | `Testimonial` |
| `GET` | `/api/v1/users/roles` | List all user roles (for UI dropdowns) | – | `List<UserRole>` |
| `GET` | `/api/v1/users` | List users (admin only) | – | `PaginatedList<User>` |
| `GET` | `/api/v1/users/{id}` | Get a single user (including role name) | – | `User` |
| `POST` | `/api/v1/users` | Register a new user (admin‑only) | `CreateUserRequest` | `201 Created` + `User` |
| `PUT` | `/api/v1/users/{id}` | Update user details (password hashing handled separately) | `UpdateUserRequest` | `200 OK` + `User` |
| `DELETE` | `/api/v1/users/{id}` | Soft‑delete a user (set `Disabled = true`) | – | `204 No Content` |
| `POST` | `/api/v1/auth/login` | **Authentication** – returns JWT | `LoginRequest` (`email`, `password`) | `200 OK` + JWT token |
| `POST` | `/api/v1/auth/logout` | Invalidate token (client‑side) | – | `204 No Content` |
| `GET` | `/api/v1/statistics` | CMS statistics (posts, pages, comments, etc.) | – | `StatisticsResponse` (custom) |

#### Example Schemas  

```yaml
  CreateFormRequest:
    type: object
    required:
      - formId
      - fields
    properties:
      formId:
        type: integer
      fields:
        type: array
        items:
          $ref: '#/components/schemas/FormField'

  UpdateFormRequest:
    type: object
    properties:
      fields:
        type: array
        items:
          $ref: '#/components/schemas/FormField'
      # optional: add/remove fields, change sort order, etc.

  LoginRequest:
    type: object
    required:
      - email
      - password
    properties:
      email:
        type: string
        format: email
      password:
        type: string

  CreateUserRequest:
    type: object
    required:
      - userId
      - email
      - password
    properties:
      userId:
        type: string
      email:
        type: string
        format: email
      password:
        type: string
      firstName:
        type: string
      secondName:
        type: string
      roleId:
        type: integer

  StatisticsResponse:
    type: object
    properties:
      posts:
        type: integer
      pages:
        type: integer
      comments:
        type: integer
      categories:
        type: integer
      tags:
        type: integer
      links:
        type: integer
      users:
        type: integer
```

### 3.3 Versioning & Compatibility  

* **URI versioning** – the `v1` segment of the path.  When a breaking change is required, a new version (`v2`) is introduced; old endpoints remain alive for a deprecation period (12 months).  
* **Content‑Negotiation** – only `application/json` is supported.  
* **Error handling** – consistent envelope (`code`, `message`, optional `details`).  HTTP status codes map to the domain (e.g., `400` for validation errors, `401`/`403` for auth, `404` for not‑found, `409` for conflict, `500` for unexpected server errors).  

---

## 4. Architecture Decision Records (ADRs)

> **ADR 1 – API‑First vs. Incremental Rewrite**  
> **Context** – The legacy code is a monolithic Classic ASP application with no clear separation between presentation and business logic.  
> **Decision** – Adopt an **API‑first** approach: design the public contract (OpenAPI) before implementing any new code.  The existing pages will be **wrapped** by thin API controllers that forward to the same underlying services, allowing a gradual migration of UI without a full rewrite.  
> **Consequences** –  
> * ✅ Clear separation of concerns; front‑end can be built independently.  
> * ✅ Allows parallel development of UI (React) and back‑end.  
> * ⚠️ Requires a thin “shim” layer to translate Classic ASP request/response patterns into HTTP/JSON; initial effort is higher but pays off in maintainability.  

> **ADR 2 – Data Migration Strategy**  
> **Context** – The relational schema (`tblForms`, `tblModules`, …) is the source of truth.  Directly copying rows into EF Core tables risks losing custom validation logic that lives in the Classic ASP code (e.g., `Clean` class, custom date formatting).  
> **Decision** – Perform a **read‑only migration**:  
> 1. Export each table to CSV (or use `bcp`/SQL bulk copy).  
> 2. Write **idempotent import scripts** that translate legacy data types (e.g., `TEXT` → `nvarchar(max)`, date strings → `datetime2`).  
> 3. Keep the original tables **read‑only** during the transition; the new API reads from both the legacy tables (via a **view** or **cached** EF Core queries) and the new tables, ensuring no data loss.  
> 4. Once all data is verified, **switch** the API to use only the new tables and deprecate the legacy tables.  
> **Consequences** –  
> * ✅ Minimal risk; the existing application continues to work unchanged.  
> * ✅ Guarantees data integrity and preserves legacy business rules during transition.  
> * ⚠️ Requires careful testing of CSV‑to‑entity mapping and a temporary dual‑read layer.  

> **ADR 3 – Authentication & Authorization Model**  
> **Context** – Legacy code relies on session cookies and a simple `Session("LoggedOn")` flag.  Modern APIs must be stateless and support mobile/web clients.  
> **Decision** – Implement **JWT‑based Bearer authentication** with **role‑based authorization** (scopes/claims).  The `User` aggregate will expose a `RoleId` claim; the authorization middleware will enforce that only users with the required `Role` (or higher) can call a given endpoint.  Passwords are stored as ** salted SHA‑256** hashes (or better, Argon2) – never plain text.  
> **Consequences** –  
> * ✅ Stateless, scalable, and works with SPA front‑ends.  
> * ✅ Centralised permission logic; easier to audit.  
> * ⚠️ Requires migration of existing session handling; users will need to re‑login after the switch.  

> **ADR 4 – API Versioning & Backward Compatibility**  
> **Context** – The legacy system has many internal endpoints that may be used by other parts of the site or third‑party integrations.  
> **Decision** – Use **URI versioning** (`/api/v1/…`).  All new endpoints are versioned; deprecated endpoints are marked with a `Deprecation` header and remain functional for **12 months**.  Semantic versioning of the API (major/minor) is applied to the **OpenAPI document**, not the URL.  
> **Consequences** –  
> * ✅ Consumers can upgrade at their own pace.  
> * ✅ Allows A/B testing of new features without breaking existing clients.  
> * ⚠️ Requires disciplined release process and clear deprecation communication.  

> **ADR 5 – Testing, CI/CD, and Observability**  
> **Context** – Legacy code has no automated tests; deployment is manual.  
> **Decision** – Introduce a **full CI/CD pipeline**:  
> * **Unit tests** for each service (xUnit/NUnit).  
> * **Integration tests** that spin up an in‑memory SQLite or PostgreSQL database and exercise the API endpoints (TestServer).  
> * **Contract tests** using **OpenAPI validation** (e.g., `SwaggerGen` + `Microsoft.AspNetCore.Mvc.Testing`).  
> * **Automated deployment** to a staging environment (Docker image) followed by a production rollout (blue‑green or canary).  
> * **Observability** – Structured logging (Serilog), health checks (`/health`), and distributed tracing (OpenTelemetry).  
> **Consequences** –  
> * ✅ Early defect detection, faster feedback loops.  
> * ✅ Confidence when modifying core domain logic or API contracts.  
> * ⚠️ Initial investment in tooling and test scaffolding, but pays off quickly.  

---

## 5. Summary  

* **Domain Model** – A set of strongly‑typed aggregates (Form, GlobalSetting, LogEntry, Module, ModuleType, PageContent, Page, Product, Testimonial, UserRole, User) that map cleanly to the existing relational schema and to the new RESTful API.  
* **OpenAPI Draft** – Provides a complete, versioned contract for CRUD operations on every resource, authentication flow, pagination, and error handling.  The contract can be generated automatically from the schema and used to generate client SDKs for the React front‑end.  
* **ADRs** – Offer a principled rationale for the migration path (API‑first, read‑only data migration, JWT auth, versioned URLs, comprehensive testing).  They serve as a decision log for the team and future maintainers.

Implementing this specification will give the **slickcms_test** slice a modern, maintainable foundation while preserving existing business logic and data, and will enable the React + TypeScript front‑end to consume a clean, well‑documented API.