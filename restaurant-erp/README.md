# Restaurant ERP Platform (Enterprise Foundation)

منصة احترافية لبناء نظام إدارة مطاعم مكتبي **Offline-First** مع مزامنة سحابية آمنة.

## المعمارية الحالية
- `apps/desktop`: تطبيق سطح المكتب (الواجهة التشغيلية للفروع)
- `apps/api`: خدمة API السحابية (المصادقة، الصلاحيات، المزامنة، التراخيص)
- `apps/admin-web`: لوحة الإدارة المركزية (SaaS admin)
- `packages/shared`: العقود والأنواع المشتركة
- `packages/config`: إعدادات الأمان والبيئة

## تشغيل سريع للاختبار (بدون تثبيت حزم)
```bash
# تشغيل API تجريبي
node apps/api/dev-server.mjs

# في نافذة ثانية: اختبار الصحة
curl http://localhost:4000/health

# تشغيل launchers تجريبية للـ desktop/admin
node apps/desktop/dev-launcher.mjs
node apps/admin-web/dev-launcher.mjs
```

## تشغيل المشروع الكامل (عند توفر الشبكة)
```bash
pnpm install
pnpm dev
```

## فحوصات الجودة
```bash
pnpm typecheck
pnpm build
```
