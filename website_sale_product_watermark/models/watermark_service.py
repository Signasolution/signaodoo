# -*- coding: utf-8 -*-
"""Composition de filigranes (texte ou image) sur une image produit.

Ce module ne dépend que de Pillow (déjà une dépendance native d'Odoo) et ne
touche jamais à l'ORM : il peut être testé et réutilisé indépendamment,
aussi bien pour la prévisualisation que pour l'application réelle en lot.
"""

import base64
import io
import os

from PIL import Image, ImageDraw, ImageFont, ImageFile, ImageOps

# Odoo fige l'initialisation des plugins Pillow à un sous-ensemble minimal
# (odoo/tools/image.py : Image.preinit() puis Image._initialized = 2, soit
# BMP/GIF/JPEG/PPM/PNG uniquement) : le décodeur WebP n'est donc jamais
# enregistré dans les workers Odoo, même quand libwebp est disponible — or
# Odoo 18 stocke justement les images produits en WebP. L'import explicite
# du plugin l'enregistre immédiatement, indépendamment de ce gel.
try:
    from PIL import WebPImagePlugin  # noqa: F401
except ImportError:
    # Build Pillow sans support WebP : les images WebP resteront ignorées
    # (avec le diagnostic détaillé dans les logs), sans casser le module.
    pass

# Tolère les fichiers légèrement tronqués/imparfaits (cas fréquent avec des
# photos produits venant de sources diverses) plutôt que de faire échouer
# tout le traitement pour un octet manquant en fin de fichier.
ImageFile.LOAD_TRUNCATED_IMAGES = True

_SUPPORTED_WATERMARK_FORMATS = {'PNG', 'JPEG'}

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts')

FONT_FILES = {
    'dejavu_sans': 'DejaVuSans.ttf',
    'dejavu_sans_bold': 'DejaVuSans-Bold.ttf',
}

# Taille de rendu de base pour le texte : le calque est ensuite remis à
# l'échelle selon `resize_ratio`, donc seule la proportion (via la police
# choisie) compte, pas cette valeur absolue.
_TEXT_BASE_FONT_SIZE = 200
_TEXT_PADDING = 10

# Position -> fonction (largeur_zone, hauteur_zone, largeur_calque, hauteur_calque, marge) -> (x, y)
_POSITION_COORDS = {
    'top_left': lambda w, h, lw, lh, m: (m, m),
    'top_center': lambda w, h, lw, lh, m: ((w - lw) // 2, m),
    'top_right': lambda w, h, lw, lh, m: (w - lw - m, m),
    'middle_left': lambda w, h, lw, lh, m: (m, (h - lh) // 2),
    'center': lambda w, h, lw, lh, m: ((w - lw) // 2, (h - lh) // 2),
    'middle_right': lambda w, h, lw, lh, m: (w - lw - m, (h - lh) // 2),
    'bottom_left': lambda w, h, lw, lh, m: (m, h - lh - m),
    'bottom_center': lambda w, h, lw, lh, m: ((w - lw) // 2, h - lh - m),
    'bottom_right': lambda w, h, lw, lh, m: (w - lw - m, h - lh - m),
}


class WatermarkError(Exception):
    """Erreur métier de composition de filigrane (remontée telle quelle à l'UI)."""


def _resolve_font_path(font_family, custom_font_file=None):
    """Retourne un chemin de fichier .ttf utilisable par ImageFont.truetype.

    `custom_font_file` est le contenu binaire (déjà décodé, pas en base64)
    d'une police uploadée par l'utilisateur : dans ce cas on l'écrit dans un
    buffer mémoire, Pillow sait charger une police depuis un objet fichier.
    """
    if font_family == 'custom' and custom_font_file:
        return io.BytesIO(custom_font_file)
    filename = FONT_FILES.get(font_family, FONT_FILES['dejavu_sans'])
    return os.path.join(FONTS_DIR, filename)


def validate_watermark_image(image_bytes):
    """Vérifie que les octets fournis représentent une image PNG ou JPEG, et
    renvoie l'image chargée convertie en RGBA.

    Le PNG conserve sa transparence par pixel (RGBA d'origine). Le JPEG n'a
    pas de canal alpha : il devient une image RGBA entièrement opaque, sur
    laquelle le réglage global d'opacité du filigrane s'applique toujours,
    mais sans détourage (le fond de l'image JPEG sera visible).

    Lève WatermarkError si le fichier n'est ni un PNG ni un JPEG valide.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
    except Exception as exc:
        raise WatermarkError("Le fichier fourni n'est pas une image valide.") from exc
    if img.format not in _SUPPORTED_WATERMARK_FORMATS:
        raise WatermarkError(
            "Le filigrane image doit être au format PNG ou JPEG (format détecté : %s)." % (img.format or 'inconnu')
        )
    return img.convert('RGBA')


def build_layer(config):
    """Construit le calque de filigrane (image RGBA) à partir de la config.

    `config` est un dict avec les clés :
        watermark_type ('text' | 'image')
        text_content, font_family, custom_font_file (bytes|None), font_color
        watermark_image_bytes (bytes|None)

    Le calque retourné n'est PAS encore mis à l'échelle : `composite()`
    s'en charge relativement aux dimensions de l'image cible.
    """
    if config['watermark_type'] == 'image':
        if not config.get('watermark_image_bytes'):
            raise WatermarkError("Aucune image de filigrane configurée.")
        return validate_watermark_image(config['watermark_image_bytes'])

    text = (config.get('text_content') or '').strip()
    if not text:
        raise WatermarkError("Aucun texte de filigrane configuré.")

    font_path = _resolve_font_path(config.get('font_family'), config.get('custom_font_file'))
    font = ImageFont.truetype(font_path, _TEXT_BASE_FONT_SIZE)

    measure_img = Image.new('RGBA', (10, 10))
    bbox = ImageDraw.Draw(measure_img).textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    layer = Image.new('RGBA', (text_w + 2 * _TEXT_PADDING, text_h + 2 * _TEXT_PADDING), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(
        (_TEXT_PADDING - bbox[0], _TEXT_PADDING - bbox[1]),
        text,
        font=font,
        fill=_hex_to_rgba(config.get('font_color') or '#FFFFFF'),
    )
    return layer


def _hex_to_rgba(hex_color, alpha=255):
    hex_color = (hex_color or '#FFFFFF').lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, alpha)


def _apply_opacity(layer, opacity):
    opacity = max(0, min(255, int(opacity)))
    if opacity >= 255:
        return layer
    alpha = layer.getchannel('A').point(lambda a: a * opacity // 255)
    layer.putalpha(alpha)
    return layer


def _scale_layer(layer, target_w, resize_ratio):
    resize_ratio = max(0.01, min(1.0, float(resize_ratio or 0.25)))
    desired_w = max(1, int(target_w * resize_ratio))
    ratio = desired_w / layer.width
    desired_h = max(1, int(layer.height * ratio))
    return layer.resize((desired_w, desired_h), Image.LANCZOS)


def composite(base_bytes, layer, config):
    """Compose le calque de filigrane sur l'image de base et renvoie les
    octets de l'image résultante, dans le format d'origine de `base_bytes`
    (PNG conserve la transparence, les autres formats sont aplatis en RGB).
    """
    base = Image.open(io.BytesIO(base_bytes))
    original_format = base.format or 'PNG'
    base = ImageOps.exif_transpose(base)
    target_w, target_h = base.size

    working_layer = _scale_layer(layer, target_w, config.get('resize_ratio'))

    rotation = float(config.get('rotation') or 0)
    if rotation:
        working_layer = working_layer.rotate(rotation, expand=True, resample=Image.BICUBIC)

    working_layer = _apply_opacity(working_layer, config.get('opacity', 255))

    position = config.get('position') or 'center'
    margin = int(config.get('margin') or 0)
    coord_fn = _POSITION_COORDS.get(position, _POSITION_COORDS['center'])
    x, y = coord_fn(target_w, target_h, working_layer.width, working_layer.height, margin)
    # Le calque peut dépasser la zone si l'image cible est trop petite ;
    # on le rend visible au mieux plutôt que de planter.
    x = max(-working_layer.width + 1, min(x, target_w - 1))
    y = max(-working_layer.height + 1, min(y, target_h - 1))

    result = base.convert('RGBA')
    result.alpha_composite(working_layer, (x, y))

    output = io.BytesIO()
    if original_format == 'PNG':
        result.save(output, format='PNG')
    elif original_format == 'WEBP':
        # WebP supporte le canal alpha : on le conserve, comme pour le PNG.
        result.save(output, format='WEBP', quality=95)
    else:
        result = result.convert('RGB')
        result.save(output, format=original_format, quality=95)
    return output.getvalue()


_KNOWN_SIGNATURES = (
    (b'\x89PNG\r\n\x1a\n', "PNG"),
    (b'\xff\xd8\xff', "JPEG"),
    (b'GIF87a', "GIF"),
    (b'GIF89a', "GIF"),
    (b'BM', "BMP"),
)


_WEBP_VP8X_FLAGS = (
    (0x04, "ICC"),
    (0x08, "Alpha"),
    (0x10, "EXIF"),
    (0x20, "XMP"),
    (0x40, "Animation"),
)


def _describe_webp(data):
    """Diagnostic détaillé d'un fichier WebP que Pillow n'a pas su ouvrir :
    version de libwebp vue par Pillow, sous-format (simple/étendu) et
    tentative d'ouverture en forçant explicitement le plugin WEBP (le
    message d'erreur brut est parfois plus précis que le générique
    "cannot identify image file").
    """
    parts = []
    try:
        from PIL import features
        parts.append("Pillow features.version('webp') = %s" % features.version('webp'))
    except Exception as exc:
        parts.append("features.version('webp') a échoué : %s" % exc)

    chunk = data[12:16]
    if chunk == b'VP8X':
        flags = data[20] if len(data) > 20 else 0
        active = [name for bit, name in _WEBP_VP8X_FLAGS if flags & bit]
        parts.append("format WebP étendu (VP8X), options : %s" % (", ".join(active) or "aucune"))
    elif chunk in (b'VP8 ', b'VP8L'):
        parts.append("format WebP simple (%s)" % chunk.decode(errors='replace').strip())
    else:
        parts.append("chunk après RIFF/WEBP inattendu : %r" % chunk)

    try:
        Image.open(io.BytesIO(data), formats=['WEBP']).load()
        parts.append("réouverture forcée avec formats=['WEBP'] : SUCCÈS (étrange, revérifier)")
    except Exception as exc:
        parts.append("réouverture forcée avec formats=['WEBP'] : %s" % exc)

    return " | ".join(parts)


def _describe_bytes(data):
    """Décrit sommairement des octets illisibles par Pillow, pour aider au
    diagnostic dans les logs (WebP/HEIC ne sont pas des formats reconnus par
    tous les builds de Pillow, contrairement au JPEG/PNG).
    """
    if not data:
        return "0 octet (image vide)"
    header_hex = data[:16].hex()
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return "%d octets, format WebP (RIFF/WEBP) : %s" % (len(data), _describe_webp(data))
    if data[4:8] == b'ftyp':
        return "%d octets, conteneur ISOBMFF (HEIC/HEIF/AVIF probable) : non supporté par Pillow" % len(data)
    if data.lstrip()[:1] in (b'<',) and b'svg' in data[:200].lower():
        return "%d octets, semble être un SVG (non supporté par Pillow)" % len(data)
    for signature, name in _KNOWN_SIGNATURES:
        if data.startswith(signature):
            return "%d octets, en-tête %s reconnu mais fichier corrompu/tronqué" % (len(data), name)
    return "%d octets, en-tête inconnu (hex: %s)" % (len(data), header_hex)


def apply_watermark_to_image(image_b64, config):
    """Point d'entrée pratique : image source encodée en base64 (tel que
    stocké dans un champ Binary Odoo) -> image filigranée encodée en base64.

    Toute erreur de décodage/lecture Pillow (fichier corrompu, format non
    supporté...) est convertie en WatermarkError afin que l'appelant (batch
    ou aperçu) puisse l'ignorer proprement au lieu de faire planter tout le
    traitement.
    """
    if not image_b64:
        return image_b64
    base_bytes = base64.b64decode(image_b64)
    try:
        layer = build_layer(config)
        result_bytes = composite(base_bytes, layer, config)
    except WatermarkError:
        raise
    except Exception as exc:
        raise WatermarkError(
            "Image illisible ou format non pris en charge (%s) - %s" % (exc, _describe_bytes(base_bytes))
        ) from exc
    return base64.b64encode(result_bytes)
