import re
import pandas as pd
from typing import List, Dict, Any, Tuple


def parse_text_dictionary(text: str) -> pd.DataFrame:
    def _split_def_ids(rest: str) -> Tuple[str, str]:
        rest = rest.strip()
        m = re.search(r"^(.*?)(\d[\d\s,;]*)$", rest)
        if m:
            candidate_def = m.group(1).rstrip(",; -")
            candidate_ids = m.group(2).strip()
            tokens = [t for t in re.split(r"[;,\s]+", candidate_ids) if t.strip()]
            digit_tokens = [t for t in tokens if t.isdigit()]
            if tokens and digit_tokens and len(digit_tokens) / len(tokens) >= 0.6:
                return candidate_def.strip(), candidate_ids.strip()
        candidates = ["|", "=>", " - ", " : ", ":", ";"]
        for sep in candidates:
            if sep in rest:
                left, right = rest.rsplit(sep, 1)
                if any(ch.isdigit() for ch in right):
                    return left.strip(), right.strip()
        return rest.strip(), ""

    def _lenient_parse(text: str) -> pd.DataFrame:
        rows: List[Dict[str, Any]] = []
        for raw in text.splitlines():
            if not raw or not raw.strip():
                continue
            line = raw.replace('\u00A0', ' ').replace('，', ',').replace('\t', ' ').strip()
            m = re.match(r"^\s*(\d+)\s+[\-:\|]?\s*(.*)$", line)
            if m:
                code = m.group(1)
                rest = m.group(2).strip()
            else:
                parts = re.split(r"\t|\s{2,}|\s-\s|\s\|\s", raw)
                if parts and re.match(r"^\d+$", parts[0].strip()):
                    code = parts[0].strip()
                    rest = parts[1].strip() if len(parts) > 1 else ''
                else:
                    continue
            ids = []
            ids_candidate = ''
            if '\t' in raw:
                tail = raw.split('\t')[-1]
                if re.search(r'\d', tail):
                    ids_candidate = tail
            if not ids_candidate:
                m2 = re.search(r'([0-9][0-9,;\s]*)$', rest)
                if m2:
                    ids_candidate = m2.group(1).strip()
                    rest = rest[:m2.start()].strip()
            if ids_candidate:
                tokens = re.split(r'[;,\s]+', ids_candidate)
                ids = []
                for tok in (t.strip() for t in tokens):
                    if tok.isdigit():
                        try:
                            ids.append(int(tok))
                        except Exception:
                            ids.append(tok)
            rows.append({'code': code, 'definition': rest, 'ids': ids})
        return pd.DataFrame(rows)

    try:
        lenient_out = _lenient_parse(text)
        if not lenient_out.empty:
            return lenient_out
    except Exception:
        pass

    lines = [l.rstrip() for l in text.split("\n") if l.strip()]
    rows: List[Dict[str, Any]] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^\s*(\d+)\s*(.*)$", line)
        if not m:
            continue
        code = m.group(1)
        rest = m.group(2).strip()
        rest = re.sub(r"^[\-\|:,;>]+", "", rest).strip()
        definition, ids_str = _split_def_ids(rest)
        ids: List[str] = []
        if ids_str:
            for token in re.split(r"[;,\s]+", ids_str):
                tok = token.strip()
                if tok.isdigit():
                    try:
                        ids.append(int(tok))
                    except Exception:
                        ids.append(tok)
        rows.append({"code": code, "definition": definition, "ids": ids})

    out = pd.DataFrame(rows)
    if out.empty:
        try:
            out = _lenient_parse(text)
        except Exception:
            out = pd.DataFrame(rows)
    return out


if __name__ == '__main__':
    # Paste the user's dictionary text here
    text = '''1	Indisponibilité totale du réseau	1, 27, 37, 296, 306, 384, 414, 444, 484, 493, 544, 599, 644, 844, 848, 899, 900, 1040, 1043, 1199
2	Réseau instable / coupures fréquentes	6, 10, 30, 59, 64, 104, 115, 129, 149, 153, 189, 221, 237, 245, 274, 287, 322, 332, 342, 361, 380, 382, 395, 419, 450, 452, 503, 511, 530, 564, 571, 576, 580, 584, 604, 613, 626, 628, 635, 653, 657, 666, 685, 704, 726, 730, 744, 760, 761, 767, 772, 780, 783, 784, 786, 789, 796, 798, 804, 808, 815, 819, 820, 821, 832, 834, 837, 842, 843, 844, 848, 852, 853, 855, 859, 860, 867, 869, 878, 884, 887, 894, 897, 899, 900, 902, 903, 904, 907, 914, 918, 919, 930, 936, 940, 949, 951, 954, 956, 957, 962, 963, 964, 966, 968, 969, 986, 992, 1000, 1019, 1021, 1029, 1034, 1035, 1037, 1038, 1040, 1042, 1043, 1045, 1046, 1047, 1056, 1060, 1062, 1072, 1075, 1078, 1084, 1086, 1087, 1088, 1089, 1096, 1100, 1103, 1114, 1115, 1116, 1124, 1133, 1153, 1155, 1156, 1157, 1158, 1160, 1162, 1163, 1166, 1170, 1173, 1174, 1176, 1179, 1181, 1189, 1191, 1194, 1195, 1196, 1199, 1202, 1203, 1206, 1209, 1212, 1213, 1215, 1221, 1224, 1229, 1231, 1233, 1236, 1242, 1244, 1246, 1273, 1278, 1279, 1280, 1282, 1290, 1291, 1298, 1301, 1305, 1313, 1314, 1316, 1320, 1323, 1325, 1334, 1336, 1337, 1343, 1346, 1351, 1356, 1358, 1363, 1365, 1371, 1375, 1377, 1378, 1381, 1384, 1386, 1387
3	Mauvaise couverture / manque d’antennes	56, 138, 153, 385, 531, 1029, 1088, 1153, 1173, 1343, 1401
4	Mauvaise qualité de communication (bruit, fluidité)	16, 60, 73, 88, 141, 203, 207, 236, 245, 267, 309, 319, 324, 333, 346, 354, 374, 380, 385, 386, 395, 407, 419, 427, 438, 446, 450, 451, 452, 453, 456, 461, 472, 484, 486, 505, 507, 508, 524, 530, 539, 540, 549, 550, 562, 564, 571, 576, 577, 580, 583, 584, 588, 606, 607, 613, 617, 618, 626, 628, 631, 635, 638, 653, 657, 658, 666, 669, 685, 686, 689, 704, 726, 727, 730, 735, 736, 744, 750, 751, 754, 760, 761, 767, 768, 769, 770, 772, 780, 783, 784, 786, 789, 796, 798, 804, 808, 815, 817, 819, 820, 821, 832, 834, 837, 842, 843, 844, 848, 852, 853, 855, 859, 860, 867, 869, 878, 884, 887, 894, 897, 899, 900, 902, 903, 904, 907, 914, 918, 919, 930, 936, 940, 949, 951, 954, 956, 957, 962, 963, 964, 966, 968, 969, 986, 992, 1000, 1019, 1021, 1029, 1034, 1035, 1037, 1038, 1040, 1042, 1043, 1045, 1046, 1047, 1056, 1060, 1062, 1072, 1075, 1078, 1084, 1086, 1087, 1088, 1089, 1096, 1100, 1103, 1114, 1115, 1116, 1124, 1133, 1153, 1155, 1156, 1157, 1158, 1160, 1162, 1163, 1166, 1170, 1173, 1174, 1176, 1179, 1181, 1189, 1191, 1194, 1195, 1196, 1199, 1202, 1203, 1206, 1209, 1212, 1213, 1215, 1221, 1224, 1229, 1231, 1233, 1236, 1242, 1244, 1246, 1273, 1278, 1279, 1280, 1282, 1290, 1291, 1298, 1301, 1305, 1313, 1314, 1316, 1320, 1323, 1325, 1334, 1336, 1337, 1343, 1346, 1351, 1356, 1358, 1363, 1365, 1371, 1375, 1377, 1378, 1381, 1384, 1386, 1387
5	Faible vitesse Internet / lenteur	12, 45, 99, 120, 221, 245, 380, 503, 530, 564, 613, 628, 653, 666, 704, 744, 760, 772, 780, 804, 808, 819, 832, 844, 852, 860, 887, 897, 902, 1040, 1043, 1056, 1062, 1088, 1153, 1173, 1343, 1365
6	Problèmes techniques liés à l’équipement	22, 58, 111, 134, 190, 245, 287, 324, 361, 386, 395, 407, 450, 452, 503, 511, 540, 549, 576, 584, 613, 626, 635, 653, 666, 685, 704, 726, 744, 760, 767, 772, 780, 804, 808, 832, 844, 848, 852, 860, 867, 878, 894, 900, 902, 936, 1019, 1029, 1034, 1040, 1043, 1088, 1153, 1173, 1343
7	Problèmes de facturation / paiement / abonnement	5, 31, 76, 110, 203, 221, 245, 287, 380, 503, 511, 564, 576, 604, 613, 653, 666, 685, 704, 726, 744, 760, 772, 780, 804, 808, 832, 844, 848, 860, 867, 878, 894, 900, 902, 936, 1019, 1029, 1040, 1043, 1088, 1153, 1173
8	Impact sur usage personnel ou professionnel	8, 40, 67, 95, 131, 203, 221, 245, 287, 380, 503, 511, 564, 576, 604, 613, 653, 666, 704, 726, 744, 760, 772, 780, 804, 808, 832, 844, 848, 860, 867, 878, 894, 900, 902, 936, 1019, 1029, 1040, 1043, 1088, 1153, 1173
9	Service client insatisfaisant	15, 44, 89, 150, 203, 221, 245, 287, 380, 503, 511, 564, 576, 604, 613, 653, 666, 704, 726, 744, 760, 772, 780, 804, 808, 832, 844, 848, 860, 867, 878, 894, 900, 902, 936, 1019, 1029, 1040, 1043, 1088, 1153, 1173
10	Autres plaintes / remarques diverses	3, 9, 28, 77, 101, 120, 138, 153, 190, 245, 324, 385, 531, 549, 608, 636, 704, 744, 760, 804, 844, 860, 888, 1029, 1088, 1153, 1173, 1343
'''

    out = parse_text_dictionary(text)
    total_ids = 0
    for v in out['ids']:
        try:
            total_ids += len(v)
        except Exception:
            total_ids += len(re.split(r"[;,\s]+", str(v)))
    print(f"Themes parsed: {len(out)}")
    print(f"Total IDs parsed (approx): {total_ids}")
    print(out.head(10))
