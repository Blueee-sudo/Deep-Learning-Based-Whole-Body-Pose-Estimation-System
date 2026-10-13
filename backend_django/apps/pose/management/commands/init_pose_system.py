import os

from django.core.management.base import BaseCommand

from apps.pose.auth_utils import hash_password
from apps.pose.models import Role, User


class Command(BaseCommand):
    help = "初始化角色与管理员账号"

    def handle(self, *args, **options):
        admin_role, _ = Role.objects.get_or_create(
            role_id=1,
            defaults={"role_name": "admin", "description": "管理员"},
        )
        user_role, _ = Role.objects.get_or_create(
            role_id=2,
            defaults={"role_name": "user", "description": "普通用户"},
        )
        if admin_role.role_name != "admin":
            admin_role.role_name = "admin"
            admin_role.save(update_fields=["role_name"])
        if user_role.role_name != "user":
            user_role.role_name = "user"
            user_role.save(update_fields=["role_name"])

        username = os.getenv("INIT_ADMIN_USERNAME", "admin")
        email = os.getenv("INIT_ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("INIT_ADMIN_PASSWORD", "Admin@123456")

        admin = User.objects.filter(username=username).first()
        if admin is None:
            admin = User.objects.create(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role=admin_role,
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f"已创建管理员账号: {username}"))
        else:
            changed = False
            if admin.role_id != 1:
                admin.role = admin_role
                changed = True
            if not admin.is_active:
                admin.is_active = True
                changed = True
            # If admin user already exists, still update password to match INIT_ADMIN_PASSWORD.
            # This keeps "admin / Admin@123456" working for demos and avoids stale credentials.
            new_hash = hash_password(password)
            if admin.password_hash != new_hash:
                admin.password_hash = new_hash
                changed = True
            if email and admin.email != email:
                admin.email = email
                changed = True
            if changed:
                admin.save(update_fields=["role", "is_active", "password_hash", "email"])
            self.stdout.write(self.style.WARNING(f"管理员账号已存在: {username}"))

        self.stdout.write(self.style.SUCCESS("初始化完成：role(admin/user) + admin 用户"))
