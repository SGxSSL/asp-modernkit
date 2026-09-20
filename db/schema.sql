CREATE TABLE [tblForms] (
    [FieldID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [FormID] INTEGER,
    [FieldName] TEXT,
    [FieldLabel] TEXT,
    [FieldType] TEXT,
    [FieldValue] TEXT,
    [FieldValidation] TEXT,
    [FieldDescription] TEXT,
    [CustomAttributes] TEXT,
    [FieldSortOrder] INTEGER,
    [CreatedDate] TEXT,
    [ModifiedDate] TEXT
);

CREATE TABLE [tblGlobalSettings] (
    [SettingId] INTEGER PRIMARY KEY AUTOINCREMENT,
    [SettingCategory] TEXT,
    [SettingName] TEXT,
    [SettingValue] TEXT,
    [ValueType] TEXT,
    [ValidationRule] TEXT,
    [SettingDescription] TEXT,
    [SortOrder] INTEGER,
    [CreationDate] TEXT,
    [ModifiedDate] TEXT
);

CREATE TABLE [tblLog] (
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Description] TEXT,
    [Date] TEXT
);

CREATE TABLE [tblModules] (
    [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Active] INTEGER,
    [Name] TEXT,
    [Description] TEXT,
    [Type] INTEGER,
    [StyleID] TEXT,
    [StyleClass] TEXT,
    [StyleInline] TEXT,
    [PageIDs] TEXT,
    [CustomSettings] TEXT,
    [SortOrder] INTEGER,
    [Location] TEXT
);

CREATE TABLE [tblModuleTypes] (
    [Disabled] INTEGER,
    [ModID] INTEGER,
    [ModName] TEXT,
    [ModHandler] TEXT,
    [ModDescription] TEXT
);

CREATE TABLE [tblPageContent] (
    [ContentID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [PageID] INTEGER,
    [PageContent] TEXT,
    [ModifiedDate] TEXT
);

CREATE TABLE [tblPages] (
    [PageID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Active] INTEGER,
    [PageName] TEXT,
    [PageFileName] TEXT,
    [PageLinkHoverText] TEXT,
    [PageDescription] TEXT,
    [PageKeywords] TEXT,
    [MainMenu] INTEGER,
    [PageTitle] TEXT,
    [MenuIndex] INTEGER,
    [ParentPage] INTEGER,
    [Style] TEXT,
    [CreateDate] TEXT
);

CREATE TABLE [tblProducts] (
    [Key] INTEGER PRIMARY KEY AUTOINCREMENT,
    [PID] TEXT,
    [Category] TEXT,
    [Brand] TEXT,
    [ProductLine] TEXT,
    [ProductName] TEXT,
    [Options] TEXT,
    [ShortDescription] TEXT,
    [LongDescription] TEXT,
    [RetailPrice] INTEGER,
    [WholesalePrice] INTEGER,
    [Image1] TEXT,
    [Image2] TEXT,
    [Active] INTEGER,
    [Recommended] INTEGER,
    [Timestamp] TEXT
);

CREATE TABLE [tblTestimonials] (
    [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Active] INTEGER,
    [Name] TEXT,
    [Email] TEXT,
    [ShowEmail] INTEGER,
    [SortOrder] INTEGER,
    [Comments] TEXT,
    [Location] TEXT,
    [TestimonialDate] TEXT,
    [Timestamp] TEXT
);

CREATE TABLE [tblUserRoles] (
    [id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Name] TEXT,
    [Description] TEXT,
    [Level] INTEGER
);

CREATE TABLE [tblUsers] (
    [id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [UserID] TEXT,
    [Password] TEXT,
    [LastLogin] TEXT,
    [Disabled] INTEGER,
    [Description] TEXT,
    [FirstName] TEXT,
    [SecondName] TEXT,
    [Email] TEXT,
    [Phone] TEXT,
    [Address1] TEXT,
    [Address2] TEXT,
    [City] TEXT,
    [State] TEXT,
    [PostalCode] TEXT,
    [Country] TEXT,
    [Role] INTEGER
);
