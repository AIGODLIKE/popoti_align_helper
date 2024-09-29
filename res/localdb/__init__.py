import json
import os
import re

import bpy

from .helper import TranslationHelper

dir_name = os.path.dirname(__file__)
help_classes = []

def get_language_list() -> list:
    """
    Traceback (most recent call last):
  File "<blender_console>", line 1, in <module>
TypeError: bpy_struct: item.attr = val: enum "a" not found in ('DEFAULT', 'en_US', 'es', 'ja_JP', 'sk_SK', 'vi_VN', 'zh_HANS', 'ar_EG', 'de_DE', 'fr_FR', 'it_IT', 'ko_KR', 'pt_BR', 'pt_PT', 'ru_RU', 'uk_UA', 'zh_TW', 'ab', 'ca_AD', 'cs_CZ', 'eo', 'eu_EU', 'fa_IR', 'ha', 'he_IL', 'hi_IN', 'hr_HR', 'hu_HU', 'id_ID', 'ky_KG', 'nl_NL', 'pl_PL', 'sr_RS', 'sr_RS@latin', 'sv_SE', 'th_TH', 'tr_TR')
    """
    try:
        bpy.context.preferences.view.language = ""
    except TypeError as e:
        matches = re.findall(r'\(([^()]*)\)', e.args[-1])
        text = f"({matches[-1]})"
        return eval(text)


all_language = get_language_list()
language = bpy.context.preferences.view.language
if language not in all_language:
    if language == "zh_CN":
        language = "zh_HANS"
    elif language == "zh_HANS":
        language = "zh_CN"

for file in os.listdir(dir_name):
    if not file.endswith('.json'):
        continue
    with open(os.path.join(dir_name, file), 'r', encoding='utf-8') as f:
        d = json.load(f)
        help_cls = TranslationHelper('popoti_align_helper_' + file, d, lang=language)
        help_classes.append(help_cls)
        zh_cn = d


def register():
    for cls in help_classes:
        cls.register()


def unregister():
    for cls in help_classes:
        cls.unregister()
