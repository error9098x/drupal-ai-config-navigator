"""
scraper.py — Scrape Drupal.org admin documentation to populate config_data.json

This script fetches pages from Drupal.org documentation and extracts
configuration page information to add to our config_data.json file.
"""

import json
import re
from pathlib import Path
from typing import Any

OUTPUT_PATH = Path(__file__).parent / "config_nav" / "assets" / "config_data_new.json"

BASE_URL = "https://www.drupal.org"

DRUPAL_ADMIN_PATHS = [
    "/admin/config/system/site-information",
    "/admin/config/system/cron",
    "/admin/config/system/maintenance",
    "/admin/config/system/performance",
    "/admin/config/system/logging",
    "/admin/config/system/file-system",
    "/admin/config/media/file-system",
    "/admin/config/media/image-toolkit",
    "/admin/config/content/rsi",
    "/admin/config/search/settings",
    "/admin/config/search/overview",
    "/admin/config/services/rss-publishing",
    "/admin/config/services/aggregator",
    "/admin/config/services/openid-connect",
    "/admin/config/services/rest",
    "/admin/config/services/jsonapi",
    "/admin/config/development/devel",
    "/admin/config/development/performance",
    "/admin/config/development/logging",
    "/admin/config/development/maintenance",
    "/admin/config/user-interface/shortcut",
    "/admin/config/user-interface/adminimal-theme",
    "/admin/config/regional/settings",
    "/admin/config/regional/date-time",
    "/admin/config/regional/language",
    "/admin/config/regional/translate",
    "/admin/config/workflow/workflows",
    "/admin/config/workflow/actions",
    "/admin/config/workflow/rules",
    "/admin/config/workflow/triggers",
    "/admin/people/create",
    "/admin/people/permissions",
    "/admin/people/roles",
    "/admin/structure/types",
    "/admin/structure/block",
    "/admin/structure/menu",
    "/admin/structure/taxonomy",
    "/admin/structure/views",
    "/admin/structure/contact",
    "/admin/structure/comment",
    "/admin/structure/book",
    "/admin/structure/forum",
    "/admin/appearance",
    "/admin/modules",
    "/admin/reports",
    "/admin/reports/status",
    "/admin/reports/dblog",
    "/admin/reports/field-list",
    "/admin/reports/views-plugins",
    "/admin/reports/updates",
    "/admin/reports/access-denied",
    "/admin/reports/page-not-found",
    "/admin/reports/search",
    "/admin/content",
    "/admin/content/comment",
    "/admin/content/files",
    "/admin/config/content/scheduler",
    "/admin/config/content/metatag",
    "/admin/config/content/pathauto",
    "/admin/config/content/xmlsitemap",
    "/admin/config/content/redirect",
    "/admin/config/content/entityqueue",
    "/admin/config/content/quick-edit",
    "/admin/config/media/entity-browser",
    "/admin/config/media/embed-button",
    "/admin/config/media/image-styles",
    "/admin/config/media/media",
    "/admin/config/media/video-embed-field",
    "/admin/config/services/google-analytics",
    "/admin/config/services/simple-sitemap",
    "/admin/config/services/honeypot",
    "/admin/config/services/captcha",
    "/admin/config/services/recaptcha",
    "/admin/config/services/smtp",
    "/admin/config/services/mailsystem",
    "/admin/config/services/swiftmailer",
    "/admin/config/system/backup_migrate",
    "/admin/config/system/site-details",
    "/admin/config/system/error-reporting",
    "/admin/config/system/clean-urls",
    "/admin/config/system/actions",
    "/admin/config/system/uuid",
    "/admin/config/development/configuration",
    "/admin/config/development/configuration/sync",
    "/admin/config/development/configuration/import",
    "/admin/config/development/configuration/export",
    "/admin/config/development/configuration/full/import",
    "/admin/config/development/configuration/full/export",
]

KNOWN_CONFIG_PAGES: list[dict[str, Any]] = [
    {
        "title": "Cron Settings",
        "path": "/admin/config/system/cron",
        "module": "system",
        "description": "Configure automated tasks (cron jobs) that run periodically to perform maintenance tasks like indexing content, checking for updates, and clearing caches.",
        "keywords": ["cron", "scheduled tasks", "automated tasks", "cron job", "background tasks", "maintenance cron"],
        "synonyms": ["scheduled tasks", "automated maintenance", "cron configuration", "task scheduler"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Maintenance Mode",
        "path": "/admin/config/system/maintenance",
        "module": "system",
        "description": "Put the site in maintenance mode to prevent users from accessing the site during updates, migrations, or other maintenance tasks. Only administrators can access the site.",
        "keywords": ["maintenance mode", "offline", "site offline", "under maintenance", "maintenance page", "site down"],
        "synonyms": ["offline mode", "site offline", "maintenance page", "under construction"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Performance Settings",
        "path": "/admin/config/system/performance",
        "module": "system",
        "description": "Configure caching and bandwidth optimization settings. Enable CSS/JS aggregation, page caching, and optimize site performance for faster page loads.",
        "keywords": ["performance", "cache", "caching", "bandwidth", "optimization", "css aggregation", "js aggregation", "page cache", "speed"],
        "synonyms": ["site speed", "cache settings", "performance optimization", "page load speed"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Logging and Errors",
        "path": "/admin/config/system/logging",
        "module": "system",
        "description": "Configure error reporting, database logging settings, and how Drupal handles errors. Control what gets logged and displayed to users.",
        "keywords": ["logging", "errors", "error reporting", "dblog", "watchdog", "database log", "error messages", "debug"],
        "synonyms": ["error log", "system log", "debug settings", "error reporting"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "File System",
        "path": "/admin/config/system/file-system",
        "module": "system",
        "description": "Configure the file system paths for storing uploaded files, temporary files, and private files. Set default download method and file handling settings.",
        "keywords": ["file system", "files", "upload path", "public files", "private files", "temporary files", "file upload", "storage"],
        "synonyms": ["file storage", "upload settings", "file paths", "file directory"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Image Toolkit",
        "path": "/admin/config/media/image-toolkit",
        "module": "system",
        "description": "Configure the image toolkit used for image processing operations like resizing, cropping, and rotating images. Choose between GD or ImageMagick.",
        "keywords": ["image toolkit", "image processing", "gd", "imagemagick", "image resize", "image operations", "image manipulation"],
        "synonyms": ["image processing", "image library", "image settings"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "RSS Publishing",
        "path": "/admin/config/services/rss-publishing",
        "module": "node",
        "description": "Configure RSS feed settings for content syndication. Set feed description, number of items, and feed content settings.",
        "keywords": ["rss", "feed", "syndication", "rss feed", "content feed", "news feed", "xml feed"],
        "synonyms": ["rss settings", "feed settings", "content syndication", "news feed"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Regional Settings",
        "path": "/admin/config/regional/settings",
        "module": "system",
        "description": "Configure default country, first day of week, and timezone settings for the site. Affects date display and user-facing time information.",
        "keywords": ["regional", "country", "timezone", "locale", "first day of week", "regional settings", "site timezone"],
        "synonyms": ["locale settings", "timezone settings", "country settings"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Date and Time",
        "path": "/admin/config/regional/date-time",
        "module": "system",
        "description": "Configure date and time formats used throughout the site. Create custom date formats for display in content, views, and other areas.",
        "keywords": ["date format", "time format", "datetime", "date display", "time display", "date settings", "custom date format"],
        "synonyms": ["date settings", "time settings", "datetime configuration"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Language Settings",
        "path": "/admin/config/regional/language",
        "module": "language",
        "description": "Add, configure, and manage languages for multilingual sites. Set default language, enable language detection, and manage language settings.",
        "keywords": ["language", "multilingual", "languages", "add language", "default language", "language settings", "translation"],
        "synonyms": ["languages", "multilingual settings", "language configuration"],
        "permissions": ["administer languages"]
    },
    {
        "title": "Translate Interface",
        "path": "/admin/config/regional/translate",
        "module": "locale",
        "description": "Translate the site interface text to different languages. Search and edit translations for all user-facing text strings.",
        "keywords": ["translate", "translation", "interface translation", "translate strings", "localization", "i18n", "translate interface"],
        "synonyms": ["interface translation", "string translation", "localization"],
        "permissions": ["translate interface"]
    },
    {
        "title": "Workflows",
        "path": "/admin/config/workflow/workflows",
        "module": "workflows",
        "description": "Create and manage content moderation workflows. Define states and transitions for content approval processes.",
        "keywords": ["workflow", "workflows", "moderation", "approval workflow", "content moderation", "states", "transitions", "editorial workflow"],
        "synonyms": ["moderation workflow", "approval process", "content workflow"],
        "permissions": ["administer workflows"]
    },
    {
        "title": "Actions",
        "path": "/admin/config/system/actions",
        "module": "action",
        "description": "Configure actions that can be triggered by events or rules. Create and manage automated actions like sending emails, publishing content, or changing node status.",
        "keywords": ["actions", "automated actions", "triggers", "action configuration", "automated tasks", "action rules"],
        "synonyms": ["automated actions", "triggers configuration", "action settings"],
        "permissions": ["administer actions"]
    },
    {
        "title": "Views",
        "path": "/admin/structure/views",
        "module": "views",
        "description": "Create and manage views to display content in various formats. Build custom lists, grids, tables, and other displays of content and data.",
        "keywords": ["views", "content list", "display", "content display", "query builder", "views list", "custom display", "content query"],
        "synonyms": ["content displays", "views list", "content lists", "query builder"],
        "permissions": ["administer views"]
    },
    {
        "title": "Contact Forms",
        "path": "/admin/structure/contact",
        "module": "contact",
        "description": "Create and manage contact forms for site visitors. Add categories, set recipients, and configure form settings.",
        "keywords": ["contact", "contact form", "contact page", "feedback form", "contact categories", "email contact"],
        "synonyms": ["feedback form", "contact categories", "contact settings"],
        "permissions": ["administer contact forms"]
    },
    {
        "title": "Comment Types",
        "path": "/admin/structure/comment",
        "module": "comment",
        "description": "Configure comment types and settings. Manage comment fields, display settings, and comment moderation options.",
        "keywords": ["comments", "comment types", "comment settings", "comment configuration", "moderation comments"],
        "synonyms": ["comment configuration", "comment settings", "comment management"],
        "permissions": ["administer comment types"]
    },
    {
        "title": "Book Structure",
        "path": "/admin/structure/book",
        "module": "book",
        "description": "Manage book outlines and organize content into hierarchical book structures. Configure book navigation and outline settings.",
        "keywords": ["book", "book outline", "hierarchical content", "book structure", "book navigation", "chapters"],
        "synonyms": ["book outline", "book navigation", "book organization"],
        "permissions": ["administer book outlines"]
    },
    {
        "title": "Forum Structure",
        "path": "/admin/structure/forum",
        "module": "forum",
        "description": "Create and manage forum containers and forums. Organize discussion topics into hierarchical forum structures.",
        "keywords": ["forum", "forums", "discussion", "forum container", "forum topics", "message board", "discussion board"],
        "synonyms": ["forum settings", "discussion forums", "message board"],
        "permissions": ["administer forums"]
    },
    {
        "title": "Modules",
        "path": "/admin/modules",
        "module": "system",
        "description": "Enable, disable, and configure modules that extend Drupal functionality. Install new modules and manage module settings.",
        "keywords": ["modules", "enable module", "disable module", "install module", "extensions", "plugins", "functionality", "module list"],
        "synonyms": ["extend functionality", "module configuration", "enable extensions"],
        "permissions": ["administer modules"]
    },
    {
        "title": "Reports Dashboard",
        "path": "/admin/reports",
        "module": "system",
        "description": "Access various site reports including status report, available updates, database logs, and other diagnostic information.",
        "keywords": ["reports", "status report", "site status", "diagnostics", "logs", "updates report", "system status"],
        "synonyms": ["site reports", "status dashboard", "diagnostic reports"],
        "permissions": ["view site reports"]
    },
    {
        "title": "Status Report",
        "path": "/admin/reports/status",
        "module": "system",
        "description": "View a comprehensive status report of the Drupal installation including PHP version, database status, modules, and configuration issues.",
        "keywords": ["status", "status report", "site health", "system status", "diagnostics", "php info", "database status"],
        "synonyms": ["site health", "system status", "diagnostic report"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Database Logging",
        "path": "/admin/reports/dblog",
        "module": "dblog",
        "description": "View system events and errors logged in the database. Monitor site activity, errors, warnings, and user actions.",
        "keywords": ["dblog", "database log", "watchdog", "event log", "system log", "error log", "recent log entries", "activity log"],
        "synonyms": ["system log", "event log", "activity log", "watchdog log"],
        "permissions": ["view site reports"]
    },
    {
        "title": "Field List",
        "path": "/admin/reports/field-list",
        "module": "field_ui",
        "description": "View a list of all fields used on the site and their usage. See which content types and entities use each field.",
        "keywords": ["fields", "field list", "field usage", "field report", "content fields", "field inventory"],
        "synonyms": ["field report", "field inventory", "field usage report"],
        "permissions": ["administer content types"]
    },
    {
        "title": "Available Updates",
        "path": "/admin/reports/updates",
        "module": "update",
        "description": "Check for available updates to Drupal core, modules, and themes. View update status and download new versions.",
        "keywords": ["updates", "update report", "security updates", "module updates", "core updates", "theme updates", "update status"],
        "synonyms": ["update status", "available updates", "security updates"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Access Denied Report",
        "path": "/admin/reports/access-denied",
        "module": "dblog",
        "description": "View a list of access denied (403) errors that visitors have encountered. Identify permission issues and broken links.",
        "keywords": ["access denied", "403 errors", "permission errors", "access denied log", "forbidden pages"],
        "synonyms": ["403 log", "permission issues", "access denied log"],
        "permissions": ["view site reports"]
    },
    {
        "title": "Page Not Found Report",
        "path": "/admin/reports/page-not-found",
        "module": "dblog",
        "description": "View a list of page not found (404) errors that visitors have encountered. Identify broken links and missing content.",
        "keywords": ["page not found", "404 errors", "broken links", "missing pages", "404 report", "not found log"],
        "synonyms": ["404 log", "broken links", "missing pages report"],
        "permissions": ["view site reports"]
    },
    {
        "title": "Content Overview",
        "path": "/admin/content",
        "module": "node",
        "description": "View and manage all content on the site. Filter, edit, delete, and perform bulk operations on content items.",
        "keywords": ["content", "content list", "manage content", "content management", "all content", "node list", "articles", "pages"],
        "synonyms": ["content management", "content list", "manage articles"],
        "permissions": ["access content overview"]
    },
    {
        "title": "Comments Overview",
        "path": "/admin/content/comment",
        "module": "comment",
        "description": "View and manage all comments on the site. Filter, approve, delete, and perform bulk operations on comments.",
        "keywords": ["comments", "comment list", "manage comments", "comment approval", "comment moderation", "spam comments"],
        "synonyms": ["comment management", "comment moderation", "manage comments"],
        "permissions": ["administer comments"]
    },
    {
        "title": "Files Overview",
        "path": "/admin/content/files",
        "module": "file",
        "description": "View and manage all uploaded files on the site. Filter, delete, and track file usage across content.",
        "keywords": ["files", "file list", "manage files", "uploaded files", "file management", "media files", "attachments"],
        "synonyms": ["file management", "file list", "manage uploads"],
        "permissions": ["administer files"]
    },
    {
        "title": "URL Aliases",
        "path": "/admin/config/search/path",
        "module": "path",
        "description": "Create and manage custom URL aliases for content. Create search engine friendly URLs and manage path patterns.",
        "keywords": ["url alias", "path alias", "aliases", "url path", "friendly url", "clean url", "seo url", "custom url"],
        "synonyms": ["url aliases", "path aliases", "friendly urls", "clean urls"],
        "permissions": ["administer url aliases"]
    },
    {
        "title": "Pathauto Settings",
        "path": "/admin/config/content/pathauto",
        "module": "pathauto",
        "description": "Configure automatic URL alias generation patterns. Set patterns for content types, taxonomy terms, and user pages.",
        "keywords": ["pathauto", "automatic url", "url pattern", "automatic alias", "url generation", "path patterns", "automatic paths"],
        "synonyms": ["automatic url generation", "path patterns", "url patterns"],
        "permissions": ["administer pathauto"]
    },
    {
        "title": "Metatag Settings",
        "path": "/admin/config/content/metatag",
        "module": "metatag",
        "description": "Configure meta tags for SEO optimization. Set default meta tags for content types, taxonomy, and other pages.",
        "keywords": ["metatag", "meta tags", "seo", "seo settings", "meta description", "meta keywords", "open graph", "twitter cards"],
        "synonyms": ["meta tag settings", "seo configuration", "meta data"],
        "permissions": ["administer meta tags"]
    },
    {
        "title": "Scheduler Settings",
        "path": "/admin/config/content/scheduler",
        "module": "scheduler",
        "description": "Configure content scheduling settings. Set options for publishing and unpublishing content at specified times.",
        "keywords": ["scheduler", "schedule", "scheduled publishing", "time-based publishing", "publish later", "unpublish later", "content scheduling"],
        "synonyms": ["content scheduling", "scheduled content", "time-based publishing"],
        "permissions": ["administer scheduler"]
    },
    {
        "title": "XML Sitemap",
        "path": "/admin/config/content/xmlsitemap",
        "module": "xmlsitemap",
        "description": "Configure XML sitemap generation for search engines. Set content inclusion, priority settings, and submit to search engines.",
        "keywords": ["xml sitemap", "sitemap", "seo sitemap", "search engine sitemap", "google sitemap", "sitemap settings"],
        "synonyms": ["sitemap settings", "search engine sitemap", "seo sitemap"],
        "permissions": ["administer xmlsitemap"]
    },
    {
        "title": "Redirect Settings",
        "path": "/admin/config/content/redirect",
        "module": "redirect",
        "description": "Manage URL redirects to prevent 404 errors. Create, edit, and delete redirects for changed URLs.",
        "keywords": ["redirect", "redirects", "url redirect", "301 redirect", "page redirect", "redirect list", "url forwarding"],
        "synonyms": ["url redirects", "page redirects", "301 redirects"],
        "permissions": ["administer redirects"]
    },
    {
        "title": "Entity Queue",
        "path": "/admin/config/content/entityqueue",
        "module": "entityqueue",
        "description": "Create and manage queues of content items. Manually curate lists of featured or promoted content.",
        "keywords": ["entityqueue", "queue", "content queue", "featured content", "content list", "curated list", "entity queue"],
        "synonyms": ["content queue", "featured items", "curated content"],
        "permissions": ["administer entityqueue"]
    },
    {
        "title": "Image Styles",
        "path": "/admin/config/media/image-styles",
        "module": "image",
        "description": "Create and manage image styles for automatic image resizing, cropping, and effects. Apply transformations to uploaded images.",
        "keywords": ["image styles", "image resize", "image effects", "image crop", "image processing", "image styles list", "image presets"],
        "synonyms": ["image presets", "image effects", "image transformations"],
        "permissions": ["administer image styles"]
    },
    {
        "title": "Media Settings",
        "path": "/admin/config/media/media",
        "module": "media",
        "description": "Configure media library settings and media types. Manage media entity settings and display options.",
        "keywords": ["media", "media library", "media settings", "media types", "media management", "asset library"],
        "synonyms": ["media library settings", "media configuration", "asset management"],
        "permissions": ["administer media"]
    },
    {
        "title": "Entity Browser",
        "path": "/admin/config/media/entity-browser",
        "module": "entity_browser",
        "description": "Configure entity browsers for selecting content and media in forms. Create custom browsers for different use cases.",
        "keywords": ["entity browser", "media browser", "content selector", "file browser", "entity selection"],
        "synonyms": ["media browser", "content browser", "entity selection"],
        "permissions": ["administer entity browsers"]
    },
    {
        "title": "Google Analytics",
        "path": "/admin/config/services/google-analytics",
        "module": "google_analytics",
        "description": "Configure Google Analytics tracking for the site. Set tracking ID, configure tracking settings, and view analytics integration.",
        "keywords": ["google analytics", "analytics", "tracking", "statistics", "site analytics", "ga", "tracking code"],
        "synonyms": ["analytics settings", "tracking settings", "site statistics"],
        "permissions": ["administer google analytics"]
    },
    {
        "title": "Simple XML Sitemap",
        "path": "/admin/config/services/simple-sitemap",
        "module": "simple_sitemap",
        "description": "Configure simple XML sitemap generation. Set inclusion settings for content types, menu links, and custom links.",
        "keywords": ["sitemap", "xml sitemap", "simple sitemap", "sitemap generation", "seo sitemap"],
        "synonyms": ["sitemap settings", "sitemap generation"],
        "permissions": ["administer simple sitemap"]
    },
    {
        "title": "Honeypot Settings",
        "path": "/admin/config/services/honeypot",
        "module": "honeypot",
        "description": "Configure Honeypot spam protection settings. Set time limits and honeypot configuration for form spam prevention.",
        "keywords": ["honeypot", "spam protection", "spam prevention", "form protection", "anti-spam", "spam filter"],
        "synonyms": ["spam protection", "form protection", "anti-spam settings"],
        "permissions": ["administer honeypot"]
    },
    {
        "title": "CAPTCHA Settings",
        "path": "/admin/config/services/captcha",
        "module": "captcha",
        "description": "Configure CAPTCHA settings for spam protection. Set challenge types and apply CAPTCHAs to specific forms.",
        "keywords": ["captcha", "spam protection", "challenge", "human verification", "anti-spam", "captcha settings"],
        "synonyms": ["spam protection", "verification settings", "anti-spam"],
        "permissions": ["administer captcha"]
    },
    {
        "title": "reCAPTCHA Settings",
        "path": "/admin/config/services/recaptcha",
        "module": "recaptcha",
        "description": "Configure Google reCAPTCHA settings. Set site keys and configure v2 or v3 reCAPTCHA for forms.",
        "keywords": ["recaptcha", "google recaptcha", "captcha", "spam protection", "i am not a robot", "invisible captcha"],
        "synonyms": ["google captcha", "spam protection", "form verification"],
        "permissions": ["administer recaptcha"]
    },
    {
        "title": "SMTP Settings",
        "path": "/admin/config/services/smtp",
        "module": "smtp",
        "description": "Configure SMTP settings for sending emails. Set up external SMTP servers for reliable email delivery.",
        "keywords": ["smtp", "email", "mail server", "email settings", "email delivery", "outgoing mail", "smtp server"],
        "synonyms": ["email settings", "mail server settings", "email delivery"],
        "permissions": ["administer smtp"]
    },
    {
        "title": "Backup and Migrate",
        "path": "/admin/config/system/backup_migrate",
        "module": "backup_migrate",
        "description": "Configure backup and migration settings. Create scheduled backups, manual backups, and restore site data.",
        "keywords": ["backup", "migrate", "backup settings", "database backup", "site backup", "restore", "scheduled backup", "backup files"],
        "synonyms": ["site backup", "database backup", "backup configuration"],
        "permissions": ["administer backup and migrate"]
    },
    {
        "title": "Configuration Synchronization",
        "path": "/admin/config/development/configuration",
        "module": "config",
        "description": "Manage configuration synchronization between environments. Import and export configuration settings.",
        "keywords": ["configuration", "config sync", "import export", "config management", "configuration sync", "drush cex", "drush cim"],
        "synonyms": ["config management", "configuration management", "settings sync"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Configuration Import",
        "path": "/admin/config/development/configuration/import",
        "module": "config",
        "description": "Import configuration settings from files into the active site configuration. Apply configuration changes from development environments.",
        "keywords": ["config import", "configuration import", "import settings", "sync configuration", "apply configuration"],
        "synonyms": ["import configuration", "apply config", "config sync"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Configuration Export",
        "path": "/admin/config/development/configuration/export",
        "module": "config",
        "description": "Export current site configuration to files. Download configuration for version control or migration.",
        "keywords": ["config export", "configuration export", "export settings", "download configuration", "config files"],
        "synonyms": ["export configuration", "download config", "save configuration"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Shortcut Settings",
        "path": "/admin/config/user-interface/shortcut",
        "module": "shortcut",
        "description": "Configure shortcut links for quick access to frequently used pages. Manage shortcut sets and customize the shortcut bar.",
        "keywords": ["shortcut", "shortcuts", "quick links", "shortcut bar", "toolbar shortcuts", "favorite pages"],
        "synonyms": ["quick links", "shortcut bar", "favorite links"],
        "permissions": ["administer shortcuts"]
    },
    {
        "title": "Devel Settings",
        "path": "/admin/config/development/devel",
        "module": "devel",
        "description": "Configure Devel module settings for developers. Enable debug tools, query logging, and development helpers.",
        "keywords": ["devel", "developer", "debug", "development", "debug tools", "query log", "devel settings", "developer tools"],
        "synonyms": ["developer settings", "debug settings", "development tools"],
        "permissions": ["administer devel"]
    },
    {
        "title": "Search Settings",
        "path": "/admin/config/search/settings",
        "module": "search",
        "description": "Configure search settings for content indexing. Set minimum word length, indexing frequency, and search display options.",
        "keywords": ["search", "search settings", "content search", "search index", "search configuration", "search settings"],
        "synonyms": ["search configuration", "search index settings", "search options"],
        "permissions": ["administer search"]
    },
    {
        "title": "OpenID Connect",
        "path": "/admin/config/services/openid-connect",
        "module": "openid_connect",
        "description": "Configure OpenID Connect authentication providers. Enable social login and external authentication services.",
        "keywords": ["openid connect", "oauth", "social login", "authentication", "single sign on", "sso", "external login", "google login", "facebook login"],
        "synonyms": ["social login", "external authentication", "sso settings"],
        "permissions": ["administer openid connect"]
    },
    {
        "title": "REST Settings",
        "path": "/admin/config/services/rest",
        "module": "rest",
        "description": "Configure REST API endpoints and resources. Enable REST services for content and configure authentication methods.",
        "keywords": ["rest", "rest api", "api", "restful", "web services", "json api", "rest endpoints", "api settings"],
        "synonyms": ["api settings", "rest api configuration", "web services"],
        "permissions": ["administer rest resources"]
    },
    {
        "title": "JSON API Settings",
        "path": "/admin/config/services/jsonapi",
        "module": "jsonapi",
        "description": "Configure JSON API settings. Control resource exposure and API endpoint configuration for headless implementations.",
        "keywords": ["json api", "api", "headless", "jsonapi", "rest api", "api settings", "headless drupal"],
        "synonyms": ["api configuration", "headless settings", "json api"],
        "permissions": ["administer jsonapi"]
    },
    {
        "title": "Aggregator Settings",
        "path": "/admin/config/services/aggregator",
        "module": "aggregator",
        "description": "Configure RSS/Atom feed aggregator settings. Add external feeds and display aggregated content.",
        "keywords": ["aggregator", "rss", "feed", "feed aggregator", "news feed", "rss aggregator", "external feeds"],
        "synonyms": ["feed aggregator", "rss reader", "news aggregator"],
        "permissions": ["administer aggregator"]
    },
    {
        "title": "Paragraphs Settings",
        "path": "/admin/structure/paragraphs_type",
        "module": "paragraphs",
        "description": "Create and manage paragraph types for flexible content building. Configure fields and display settings for reusable content components.",
        "keywords": ["paragraphs", "paragraph types", "content builder", "flexible content", "paragraph settings", "content components"],
        "synonyms": ["content builder", "paragraph configuration", "flexible content types"],
        "permissions": ["administer paragraphs types"]
    },
    {
        "title": "Webform Settings",
        "path": "/admin/structure/webform",
        "module": "webform",
        "description": "Create and manage webforms for surveys, contact forms, and data collection. Configure form elements, email notifications, and submissions.",
        "keywords": ["webform", "forms", "survey", "contact form", "form builder", "webform settings", "form submissions"],
        "synonyms": ["form builder", "contact forms", "survey forms"],
        "permissions": ["administer webform"]
    },
    {
        "title": "Webform Submissions",
        "path": "/admin/structure/webform/submissions",
        "module": "webform",
        "description": "View and manage webform submissions. Export, delete, and analyze form submission data.",
        "keywords": ["webform submissions", "form submissions", "submissions", "form data", "submission list", "export submissions"],
        "synonyms": ["form submissions", "submission data", "form results"],
        "permissions": ["administer webform submission"]
    },
    {
        "title": "Layout Builder",
        "path": "/admin/structure/display-modes",
        "module": "layout_builder",
        "description": "Configure layout builder settings and manage display modes. Create custom layouts for content pages.",
        "keywords": ["layout builder", "layouts", "display modes", "page layout", "content layout", "drag and drop", "layout configuration"],
        "synonyms": ["page layouts", "display modes", "content layout"],
        "permissions": ["administer display modes"]
    },
    {
        "title": "Entity Display Modes",
        "path": "/admin/structure/display-modes/view",
        "module": "field_ui",
        "description": "Create and manage entity view modes. Configure different display formats for content in different contexts.",
        "keywords": ["view modes", "display modes", "entity display", "content display", "teaser", "full content", "display settings"],
        "synonyms": ["display modes", "view modes configuration", "content display settings"],
        "permissions": ["administer display modes"]
    },
    {
        "title": "Entity Form Modes",
        "path": "/admin/structure/display-modes/form",
        "module": "field_ui",
        "description": "Create and manage entity form modes. Configure different form layouts for content editing in different contexts.",
        "keywords": ["form modes", "edit forms", "entity forms", "form display", "form configuration", "edit settings"],
        "synonyms": ["edit forms", "form configuration", "form layouts"],
        "permissions": ["administer display modes"]
    },
    {
        "title": "Color Module",
        "path": "/admin/appearance/settings",
        "module": "color",
        "description": "Change the color scheme of compatible themes. Customize colors for site branding without coding.",
        "keywords": ["color", "colors", "color scheme", "theme colors", "customize colors", "branding colors", "color settings"],
        "synonyms": ["theme colors", "color customization", "branding"],
        "permissions": ["administer themes"]
    },
    {
        "title": "Statistics Settings",
        "path": "/admin/config/system/statistics",
        "module": "statistics",
        "description": "Configure content view counter settings. Track how many times content has been viewed.",
        "keywords": ["statistics", "view counter", "page views", "content views", "hit counter", "view statistics", "popular content"],
        "synonyms": ["view counter", "page statistics", "content views"],
        "permissions": ["administer statistics"]
    },
    {
        "title": "Tracker",
        "path": "/admin/content/tracker",
        "module": "tracker",
        "description": "View recent posts and updates across the site. Track new and updated content.",
        "keywords": ["tracker", "recent posts", "recent content", "new content", "content tracker", "activity", "recent updates"],
        "synonyms": ["recent posts", "content activity", "new content"],
        "permissions": ["access content"]
    },
    {
        "title": "Content Lock",
        "path": "/admin/config/content/content_lock",
        "module": "content_lock",
        "description": "Configure content locking settings to prevent concurrent editing. Set lock timeouts and override permissions.",
        "keywords": ["content lock", "lock", "concurrent editing", "edit lock", "prevent editing", "lock settings", "editing protection"],
        "synonyms": ["edit lock", "content protection", "concurrent editing prevention"],
        "permissions": ["administer content lock"]
    },
    {
        "title": "Menu Link Attributes",
        "path": "/admin/structure/menu/settings",
        "module": "menu_link_attributes",
        "description": "Configure custom attributes for menu links. Add CSS classes, IDs, and other HTML attributes to menu items.",
        "keywords": ["menu attributes", "menu link", "menu settings", "css classes", "menu classes", "menu customization"],
        "synonyms": ["menu customization", "menu link settings", "menu styling"],
        "permissions": ["administer menu"]
    },
    {
        "title": "Taxonomy Manager",
        "path": "/admin/structure/taxonomy_manager",
        "module": "taxonomy_manager",
        "description": "Manage taxonomy terms in a hierarchical view. Bulk edit, move, and organize taxonomy terms.",
        "keywords": ["taxonomy manager", "taxonomy", "terms", "categories", "tags", "vocabulary manager", "term hierarchy"],
        "synonyms": ["term manager", "category management", "tag management"],
        "permissions": ["administer taxonomy"]
    },
    {
        "title": "IMCE File Manager",
        "path": "/admin/config/media/imce",
        "module": "imce",
        "description": "Configure IMCE file manager settings. Enable file browsing and image uploading for editors.",
        "keywords": ["imce", "file manager", "file browser", "image upload", "media browser", "file upload", "file explorer"],
        "synonyms": ["file browser", "file manager settings", "media manager"],
        "permissions": ["administer imce"]
    },
    {
        "title": "CKEditor Settings",
        "path": "/admin/config/content/ckeditor",
        "module": "ckeditor",
        "description": "Configure CKEditor WYSIWYG editor settings. Customize toolbar, plugins, and text format integration.",
        "keywords": ["ckeditor", "editor", "wysiwyg", "rich text editor", "editor settings", "text editor", "toolbar"],
        "synonyms": ["text editor", "wysiwyg editor", "rich text editor settings"],
        "permissions": ["administer filters"]
    },
    {
        "title": "Text Formats and Editors",
        "path": "/admin/config/content/formats",
        "module": "filter",
        "description": "Configure text formats and their allowed HTML tags. Set up input formats for different user roles.",
        "keywords": ["text formats", "input formats", "filters", "allowed tags", "text filter", "input filter", "html filter"],
        "synonyms": ["input formats", "text filters", "content filters"],
        "permissions": ["administer filters"]
    },
    {
        "title": "Views UI",
        "path": "/admin/structure/views/settings",
        "module": "views_ui",
        "description": "Configure Views UI settings. Set default values for view creation and advanced settings.",
        "keywords": ["views ui", "views settings", "view configuration", "views defaults", "query settings"],
        "synonyms": ["views configuration", "views defaults", "query builder settings"],
        "permissions": ["administer views"]
    },
    {
        "title": "Rules Settings",
        "path": "/admin/config/workflow/rules",
        "module": "rules",
        "description": "Create and manage rules for automated actions based on site events. Configure triggers and conditions.",
        "keywords": ["rules", "automation", "conditions", "actions", "triggers", "event-based", "workflow automation"],
        "synonyms": ["automation rules", "event automation", "workflow triggers"],
        "permissions": ["administer rules"]
    },
    {
        "title": "Features",
        "path": "/admin/structure/features",
        "module": "features",
        "description": "Manage configuration features for deployment. Bundle configuration into features for export and reuse.",
        "keywords": ["features", "configuration bundle", "export configuration", "deployment", "feature export", "config package"],
        "synonyms": ["configuration bundles", "deployment features", "config packages"],
        "permissions": ["administer features"]
    },
    {
        "title": "Configuration Manager",
        "path": "/admin/config/development/configuration/config_mapper",
        "module": "config",
        "description": "View and manage configuration mappings. Understand configuration dependencies and structure.",
        "keywords": ["configuration manager", "config mapper", "configuration mapping", "config dependencies", "config structure"],
        "synonyms": ["config management", "configuration mapping", "config structure"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Environment Indicator",
        "path": "/admin/config/development/environment-indicator",
        "module": "environment_indicator",
        "description": "Configure environment indicator settings. Visual color-coded indicator showing current environment (dev, staging, prod).",
        "keywords": ["environment indicator", "environment", "dev staging prod", "color indicator", "environment switcher", "toolbar color"],
        "synonyms": ["environment settings", "environment visual", "environment marker"],
        "permissions": ["administer environment indicator"]
    },
    {
        "title": "Admin Toolbar",
        "path": "/admin/config/user-interface/admin-toolbar",
        "module": "admin_toolbar",
        "description": "Configure admin toolbar settings. Enhance the admin menu with dropdown menus and quick access links.",
        "keywords": ["admin toolbar", "toolbar", "admin menu", "dropdown menu", "quick access", "admin navigation"],
        "synonyms": ["toolbar settings", "admin menu settings", "admin navigation"],
        "permissions": ["administer toolbar"]
    },
    {
        "title": "Token Settings",
        "path": "/admin/help/token",
        "module": "token",
        "description": "View available tokens for use in fields, paths, and configuration. Browse token types and replacement patterns.",
        "keywords": ["tokens", "replacement patterns", "variables", "placeholders", "token list", "dynamic values", "token browser"],
        "synonyms": ["replacement patterns", "placeholders", "dynamic variables"],
        "permissions": ["administer tokens"]
    },
    {
        "title": "Menu Admin Per Menu",
        "path": "/admin/structure/menu/manage/main",
        "module": "menu_admin_per_menu",
        "description": "Configure per-menu administration permissions. Control which roles can edit specific menus.",
        "keywords": ["menu permissions", "menu access", "menu administration", "per-menu permissions", "menu roles"],
        "synonyms": ["menu access control", "menu permissions", "menu administration rights"],
        "permissions": ["administer menu"]
    },
    {
        "title": "Flood Control",
        "path": "/admin/config/system/flood",
        "module": "flood_control",
        "description": "Configure flood control settings to prevent abuse. Set limits on login attempts and form submissions.",
        "keywords": ["flood control", "rate limiting", "throttle", "login attempts", "abuse prevention", "security", "spam prevention"],
        "synonyms": ["rate limiting", "throttle settings", "abuse prevention"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Internal Page Cache",
        "path": "/admin/config/development/performance",
        "module": "page_cache",
        "description": "Configure internal page caching for anonymous users. Set cache expiration and bypass conditions.",
        "keywords": ["page cache", "internal cache", "anonymous cache", "caching", "cache settings", "page caching", "performance cache"],
        "synonyms": ["anonymous cache", "page caching", "performance caching"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "Dynamic Page Cache Settings",
        "path": "/admin/config/development/dynamic-page-cache",
        "module": "dynamic_page_cache",
        "description": "Configure dynamic page caching for authenticated users. Cache personalized content for faster page loads.",
        "keywords": ["dynamic page cache", "dynamic cache", "authenticated cache", "personalized cache", "page caching", "performance"],
        "synonyms": ["dynamic caching", "personalized cache", "authenticated user cache"],
        "permissions": ["administer site configuration"]
    },
    {
        "title": "BigPipe Configuration",
        "path": "/admin/config/development/bigpipe",
        "module": "bigpipe",
        "description": "Configure BigPipe for progressive page loading. Stream page content for faster perceived performance.",
        "keywords": ["bigpipe", "progressive loading", "streaming", "performance", "page streaming", "lazy loading", "fast loading"],
        "synonyms": ["progressive loading", "page streaming", "fast page load"],
        "permissions": ["administer site configuration"]
    },
]


def load_existing_data() -> list[dict[str, Any]]:
    existing_path = Path(__file__).parent / "config_nav" / "assets" / "config_data.json"
    if existing_path.exists():
        with existing_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def generate_keywords_from_title(title: str, description: str) -> list[str]:
    words = re.findall(r"\b\w{4,}\b", f"{title} {description}".lower())
    common_words = {"with", "from", "this", "that", "have", "been", "will", "their", "would", "could", "should", "when", "where", "which", "while", "about", "after", "before", "between", "under", "again", "further", "then", "once", "here", "there", "other", "more", "some", "such", "only", "also", "than", "most", "must", "over", "into", "most", "very", "just", "back", "much", "config", "configure", "configuration", "settings", "setting", "admin", "administer", "administration"}
    keywords = []
    for word in words:
        if word not in common_words and len(word) >= 4:
            keywords.append(word)
    return list(dict.fromkeys(keywords))[:8]


def generate_synonyms(title: str) -> list[str]:
    synonyms_map = {
        "settings": ["configuration", "options", "preferences"],
        "configuration": ["settings", "options", "setup"],
        "management": ["administration", "control", "handling"],
        "list": ["overview", "index", "directory"],
        "overview": ["list", "summary", "dashboard"],
        "create": ["add", "new", "build"],
        "edit": ["modify", "change", "update"],
        "delete": ["remove", "erase", "clear"],
    }
    synonyms = []
    title_lower = title.lower()
    for key, values in synonyms_map.items():
        if key in title_lower:
            synonyms.extend(values)
    return synonyms[:4]


def main():
    print("Loading existing config_data.json...")
    existing_data = load_existing_data()
    existing_paths = {item["path"] for item in existing_data}
    print(f"Found {len(existing_data)} existing entries")

    print(f"\nAdding {len(KNOWN_CONFIG_PAGES)} predefined config pages...")
    new_entries = []
    added_count = 0
    
    for page in KNOWN_CONFIG_PAGES:
        if page["path"] not in existing_paths:
            if "keywords" not in page or not page["keywords"]:
                page["keywords"] = generate_keywords_from_title(page["title"], page.get("description", ""))
            if "synonyms" not in page or not page["synonyms"]:
                page["synonyms"] = generate_synonyms(page["title"])
            new_entries.append(page)
            existing_paths.add(page["path"])
            added_count += 1
    
    print(f"Added {added_count} new entries from predefined list")

    all_data = existing_data + new_entries
    all_data.sort(key=lambda x: x["title"].lower())

    print(f"\nTotal entries: {len(all_data)}")
    print(f"Writing to {OUTPUT_PATH}...")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Created {OUTPUT_PATH}")
    print(f"Original: {len(existing_data)} entries")
    print(f"Added: {added_count} entries")
    print(f"Total: {len(all_data)} entries")


if __name__ == "__main__":
    main()