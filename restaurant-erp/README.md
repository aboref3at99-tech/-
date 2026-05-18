# Restaurant ERP Platform (Enterprise Starter)

هذا المشروع هو نقطة الانطلاق الاحترافية لبناء نظام إدارة مطاعم مكتبي (Desktop ERP) بأسلوب **Offline-First** مع مزامنة سحابية.

## المكدس التقني
- Desktop: Tauri + React + TypeScript
- API: NestJS + TypeScript
- Local DB: SQLite (SQLCipher لاحقًا)
- Cloud DB: PostgreSQL
- ORM: Prisma
- UI: Tailwind CSS

## التشغيل السريع
```bash
pnpm install
pnpm dev
```

## هيكلية المونوريبو
- `apps/desktop`: تطبيق سطح المكتب
- `apps/api`: واجهة API السحابية
- `apps/admin-web`: لوحة إدارة السحابة
- `packages/shared`: أنواع وواجهات مشتركة
- `packages/config`: إعدادات البيئة والأمن
- `docs`: وثائق معمارية وخطة التنفيذ

## الحالة الحالية
- تم تجهيز **الهيكل الأساسي للمشروع** (Phase 0 + بداية Phase 1).
- جاهز للانتقال إلى تنفيذ المصادقة والترخيص والمزامنة.
