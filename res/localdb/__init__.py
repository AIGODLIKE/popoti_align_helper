import ast
import re

import bpy

from . import zh_CN


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
        return ast.literal_eval(f"({matches[-1]})")


class TranslationHelper:
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        bpy.app.translations.register(self.name, self.translations_dict)

    def unregister(self):
        bpy.app.translations.unregister(self.name)


translate = None


def register():
    global translate

    language = "zh_CN"
    all_language = get_language_list()
    if language not in all_language:
        if language == "zh_CN":
            language = "zh_HANS"
        elif language == "zh_HANS":
            language = "zh_CN"
    translate = TranslationHelper(f"popoti_align_helper_{language}", zh_CN.data, lang=language)
    translate.register()


def unregister():
    global translate
    translate.unregister()
    translate = None
