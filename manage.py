#!/usr/bin/env python

import sys

sys.path.append("..")

from django.conf import settings

settings.configure(
    ROOT_URLCONF="spice_orgs.tests.urls",
    SECRET_KEY="TEST_KEY",
    INSTALLED_APPS=(
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "spice_orgs",
    ),
    MIDDLEWARE=(
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ),
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "USER": "",
            "PASSWORD": "",
            "HOST": "",
            "PORT": "",
        }
    },
)

import django

django.setup()

from django.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
