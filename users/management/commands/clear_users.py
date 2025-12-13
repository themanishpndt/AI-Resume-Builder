import os
import shutil
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Delete all user accounts and optionally remove user media files."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Proceed without interactive confirmation",
        )
        parser.add_argument(
            "--remove-media",
            action="store_true",
            help=("Remove media subfolders (profile_photos, resumes, project_thumbnails) "
                  "under MEDIA_ROOT after deleting users"),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without making changes",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        qs = User.objects.all()
        total = qs.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No user accounts found."))
            return

        self.stdout.write(self.style.WARNING(f"About to delete {total} user account(s)."))

        if options.get("dry_run"):
            self.stdout.write(self.style.NOTICE if hasattr(self.style, 'NOTICE') else self.style.WARNING(
                "Dry run: no changes will be made."))

        if not options.get("yes") and not options.get("dry_run"):
            confirm = input("Type DELETE to confirm deleting ALL user accounts: ")
            if confirm != "DELETE":
                self.stdout.write(self.style.ERROR("Aborted — confirmation not provided."))
                return

        # Delete users (iterate to call instance.delete() so signals and custom delete are honored)
        if options.get("dry_run"):
            self.stdout.write(self.style.WARNING(f"Dry run: would delete {total} user(s)."))
        else:
            with transaction.atomic():
                deleted = 0
                for user in qs:
                    # Call instance.delete() to ensure post_delete signals run and any overridden
                    # delete() logic executes.
                    user.delete()
                    deleted += 1
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} user(s)."))

        # Optionally remove media folders
        if options.get("remove_media"):
            media_root = getattr(settings, "MEDIA_ROOT", None)
            if not media_root:
                self.stdout.write(self.style.ERROR("MEDIA_ROOT is not configured; cannot remove media files."))
                return

            folders = ["profile_photos", "resumes", "project_thumbnails"]
            for folder in folders:
                path = os.path.join(media_root, folder)
                if os.path.exists(path):
                    if options.get("dry_run"):
                        self.stdout.write(self.style.WARNING(f"Dry run: would remove {path}"))
                    else:
                        try:
                            # Remove all contents safely
                            shutil.rmtree(path)
                            # Recreate empty directory so app references don't break later
                            os.makedirs(path, exist_ok=True)
                            self.stdout.write(self.style.SUCCESS(f"Removed files in {path}"))
                        except Exception as exc:
                            self.stdout.write(self.style.ERROR(f"Failed to remove {path}: {exc}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Path not found: {path}"))

        self.stdout.write(self.style.SUCCESS("Operation completed."))
