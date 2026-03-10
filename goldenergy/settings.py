"""
Django settings for goldenergy project.
Configurado para Produção no Render.com (PostgreSQL e WhiteNoise).
"""

from pathlib import Path
import os
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Assume que o BASE_DIR é 'goldenergy' (pasta do projeto).
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# Chaves e Flags lidas do arquivo .env ou variáveis de ambiente
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Adiciona o hostname do Render dinamicamente
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

# Configurações de Hosts Permitidos
# Em desenvolvimento, o valor padrão é lido do .env.
# Em produção, o Render.com o injeta.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# Adiciona o domínio personalizado e o subdomínio www
ALLOWED_HOSTS.extend(['goldenergy.pro', 'www.goldenergy.pro'])

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    
# Se estiver em produção (não DEBUG) e não houver HOSTS definidos, 
# adicione o hostname do Render como fallback.
if not DEBUG and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    # WhiteNoise deve ser o primeiro app, exceto no Django > 4.1
    # Mantemos aqui para compatibilidade e boa prática geral.
    'whitenoise.runserver_nostatic', 
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Seus Apps
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise deve vir logo abaixo do SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'goldenergy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Assumindo que você tem uma pasta 'templates' na raiz do projeto
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'goldenergy.wsgi.application'


# 🚀 Configuração do Banco de Dados para Produção (Render/PostgreSQL)
# Se estiver em produção (não DEBUG) e a DATABASE_URL for fornecida, use PostgreSQL.
if not DEBUG and 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True 
        )
    }
    # Configura o Django para reconhecer a conexão SSL através do proxy do Render
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # Configuração local (desenvolvimento) usando SQLite
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR}/db.sqlite3'
        )
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'Africa/Luanda' # Mantido como solicitado

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Onde os arquivos estáticos serão coletados (produção)
STATICFILES_DIRS = [BASE_DIR / 'static'] # Seus diretórios estáticos locais (desenvolvimento)


# ======================================================================
# 🚀 Configuração de Armazenamento de Arquivos Estáticos (WhiteNoise)
# Usa o novo sistema STORAGES para WhiteNoise em Produção
# ======================================================================
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ======================================================================
# Configurações de Mídia (Media Files)
# Mantém o armazenamento LOCAL, mas requer atenção na produção
# ======================================================================
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# NOTA: Em produção no Render, arquivos de mídia não devem ser 
# armazenados localmente, pois o sistema de arquivos é temporário.
# Você deve configurar o AWS S3 ou similar para mídia em produção.
# ======================================================================


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# UKZ o modelo de usuário personalizado
AUTH_USER_MODEL = 'core.CustomUser' # Mantido, assumindo que 'core' contém este modelo

LOGIN_URL = 'login'

# Configuração de segurança adicional para produção (Recomendado)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000 # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    