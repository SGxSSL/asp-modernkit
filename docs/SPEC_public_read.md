# Architectural Specification: `public_read` Slice

## 1. Domain Model

### Entities

#### Page
Represents a page in the CMS, sourced from `tblPages` and `tblPageContent`.

| Property           | Type     | Description                          |
|--------------------|----------|--------------------------------------|
| PageId             | int      | Primary key                          |
| Active             | bool     | Whether the page is active           |
| PageName           | string   | Display name of the page             |
| PageFileName       | string   | File name used for routing           |
| PageLinkHoverText  | string   | Tooltip text for navigation links    |
| PageDescription    | string   | Meta description                     |
| PageKeywords       | string   | Meta keywords                        |
| MainMenu           | bool     | Whether the page appears in main menu|
| PageTitle          | string   | Title tag content                    |
| MenuIndex          | int      | Sort order in menu                   |
| ParentPageId       | int?     | Reference to parent page             |
| Style              | string   | Custom stylesheet name               |
| CreateDate         | DateTime | When the page was created            |
| Content            | string   | HTML content of the page             |
| ModifiedDate       | DateTime | Last modified timestamp              |

#### Product
Represents a product listed on the site, sourced from `tblProducts`.

| Property          | Type     | Description                       |
|-------------------|----------|-----------------------------------|
| Key               | int      | Primary key                       |
| PID               | string   | Product ID                        |
| Category          | string   | Product category                  |
| Brand             | string   | Brand name                        |
| ProductLine       | string   | Product line                      |
| ProductName       | string   | Name of the product               |
| Options           | string   | Product options                   |
| ShortDescription  | string   | Brief description                 |
| LongDescription   | string   | Detailed description              |
| RetailPrice       | decimal  | Retail price                      |
| WholesalePrice    | decimal  | Wholesale price                   |
| Image1            | string   | URL/path to first image           |
| Image2            | string   | URL/path to second image          |
| Active            | bool     | Whether the product is active     |
| Recommended       | bool     | Whether the product is recommended|
| Timestamp         | DateTime | Record timestamp                  |

#### Testimonial
Represents a customer testimonial, sourced from `tblTestimonials`.

| Property         | Type     | Description                         |
|------------------|----------|-------------------------------------|
| ID               | int      | Primary key                         |
| Active           | bool     | Whether the testimonial is active   |
| Name             | string   | Customer name                       |
| Email            | string   | Customer email                      |
| ShowEmail        | bool     | Whether to display email publicly   |
| SortOrder        | int      | Display order                       |
| Comments         | string   | Testimonial text                    |
| Location         | string   | Customer location                   |
| TestimonialDate  | DateTime | Date of the testimonial             |
| Timestamp        | DateTime | Record timestamp                  |

#### GlobalSetting
Represents a global setting, sourced from `tblGlobalSettings`.

| Property            | Type     | Description                       |
|---------------------|----------|-----------------------------------|
| SettingId           | int      | Primary key                       |
| SettingCategory     | string   | Category of the setting           |
| SettingName         | string   | Name of the setting               |
| SettingValue        | string   | Value of the setting              |
| ValueType           | string   | Data type of the value            |
| ValidationRule      | string   | Validation rule for the value     |
| SettingDescription  | string   | Description of the setting        |
| SortOrder           | int      | Display order                     |
| CreationDate        | DateTime | When the setting was created      |
| ModifiedDate        | DateTime | Last modified timestamp           |

#### Module
Represents a modular component that can be attached to pages, sourced from `tblModules` and `tblModuleTypes`.

| Property         | Type     | Description                              |
|------------------|----------|------------------------------------------|
| ID               | int      | Primary key                              |
| Active           | bool     | Whether the module is active             |
| Name             | string   | Display name of the module               |
| Description      | string   | Description of the module                |
| Type             | int      | Reference to module type                 |
| StyleID          | string   | CSS ID for styling                       |
| StyleClass       | string   | CSS class for styling                    |
| StyleInline      | string   | Inline CSS styles                        |
| PageIDs          | string   | Pages where the module is active         |
| CustomSettings   | string   | Custom configuration for the module      |
| SortOrder        | int      | Display order                            |
| Location         | string   | Where the module renders (e.g., header)  |
| ModName          | string   | Name of the module type                  |
| ModHandler       | string   | Handler path for the module              |
| ModDescription   | string   | Description of the module type           |
| Disabled         | bool     | Whether the module type is disabled      |

---

## 2. OpenAPI Specification Drafts

### Base URL: `/api/public`

#### GET `/pages/{fileName}`
Retrieves a page by its filename.

```yaml
openapi: 3.0.0
info:
  title: Public Read API
  version: 1.0.0
paths:
  /pages/{fileName}:
    get:
      summary: Get a page by filename
      parameters:
        - in: path
          name: fileName
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Page found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Page'
        '404':
          description: Page not found
```

#### GET `/pages`
Lists all active pages.

```yaml
      '/pages':
        get:
          summary: List all active pages
          responses:
            '200':
              description: List of pages
              content:
                application/json:
                  schema:
                    type: array
                    items:
                      $ref: '#/components/schemas/Page'
```

#### GET `/products`
Lists all active products.

```yaml
      '/products':
        get:
          summary: List all active products
          responses:
            '200':
              description: List of products
              content:
                application/json:
                  schema:
                    type: array
                    items:
                      $ref: '#/components/schemas/Product'
```

#### GET `/products/{id}`
Retrieves a specific product by ID.

```yaml
      '/products/{id}':
        get:
          summary: Get a product by ID
          parameters:
            - in: path
              name: id
              required: true
              schema:
                type: integer
          responses:
            '200':
              description: Product found
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Product'
            '404':
              description: Product not found
```

#### GET `/testimonials`
Lists all active testimonials.

```yaml
      '/testimonials':
        get:
          summary: List all active testimonials
          responses:
            '200':
              description: List of testimonials
              content:
                application/json:
                  schema:
                    type: array
                    items:
                      $ref: '#/components/schemas/Testimonial'
```

#### GET `/settings`
Retrieves all global settings.

```yaml
      '/settings':
        get:
          summary: Get all global settings
          responses:
            '200':
              description: Global settings
              content:
                application/json:
                  schema:
                    type: object
                    additionalProperties:
                      type: string
```

#### GET `/modules`
Lists all active modules.

```yaml
      '/modules':
        get:
          summary: List all active modules
          responses:
            '200':
              description: List of modules
              content:
                application/json:
                  schema:
                    type: array
                    items:
                      $ref: '#/components/schemas/Module'
```

### Components

```yaml
components:
  schemas:
    Page:
      type: object
      properties:
        pageId:
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
        parentPageId:
          type: integer
          nullable: true
        style:
          type: string
        createDate:
          type: string
          format: date-time
        content:
          type: string
        modifiedDate:
          type: string
          format: date-time

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
          type: number
          format: double
        wholesalePrice:
          type: number
          format: double
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
          type: string
        customSettings:
          type: string
        sortOrder:
          type: integer
        location:
          type: string
        modName:
          type: string
        modHandler:
          type: string
        modDescription:
          type: string
        disabled:
          type: boolean
```

---

## 3. Architecture Decision Records (ADRs)

### ADR-001: Migration Strategy for Public-Facing Pages

**Status:** Accepted  
**Context:** The legacy Classic ASP application serves public-facing pages through individual `.asp` files that rely on server-side includes and inline VBScript. These pages dynamically pull content from a database using ADO recordsets.  
**Decision:** Replace each legacy endpoint with a RESTful API in .NET 10 that returns structured JSON data. The React frontend will consume these APIs to render pages.  
**Consequences:**
- Improved separation of concerns between backend logic and frontend presentation.
- Enables better caching strategies at both API and client levels.
- Requires reimplementation of dynamic features like navigation menus and breadcrumbs in the frontend.

### ADR-002: Data Access Layer Implementation

**Status:** Proposed  
**Context:** Legacy code uses direct ADO calls scattered across multiple classes and functions.  
**Decision:** Implement a clean data access layer using Entity Framework Core with repository pattern. Map existing database tables to strongly-typed entities.  
**Consequences:**
- Reduces risk of SQL injection vulnerabilities.
- Improves maintainability and testability of data operations.
- May require initial effort to map complex legacy queries.

### ADR-003: Handling Legacy Content Rendering

**Status:** Accepted  
**Context:** Legacy pages store HTML content directly in the database (`PageContent` field).  
**Decision:** Store raw HTML content in the API response and let the React frontend render it safely using `dangerouslySetInnerHTML`. Sanitize content during migration to prevent XSS attacks.  
**Consequences:**
- Preserves existing formatting and layout without requiring extensive refactoring.
- Introduces potential security risks if sanitization is not properly implemented.

### ADR-004: Session State Management

**Status:** Proposed  
**Context:** Legacy application relies heavily on ASP Session state for user authentication and temporary data storage.  
**Decision:** For public read-only endpoints, avoid session state entirely. Use JWT tokens or stateless authentication for any future authenticated features.  
**Consequences:**
- Simplifies scaling and deployment of public APIs.
- Eliminates dependency on sticky sessions or shared session stores.

### ADR-005: Static Asset Serving

**Status:** Proposed  
**Context:** Legacy application serves static assets (images, CSS, JS) directly from the web root.  
**Decision:** Serve static assets via CDN or dedicated static file server. Configure React build output to reference correct asset paths.  
**Consequences:**
- Offloads traffic from application servers.
- Improves performance through caching and geographic distribution.
- Requires coordination between backend and frontend teams for asset path management.