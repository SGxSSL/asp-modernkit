import DOMPurify from 'dompurify';

export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'span', 'div',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
      'blockquote', 'code', 'pre', 'hr', 'br',
      'figure', 'figcaption', 'video', 'audio', 'source',
      'iframe', 'object', 'param', 'embed',
      'form', 'input', 'label', 'select', 'option', 'textarea', 'button',
      'section', 'article', 'header', 'footer', 'nav', 'aside', 'main',
      'details', 'summary', 'mark', 'small', 'sub', 'sup', 'del', 'ins',
    ],
    ALLOWED_ATTR: [
      'class', 'id', 'style', 'href', 'src', 'alt', 'title', 'width', 'height',
      'name', 'type', 'value', 'placeholder', 'checked', 'disabled', 'selected',
      'target', 'rel', 'colspan', 'rowspan', 'datetime', 'cite',
    ],
    ALLOW_DATA_ATTR: false,
    FORBID_TAGS: ['script', 'style', 'form', 'input', 'iframe', 'object', 'embed'],
    FORBID_ATTR: ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur'],
  });
}

export function sanitizeUrl(url: string): string {
  try {
    const parsed = new URL(url, window.location.origin);
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:' || parsed.protocol === '') {
      return url;
    }
    return '';
  } catch {
    return '';
  }
}
