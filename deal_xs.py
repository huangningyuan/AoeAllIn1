from constants import GAME_XS_PATH

import utils
import os
import re
import json


_XS_BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xs_baselines.json")

_FUNCTIONS_TO_WATCH = [
    "EffectFunction3",
    "EffectFunction13",
    "EffectFunction14",
    "EffectFunction15",
    "EffectFunction16",
]


def _load_xs_baselines() -> dict:
    if not os.path.exists(_XS_BASELINE_PATH):
        return {}
    try:
        with open(_XS_BASELINE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_xs_baselines(data: dict) -> None:
    with open(_XS_BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _extract_function(content: str, func_name: str) -> str | None:
    pattern = rf'void\s+{re.escape(func_name)}\([^)]*\)\s*\{{'
    match = re.search(pattern, content)
    if not match:
        return None
    start = match.start()
    depth = 0
    pos = match.end() - 1
    while pos < len(content):
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
            if depth == 0:
                return content[start:pos + 1]
        pos += 1
    return None


def _diff_text(old: str, new: str) -> list:
    diffs = []
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    max_len = max(len(old_lines), len(new_lines))
    for i in range(max_len):
        o = old_lines[i] if i < len(old_lines) else None
        n = new_lines[i] if i < len(new_lines) else None
        if o is None:
            diffs.append(f"  + NEW only: {n}")
        elif n is None:
            diffs.append(f"  - OLD only: {o}")
        elif o != n:
            diffs.append(f"  @@ line {i+1}:")
            diffs.append(f"    - {o}")
            diffs.append(f"    + {n}")
    return diffs


def _check_official_changes(original_content: str) -> None:
    baselines = _load_xs_baselines()
    updated = False

    for func_name in _FUNCTIONS_TO_WATCH:
        current_func = _extract_function(original_content, func_name)
        key = func_name

        if key not in baselines:
            if current_func is None:
                print(f"[XSTracker] {func_name}: not present in official Effects.xs (recorded as absent)")
            else:
                print(f"[XSTracker] NEW {func_name}: found ({len(current_func.splitlines())} lines, baseline recorded)")
            baselines[key] = current_func
            updated = True
        else:
            baseline = baselines[key]
            if baseline is None and current_func is not None:
                print(f"[XSTracker] CHANGE DETECTED {func_name}: was ABSENT, now PRESENT ({len(current_func.splitlines())} lines)")
                baselines[key] = current_func
                updated = True
            elif baseline is not None and current_func is None:
                print(f"[XSTracker] CHANGE DETECTED {func_name}: was PRESENT ({len(baseline.splitlines())} lines), now ABSENT")
                baselines[key] = None
                updated = True
            elif baseline is not None and current_func is not None and baseline != current_func:
                diffs = _diff_text(baseline, current_func)
                print(f"[XSTracker] CHANGE DETECTED {func_name}:")
                for line in diffs:
                    print(line)
                print(f"  (old: {len(baseline.splitlines())} lines, new: {len(current_func.splitlines())} lines)")
                baselines[key] = current_func
                updated = True

    if updated:
        _save_xs_baselines(baselines)


def _replace_effect_function14(content: str) -> str:
    old_block = (
        r'(xsTaskAmount\(cTaskAttrWorkValue1, 0\.01\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrProductivityResource, cAttributeGoldFarmingProductivity\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrResourceOut, cAttributeGold\);)\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrCombatLevelFlag, 1\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrSearchWaitTime, 3\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrAutoSearch, 1\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrEnableTargeting, 1\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrOwnerType, 5\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrGatherType, 1\);\s*\n'
        r'\s*\n'
        r'\s*xsTask\(FarmerMaleID, cTaskTypeGenerateResources, cFarmClass, playerId\);\s*\n'
        r'\s*xsTask\(FarmerFemaleID, cTaskTypeGenerateResources, cFarmClass, playerId\);'
    )
    new_block = (
        r'\1\n'
        r'\n'
        r'  xsTask(FarmerMaleID, cTaskTypeAdditionalResource, cFarmClass, playerId);\n'
        r'  xsTask(FarmerFemaleID, cTaskTypeAdditionalResource, cFarmClass, playerId);'
    )
    new_content, count = re.subn(old_block, new_block, content)
    if count == 0:
        print("[Effects.xs] EffectFunction14: old pattern not matched, official may have changed — manual review needed")
    else:
        print(f"[Effects.xs] EffectFunction14: rewritten to new-style")
    return new_content


def _replace_effect_function15(content: str) -> str:
    old_block = (
        r'(xsTaskAmount\(cTaskAttrWorkValue1, 0\.01\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrProductivityResource, cAttributeChoppingGoldProductivity\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrResourceOut, cAttributeGold\);)\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrCombatLevelFlag, 1\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrSearchWaitTime, 3\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrAutoSearch, 1\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrEnableTargeting, 1\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrOwnerType, 5\);\s*\n'
        r'\s*xsTaskAmount\(cTaskAttrGatherType, 1\);\s*\n'
        r'\s*\n'
        r'\s*xsTask\(LumberjackMaleID, cTaskTypeGenerateResources, cTreeClass, playerId\);\s*\n'
        r'\s*xsTask\(LumberjackFemaleID, cTaskTypeGenerateResources, cTreeClass, playerId\);'
    )
    new_block = (
        r'\1\n'
        r'\n'
        r'  xsTask(LumberjackMaleID, cTaskTypeAdditionalResource, cTreeClass, playerId);\n'
        r'  xsTask(LumberjackFemaleID, cTaskTypeAdditionalResource, cTreeClass, playerId);'
    )
    new_content, count = re.subn(old_block, new_block, content)
    if count == 0:
        print("[Effects.xs] EffectFunction15: old pattern not matched, official may have changed — manual review needed")
    else:
        print(f"[Effects.xs] EffectFunction15: rewritten to new-style")
    return new_content


def deal_xs():
    xs_path = GAME_XS_PATH
    mod_xs_path = os.path.join(utils.get_mod_path(), 'resources', '_common', 'xs')
    if not os.path.exists(mod_xs_path):
        os.makedirs(mod_xs_path, exist_ok=True)

    effects_xs_path = os.path.join(xs_path, 'Effects.xs')
    mod_effects_xs_path = os.path.join(mod_xs_path, 'Effects.xs')

    if os.path.exists(effects_xs_path):
        with open(effects_xs_path, 'r', encoding='utf-8') as f:
            effects_content = f.read()

        _check_official_changes(effects_content)

        modified_effects_content = effects_content
        modified_effects_content = _replace_effect_function14(modified_effects_content)
        modified_effects_content = _replace_effect_function15(modified_effects_content)

        with open(mod_effects_xs_path, 'w', encoding='utf-8') as f:
            f.write(modified_effects_content)

        print(f"Effects.xs modified and copied to mod directory: {mod_effects_xs_path}")
    else:
        print(f"Effects.xs not found at {effects_xs_path}")