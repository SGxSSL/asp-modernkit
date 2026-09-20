export interface PageDto {
  pageId: number;
  active: boolean;
  pageName: string;
  pageFileName: string;
  pageLinkHoverText: string | null;
  pageDescription: string | null;
  pageKeywords: string | null;
  mainMenu: boolean;
  pageTitle: string | null;
  menuIndex: number;
  parentPageId: number | null;
  style: string | null;
  createDate: string;
  content: string | null;
  modifiedDate: string | null;
}

export interface ProductDto {
  key: number;
  pid: string;
  category: string;
  brand: string;
  productLine: string;
  productName: string;
  options: string | null;
  shortDescription: string | null;
  longDescription: string | null;
  retailPrice: number;
  wholesalePrice: number;
  image1: string | null;
  image2: string | null;
  active: boolean;
  recommended: boolean;
  timestamp: string;
}

export interface TestimonialDto {
  id: number;
  active: boolean;
  name: string;
  email: string | null;
  showEmail: boolean;
  sortOrder: number;
  comments: string | null;
  location: string | null;
  testimonialDate: string;
  timestamp: string;
}

export interface GlobalSettingDto {
  settingId: number;
  settingCategory: string | null;
  settingName: string | null;
  settingValue: string | null;
  valueType: string | null;
  validationRule: string | null;
  settingDescription: string | null;
  sortOrder: number;
  creationDate: string;
  modifiedDate: string | null;
}

export interface ModuleDto {
  id: number;
  active: boolean;
  name: string;
  description: string | null;
  type: number;
  styleId: string | null;
  styleClass: string | null;
  styleInline: string | null;
  pageIds: string | null;
  customSettings: string | null;
  sortOrder: number;
  location: string | null;
  modName: string | null;
  modHandler: string | null;
  modDescription: string | null;
  disabled: boolean;
}
